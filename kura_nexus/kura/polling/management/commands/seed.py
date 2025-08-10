# polling/management/commands/seed.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from polling.models import Voter, Candidate, StudentID, Vote, Position
import random
import names
from collections import defaultdict
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with sample data for development and testing.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Seeding database..."))

        # Clean existing data
        Voter.objects.all().delete()
        Candidate.objects.all().delete()
        StudentID.objects.all().delete()
        User.objects.all().delete()
        Vote.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("Existing data cleared."))

        # 1. Create StudentID records (pre-registered students)
        self.stdout.write("Creating 2 pre-registered students...")
        student_ids = []
        for i in range(2):
            first_name = names.get_first_name()
            last_name = names.get_last_name()
            student_id = f'ALX{random.randint(1000, 9999)}'
            email = f'{first_name.lower()}.{last_name.lower()}{i}@alx.com'
            StudentID.objects.create(
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                email=email
            )
            student_ids.append(student_id)
        self.stdout.write(self.style.SUCCESS("Pre-registered students created."))

        # 2. Create Django Users and Voter profiles
        self.stdout.write("Creating 5 sample voters...")
        voter_student_ids = random.sample(student_ids, 2) # Select 5 to create voters for
        for student_id in voter_student_ids:
            student = StudentID.objects.get(student_id=student_id)
            user = User.objects.create_user(
                username=student.student_id,
                email=student.email,
                password='password123',
                first_name=student.first_name,
                last_name=student.last_name
            )
            Voter.objects.create(
                user=user,
                student_id=student.student_id,
                is_voted=False,
                registration_status='Verified'
            )
        self.stdout.write(self.style.SUCCESS("Sample voters and users created."))

        # 3. Create Candidates
        self.stdout.write("Creating positions and candidates...")
        
        # Define the positions and create the model instances first
        position_names = ['President', 'Vice President', 'Treasurer', 'Secretary']
        position_objects = {}
        for name in position_names:
            pos, created = Position.objects.get_or_create(name=name)
            position_objects[name] = pos

        # Now, create candidates for each position using the instances
        for position_name, position_obj in position_objects.items():
            for i in range(3): # Create 3 candidates for each position
                Candidate.objects.create(
                    name=names.get_full_name(),
                    position=position_obj, # Pass the Position object, not the string
                    bio=fake.paragraph(nb_sentences=3),
                    votes=0
                )
        self.stdout.write(self.style.SUCCESS("Candidates created."))

        # 4. Simulate some votes
        self.stdout.write("Simulating some votes...")
        voters = Voter.objects.filter(is_voted=False)[:3]
        
        for voter in voters:
            # Get all candidates for each position
            for position_name, position_obj in position_objects.items():
                candidates = Candidate.objects.filter(position=position_obj)
                
                if candidates.exists():
                    voted_for_candidate = random.choice(candidates)
                    Vote.objects.create(voter=voter, candidate=voted_for_candidate)
                    voted_for_candidate.votes += 1
                    voted_for_candidate.save()
            
            voter.is_voted = True
            voter.save()
            self.stdout.write(f"Voter {voter.user.username} has cast their vote.")
        
        self.stdout.write(self.style.SUCCESS("Votes simulated successfully."))
        # 5. Create a Superuser
        self.stdout.write("Creating superuser...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created with password 'adminpass'."))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists."))
        
        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))