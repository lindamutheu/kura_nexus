# kura/polling/admin.py
from django.contrib import admin
from .models import Position, Candidate, Voter, StudentID

# Register the models
admin.site.register(Position)
admin.site.register(Voter)
admin.site.register(StudentID)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'votes')
    search_fields = ('name', 'position__name')
    list_filter = ('position',)
    # This will display the profile picture in the admin change form
    fields = ('name', 'position', 'bio', 'profile_picture', 'votes')
