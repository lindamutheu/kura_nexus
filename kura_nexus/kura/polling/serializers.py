# polling/serializers.py

from rest_framework import serializers
from .models import Voter, Candidate, Vote, StudentID 
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'

class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = ['id', 'user', 'student_id', 'is_voted', 'registration_status']
        read_only_fields = ['user', 'is_voted', 'registration_status']

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'
        #fields = ['voter', 'candidate', 'timestamp']
        read_only_fields = ['voter', 'timestamp']

class VoterSignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    student_id = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    def validate_student_id(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this student ID already exists.")
        return value