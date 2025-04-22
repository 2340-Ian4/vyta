from django.urls import path
from . import views

urlpatterns = [
    # Legacy social profile URLs (renamed from social.profile to profiles.social_profile)
    path('social-profile/<int:id>/', views.social_profile, name='profiles.social_profile'),
    path('follow/<int:id>/', views.follow, name='profiles.follow'),
    path('unfollow/<int:id>/', views.unfollow, name='profiles.unfollow'),
    
    # New user profile URLs
    path('list/', views.user_profile_list, name='profiles.list'),
    path('user/<str:username>/', views.user_profile_detail, name='profiles.user_detail'),
] 