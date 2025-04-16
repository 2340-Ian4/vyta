from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:id>/', views.profile, name='social.profile'),  # View a user's profile
    path('follow/<int:id>/', views.follow, name='social.follow'),    # Follow a user
    path('unfollow/<int:id>/', views.unfollow, name='social.unfollow'),  # Unfollow a user
    path('feed/', views.feed, name='social.feed'),                   # View the social feed
]