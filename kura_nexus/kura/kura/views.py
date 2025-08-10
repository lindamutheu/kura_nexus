# kura/kura/views.py (or polling/views.py, depending on your project structure)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from polling.models import Position, Candidate # Make sure to import your models
# ... other imports

def landing_page(request):
    return render(request, 'landing_page.html')

@login_required
def voting_page(request):
    try:
        # Assuming your User model has a related 'voter' object
        voter = request.user.voter
    except AttributeError:
        # Handle cases where a User is logged in but doesn't have a Voter profile
        return render(request, 'error_page.html', {'message': 'Voter profile not found.'})

    if voter.is_voted:
        # User has already voted, show them the voted page
        return render(request, 'voted_page.html')
    else:
        # User can vote, fetch positions and candidates
        positions = Position.objects.prefetch_related('candidate_set').all().order_by('order')
        
        context = {
            'positions': positions,
            'user': request.user,
        }
        return render(request, 'voting_page.html', context)