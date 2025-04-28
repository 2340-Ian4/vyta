from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from .models import LeaderboardEntry, LeaderboardType
from user.models import UserProfile, Badge, UserBadge
from workouts.models import Workout

def index(request):
    # Get the start of the current week (Monday)
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Get user's fitness level
    user_profile = UserProfile.objects.get(user=request.user)
    user_fitness_level = user_profile.fitness_level
    
    # Get all leaderboard entries for the current week and user's fitness level
    entries = LeaderboardEntry.objects.filter(
        week_start=week_start,
        user__profile__fitness_level=user_fitness_level
    ).select_related('user', 'user__profile')
    
    # Get user's recent badges
    recent_badges = UserBadge.objects.filter(
        user_profile=user_profile
    ).select_related('badge').order_by('-earned_at')[:5]
    
    context = {
        'leaderboard_types': LeaderboardType.choices,
        'user_fitness_level': user_fitness_level,
        'leaderboards': entries,
        'recent_badges': recent_badges,
    }
    
    return render(request, 'achievements/index.html', context)

def badges(request):
    # Get all badges and user's earned badges
    user_profile = UserProfile.objects.get(user=request.user)
    all_badges = Badge.objects.all()
    earned_badges = UserBadge.objects.filter(user_profile=user_profile).select_related('badge')
    
    # Create a list of badges with earned status
    badges_with_status = []
    for badge in all_badges:
        earned = earned_badges.filter(badge=badge).exists()
        badges_with_status.append({
            'name': badge.name,
            'description': badge.description,
            'earned': earned,
            'earned_at': earned_badges.get(badge=badge).earned_at if earned else None
        })
    
    return render(request, 'achievements/badges.html', {'badges': badges_with_status})

# Create your views here.
