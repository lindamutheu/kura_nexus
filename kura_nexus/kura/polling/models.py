from django.db import models
from django.contrib.auth.models import User

class StudentID(models.Model):
    """
    A model to store the list of pre-registered students allowed to vote.
    This serves as a source of truth for the VoterSignupSerializer.
    """
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    student_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    is_voted = models.BooleanField(default=False)
    registration_status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return self.user.username

class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0, help_text="The display order of the position.")

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    votes = models.IntegerField(default=0)
    # Add this new field for the profile picture
    profile_picture = models.ImageField(upload_to='candidates/', blank=True, null=True)

    def __str__(self):
        return self.name

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'candidate')

    def __str__(self):
        return f'{self.voter.user.username} voted for {self.candidate.name}'