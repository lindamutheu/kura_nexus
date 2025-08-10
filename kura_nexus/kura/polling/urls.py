# kura/polling/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'voters', views.VoterViewSet)
router.register(r'candidates', views.CandidateViewSet)
router.register(r'votes', views.VoteViewSet)

urlpatterns = [
    # Main page and authentication URLs
    path('', views.landing_page, name='landing_page'),
    path('voter-login/', views.VoterLoginView.as_view(), name='voter-login'),
    path('voting/', views.voting_page, name='voting_page'),
    path('logout/', views.VoterLogoutView.as_view(), name='voter-logout'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/voter-signup/', views.VoterSignupView.as_view(), name='voter-signup'),
    path('api/cast-vote/', views.cast_vote, name='cast-vote'), 
]