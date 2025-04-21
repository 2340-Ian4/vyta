from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from user.models import UserProfile

# Dummy data for simplicity (will be replaced with actual database queries)
users = [
    {'id': 1, 'name': 'Alice', 'followers': 10},
    {'id': 2, 'name': 'Bob', 'followers': 5},
]

def social_profile(request, id):
    """Legacy social profile view - shows a simple profile with follow functionality"""
    user = next((u for u in users if u['id'] == id), None)
    if not user:
        return HttpResponse("User not found", status=404)
    return render(request, 'profiles/social_profile.html', {'user': user})

def follow(request, id):
    """Follow a user"""
    user = next((u for u in users if u['id'] == id), None)
    if user:
        user['followers'] += 1
    return redirect('profiles.social_profile', id=id)

def unfollow(request, id):
    """Unfollow a user"""
    user = next((u for u in users if u['id'] == id), None)
    if user and user['followers'] > 0:
        user['followers'] -= 1
    return redirect('profiles.social_profile', id=id)

@login_required
def user_profile_list(request):
    """Show a list of all user profiles"""
    user_profiles = UserProfile.objects.all()
    return render(request, 'profiles/profile_list.html', {'profiles': user_profiles})

@login_required
def user_profile_detail(request, username):
    """Show a detailed user profile using the new UserProfile model"""
    user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    is_own_profile = (user == request.user)
    
    # Get the user's achievements and workouts (sample data for now)
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
    
    return render(request, 'profiles/user_profile.html', context)
