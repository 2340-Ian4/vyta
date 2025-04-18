from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile

def index(request):
    # Dummy data for now
    user_data = {
        'username': 'JohnDoe',
        'email': 'johndoe@example.com',
        'profile_pic': 'img/default-profile.png',  # Default profile picture
    }
    return render(request, 'user/index.html', {'user_data': user_data})

def lifetime_stats(request):
    # Dummy data for now
    stats = {
        'workouts_completed': 120,
        'calories_burned': 50000,
        'active_minutes': 1500,
    }
    return render(request, 'user/lifetime_stats.html', {'stats': stats})

@login_required
def profile(request, username=None):
    """
    View function for user profile pages.
    If username is None, show the logged-in user's profile.
    Otherwise, show the profile of the specified user.
    """
    if username is None:
        # Show current user's profile
        user = request.user
        is_own_profile = True
    else:
        # Show another user's profile
        user = get_object_or_404(User, username=username)
        is_own_profile = (user == request.user)
    
    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get the user's achievements and workouts
    # In a real implementation, this would query the related models
    achievements = [
        {'name': 'Early Bird', 'description': 'Complete 5 workouts before 8am'},
        {'name': 'Marathon Runner', 'description': 'Run a total of 42.2km'},
    ]
    
    recent_workouts = [
        {'date': '2023-04-15', 'name': 'Morning Run', 'duration': '30 minutes'},
        {'date': '2023-04-12', 'name': 'Weight Training', 'duration': '45 minutes'},
    ]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'achievements': achievements,
        'recent_workouts': recent_workouts,
    }
    
    return render(request, 'user/profile.html', context)
