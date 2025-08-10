# kura/polling/views.py
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Voter, Candidate, Vote, StudentID, Position
from django.contrib.auth.models import User
from collections import defaultdict
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required
from .serializers import VoterSignupSerializer, VoterSerializer, CandidateSerializer, VoteSerializer 

def landing_page(request):
    """
    Renders the landing page.
    """
    return render(request, 'landing_page.html')

# This view is for the front-end to render the voting page
@login_required
def voting_page(request):
    try:
        voter = request.user.voter
    except Voter.DoesNotExist:
        return render(request, 'error_page.html', {'message': 'Voter profile not found.'})

    if voter.is_voted:
        return render(request, 'voted_page.html')
    else:
        positions = Position.objects.prefetch_related('candidate_set').all().order_by('order')
        
        context = {
            'positions': positions,
            'user': request.user,
        }
        return render(request, 'voting_page.html', context)

@login_required
def cast_vote(request):
    if request.method == 'POST':
        voter = request.user.voter
        if voter.is_voted:
            return JsonResponse({'detail': 'You have already voted.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                for key, candidate_id in request.POST.items():
                    if key.startswith('position-'):
                        try:
                            candidate = Candidate.objects.get(id=candidate_id)
                            if not Vote.objects.filter(voter=voter, candidate__position=candidate.position).exists():
                                Vote.objects.create(voter=voter, candidate=candidate)
                                Candidate.objects.filter(id=candidate_id).update(votes=F('votes') + 1)
                        except Candidate.DoesNotExist:
                            return JsonResponse({'detail': 'Invalid candidate selection.'}, status=status.HTTP_400_BAD_REQUEST)
            
            voter.is_voted = True
            voter.save()
            
            # 💡 Log out the user after the vote is successfully cast
            logout(request)
            
            return JsonResponse({'detail': 'Vote cast successfully!'}, status=status.HTTP_200_OK)
    
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return redirect('voting_page')

class VoterSignupView(APIView):
    permission_classes = [AllowAny]
    # ... (rest of the VoterSignupView code)
    def post(self, request):
        serializer = VoterSignupSerializer(data=request.data)
        if serializer.is_valid():
            student_id = serializer.validated_data['student_id']
            email = serializer.validated_data['email']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            
            if User.objects.filter(username=student_id).exists():
                return Response({'detail': 'An account with this student ID already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                
            user = User.objects.create_user(
                username=student_id,
                email=email,
                password=serializer.validated_data['password'],
                first_name=first_name,
                last_name=last_name
            )

            Voter.objects.create(
                user=user,
                student_id=student_id,
                registration_status='Verified'
            )
            
            StudentID.objects.create(
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                email=email
            )
            
            return Response({'detail': 'Account created successfully. You can now log in.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VoterLoginView(APIView):
    permission_classes = [AllowAny]
    
    # This GET method is for displaying the login form
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('voting_page')
        return render(request, 'login.html')
    
    # This POST method is for processing the form submission
    def post(self, request):
        student_id = request.data.get('student_id')
        password = request.data.get('password')
        
        user = authenticate(request, username=student_id, password=password)
        
        if user is not None:
            try:
                # ... (your existing validation logic)
                StudentID.objects.get(
                    student_id=student_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email
                )
            except StudentID.DoesNotExist:
                logout(request)
                return Response({"detail": "Invalid student ID or credentials. Please contact support."}, status=status.HTTP_400_BAD_REQUEST)
            
            login(request, user)
            return redirect('voting_page')
        else:
            return Response({"detail": "Invalid Student ID or password."}, status=status.HTTP_400_BAD_REQUEST)

class VoterLogoutView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        logout(request)
        return redirect('voter-login')
    
class VoterViewSet(viewsets.ModelViewSet):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def verify_registration(self, request, pk=None):
        voter = self.get_object()
        voter.registration_status = 'Verified'
        voter.save()
        return Response({'status': 'Registration verified'}, status=status.HTTP_200_OK)
    
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=False, methods=['get'])
    def results(self, request):
        candidate_votes = Candidate.objects.values('position', 'name').annotate(total_votes=Sum('votes')).order_by('position', '-total_votes')
        
        results = {}
        for item in candidate_votes:
            position = item['position']
            if position not in results:
                results[position] = []
            results[position].append({'candidate': item['name'], 'votes': item['total_votes']})
        
        winners = {}
        for position, candidates in results.items():
            if candidates:
                winners[position] = candidates[0]['candidate']
        
        return Response({'results': results, 'winners': winners}, status=status.HTTP_200_OK)

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]