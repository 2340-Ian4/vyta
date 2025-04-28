from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from workouts.models import Workout, WorkoutGoal
from user.models import UserBadge
from social.models import Post, UserConnection
import random
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.urls import reverse

# List of motivational fitness quotes
MOTIVATIONAL_QUOTES = [
    {"text": "The only bad workout is the one that didn't happen.", "author": "Unknown"},
    {"text": "Strength does not come from the body. It comes from the will.", "author": "Gandhi"},
    {"text": "Take care of your body. It's the only place you have to live.", "author": "Jim Rohn"},
    {"text": "The hardest lift of all is lifting your butt off the couch.", "author": "Unknown"},
    {"text": "Fitness is not about being better than someone else. It's about being better than you used to be.", "author": "Unknown"},
    {"text": "The only way to define your limits is by going beyond them.", "author": "Arthur C. Clarke"},
    {"text": "Your body can stand almost anything. It's your mind that you have to convince.", "author": "Unknown"},
    {"text": "The difference between try and triumph is a little umph.", "author": "Marvin Phillips"},
    {"text": "If it doesn't challenge you, it doesn't change you.", "author": "Fred DeVito"},
    {"text": "The greatest wealth is health.", "author": "Virgil"}
]

@login_required
def index(request):
    # Get user data for personalization
    user = request.user
    user_profile = user.profile
    
    # Calculate workout statistics
    workout_stats = Workout.objects.filter(user=user).aggregate(
        total_workouts=Count('id'),
        total_calories=Sum('calories_burned'),
        total_minutes=Sum('duration')
    )
    
    # Update profile with calculated statistics
    user_profile.workouts_completed = workout_stats['total_workouts'] or 0
    user_profile.calories_burned = workout_stats['total_calories'] or 0
    user_profile.active_minutes = workout_stats['total_minutes'] or 0
    user_profile.save()
    
    fitness_level = user_profile.get_fitness_level_display()
    
    # Get current date info for greeting
    current_time = datetime.now()
    greeting = "Good morning" if current_time.hour < 12 else "Good afternoon" if current_time.hour < 18 else "Good evening"
    
    # Get a random motivational quote
    quote = random.choice(MOTIVATIONAL_QUOTES)
    
    # Get recent workouts
    workouts = Workout.objects.filter(user=user).order_by('-date')[:5]
    
    # Get most recent workout date and calculate days since
    latest_workout = workouts.first()
    days_since_workout = None
    if latest_workout:
        days_since_workout = (datetime.now().date() - latest_workout.date.date()).days
    
    # Get user's active goals
    goals = WorkoutGoal.objects.filter(user=user).order_by('-start_date')[:3]
    
    # Get user achievements/badges
    achievements = UserBadge.objects.filter(
        user_profile=user_profile
    ).select_related('badge').order_by('-earned_at')[:5]
    
    # Get users that the current user follows using UserConnection model
    following_users = UserConnection.objects.filter(
        follower=user
    ).values_list('following', flat=True)
    
    # Get recent posts from followed users
    posts = Post.objects.filter(
        author__in=following_users,
        is_hidden=False
    ).select_related(
        'author', 'author__profile'
    ).order_by('-created_at')[:5]
    
    # If there are no posts from followed users, show some recent posts
    if not posts:
        posts = Post.objects.filter(
            is_hidden=False
        ).select_related(
            'author', 'author__profile'
        ).order_by('-created_at')[:5]
    
    # Create URLs with proper return_to parameters
    log_workout_url = f"{reverse('workouts.log_workout')}?return_to=home.index"
    set_goal_url = f"{reverse('workouts.set_goal')}?return_to=home.index"
    
    context = {
        'user': user,
        'profile': user_profile,
        'fitness_level': fitness_level,
        'greeting': greeting,
        'quote': quote,
        'days_since_workout': days_since_workout,
        'workouts': workouts,
        'goals': goals,
        'achievements': achievements,
        'posts': posts,
        'log_workout_url': log_workout_url,
        'set_goal_url': set_goal_url,
    }
    
    return render(request, 'home/index.html', context)

