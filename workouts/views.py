from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from .models import Workout, WorkoutGoal, WorkoutSuggestion
from .forms import WorkoutForm, WorkoutGoalForm
from achievements.models import LeaderboardEntry, LeaderboardType
from user.models import UserProfile
from .gemini_api import get_workout_suggestions
import logging
import json

logger = logging.getLogger(__name__)

@login_required
def index(request):
    workouts = Workout.objects.filter(user=request.user)[:5]  # Get recent workouts
    goals = WorkoutGoal.objects.filter(user=request.user)  # Get all goals for the user
    
    return render(request, 'workouts/index.html', {
        'workouts': workouts,
        'goals': goals,
    })

@login_required
def history(request):
    workouts = Workout.objects.filter(user=request.user)
    return render(request, 'workouts/history.html', {'workouts': workouts})

@login_required
def log_workout(request):
    # Get the return_to parameter, default to workouts.index
    return_to = request.GET.get('return_to', 'workouts.index')
    
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.date = timezone.now()  # Explicitly set the date to now
            workout.save()
            
            logger.info(f"New workout saved: {workout.name} - {workout.calories_burned} calories at {workout.date}")
            
            # Update user profile stats
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.workouts_completed += 1
            user_profile.calories_burned += workout.calories_burned
            user_profile.active_minutes += workout.duration
            
            # Update streak
            today = timezone.now().date()
            if user_profile.last_workout_date:
                day_diff = (today - user_profile.last_workout_date).days
                if day_diff <= 1:  # Either today or yesterday
                    user_profile.streak_days += 1 if day_diff == 1 else 0
                else:
                    # Reset streak if more than 1 day has passed
                    user_profile.streak_days = 1
            else:
                user_profile.streak_days = 1
                
            user_profile.last_workout_date = today
            user_profile.save()
            
            # Check for badge awards
            user_profile.check_and_award_badges()
            
            # Update leaderboard data
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            
            logger.info(f"Updating leaderboard for week of {week_start}")
            
            # Get all users with the same fitness level
            users = UserProfile.objects.filter(fitness_level=user_profile.fitness_level)
            logger.info(f"Found {users.count()} users with fitness level {user_profile.fitness_level}")
            
            # Update calories burned leaderboard
            user_scores = []
            for profile in users:
                total_calories = Workout.objects.filter(
                    user=profile.user,
                    date__date__gte=week_start,
                    date__date__lte=today
                ).aggregate(total=Sum('calories_burned'))['total'] or 0
                user_scores.append((profile.user, total_calories))
                logger.info(f"User {profile.user.username}: {total_calories} calories")
            
            # Sort users by score in descending order
            user_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Update leaderboard entries
            for rank, (user, score) in enumerate(user_scores, 1):
                entry, created = LeaderboardEntry.objects.update_or_create(
                    user=user,
                    leaderboard_type=LeaderboardType.CALORIES_BURNED,
                    week_start=week_start,
                    defaults={
                        'score': score,
                        'rank': rank
                    }
                )
                logger.info(f"Updated leaderboard entry for {user.username}: rank {rank}, score {score}")
            
            # Update active minutes leaderboard
            user_scores = []
            for profile in users:
                total_minutes = Workout.objects.filter(
                    user=profile.user,
                    date__date__gte=week_start,
                    date__date__lte=today
                ).aggregate(total=Sum('duration'))['total'] or 0
                user_scores.append((profile.user, total_minutes))
                logger.info(f"User {profile.user.username}: {total_minutes} minutes")
            
            # Sort users by score in descending order
            user_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Update leaderboard entries
            for rank, (user, score) in enumerate(user_scores, 1):
                entry, created = LeaderboardEntry.objects.update_or_create(
                    user=user,
                    leaderboard_type=LeaderboardType.ACTIVE_MINUTES,
                    week_start=week_start,
                    defaults={
                        'score': score,
                        'rank': rank
                    }
                )
                logger.info(f"Updated leaderboard entry for {user.username}: rank {rank}, score {score}")
            
            # Update workouts completed leaderboard
            user_scores = []
            for profile in users:
                workout_count = Workout.objects.filter(
                    user=profile.user,
                    date__date__gte=week_start,
                    date__date__lte=today
                ).count()
                user_scores.append((profile.user, workout_count))
                logger.info(f"User {profile.user.username}: {workout_count} workouts")
            
            # Sort users by score in descending order
            user_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Update leaderboard entries
            for rank, (user, score) in enumerate(user_scores, 1):
                entry, created = LeaderboardEntry.objects.update_or_create(
                    user=user,
                    leaderboard_type=LeaderboardType.WORKOUTS_COMPLETED,
                    week_start=week_start,
                    defaults={
                        'score': score,
                        'rank': rank
                    }
                )
                logger.info(f"Updated leaderboard entry for {user.username}: rank {rank}, score {score}")
            
            messages.success(request, 'Workout logged successfully!')
            return redirect(return_to)
    else:
        form = WorkoutForm()
    
    return render(request, 'workouts/log_workout.html', {'form': form, 'return_to': return_to})

@login_required
def set_goal(request):
    # Get the return_to parameter, default to workouts.index
    return_to = request.GET.get('return_to', 'workouts.index')
    
    # Check if user has reached the goal limit
    current_goals = WorkoutGoal.objects.filter(user=request.user).count()
    max_goals = 3
    
    if current_goals >= max_goals and request.method == 'GET':
        messages.warning(request, f'You can only have {max_goals} goals at a time. Please delete some goals before adding new ones.')
        return redirect(return_to)
    
    if request.method == 'POST':
        form = WorkoutGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal added successfully!')
            return redirect(return_to)
    else:
        form = WorkoutGoalForm()
    
    return render(request, 'workouts/set_goal.html', {
        'form': form,
        'current_goals': current_goals,
        'max_goals': max_goals,
        'return_to': return_to
    })

@login_required
def get_goal_progress(request, goal_id):
    goal = get_object_or_404(WorkoutGoal, id=goal_id, user=request.user)
    return JsonResponse({'progress': goal.progress})

@login_required
@require_http_methods(["GET"])
def get_goal(request, goal_id):
    goal = get_object_or_404(WorkoutGoal, id=goal_id, user=request.user)
    return JsonResponse({
        'goal_type': goal.goal_type,
        'target': goal.target,
        'end_date': goal.end_date.strftime('%Y-%m-%d') if goal.end_date else None,
        'progress': goal.progress
    })

@login_required
@require_http_methods(["POST"])
def update_goal(request, goal_id):
    goal = get_object_or_404(WorkoutGoal, id=goal_id, user=request.user)
    form = WorkoutGoalForm(request.POST, instance=goal)
    
    if form.is_valid():
        goal = form.save()
        # Clear workout suggestions
        WorkoutSuggestion.objects.filter(user=request.user).delete()
        return JsonResponse({
            'success': True,
            'progress': goal.progress,
            'goal_type_display': goal.get_goal_type_display(),
            'target': goal.target
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

@login_required
@require_http_methods(["POST"])
def add_goal(request):
    form = WorkoutGoalForm(request.POST)
    if form.is_valid():
        goal = form.save(commit=False)
        goal.user = request.user
        goal.save()
        # Clear workout suggestions
        WorkoutSuggestion.objects.filter(user=request.user).delete()
        return JsonResponse({
            'success': True,
            'goal_id': goal.id,
            'goal_type_display': goal.get_goal_type_display(),
            'target': goal.target,
            'progress': goal.progress,
            'end_date': goal.end_date.strftime('%b %d, %Y') if goal.end_date else None
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

@login_required
@require_http_methods(["POST"])
def delete_goal(request, goal_id):
    goal = get_object_or_404(WorkoutGoal, id=goal_id, user=request.user)
    goal.delete()
    # Clear workout suggestions
    WorkoutSuggestion.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    workout.delete()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def log_workout_ajax(request):
    """
    AJAX endpoint for logging workouts directly from the home page dashboard
    """
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        # Create new workout
        workout = Workout(
            user=request.user,
            name=data.get('name', ''),
            description=data.get('description', ''),
            duration=int(data.get('duration', 0)),
            calories_burned=int(data.get('calories_burned', 0)),
            notes=data.get('notes', ''),
            date=timezone.now()
        )
        workout.save()
        
        # Update user profile stats
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.workouts_completed += 1
        user_profile.calories_burned += workout.calories_burned
        user_profile.active_minutes += workout.duration
        
        # Update streak
        today = timezone.now().date()
        if user_profile.last_workout_date:
            day_diff = (today - user_profile.last_workout_date).days
            if day_diff <= 1:  # Either today or yesterday
                user_profile.streak_days += 1 if day_diff == 1 else 0
            else:
                # Reset streak if more than 1 day has passed
                user_profile.streak_days = 1
        else:
            user_profile.streak_days = 1
            
        user_profile.last_workout_date = today
        user_profile.save()
        
        # Update leaderboards (code from log_workout view)
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Get all users with the same fitness level
        users = UserProfile.objects.filter(fitness_level=user_profile.fitness_level)
        
        # Update calories burned leaderboard
        user_scores = []
        for profile in users:
            total_calories = Workout.objects.filter(
                user=profile.user,
                date__date__gte=week_start,
                date__date__lte=today
            ).aggregate(total=Sum('calories_burned'))['total'] or 0
            user_scores.append((profile.user, total_calories))
        
        # Sort users by score in descending order
        user_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Update leaderboard entries
        for rank, (user, score) in enumerate(user_scores, 1):
            entry, created = LeaderboardEntry.objects.update_or_create(
                user=user,
                leaderboard_type=LeaderboardType.CALORIES_BURNED,
                week_start=week_start,
                defaults={
                    'score': score,
                    'rank': rank
                }
            )
        
        # Update active minutes leaderboard
        user_scores = []
        for profile in users:
            total_minutes = Workout.objects.filter(
                user=profile.user,
                date__date__gte=week_start,
                date__date__lte=today
            ).aggregate(total=Sum('duration'))['total'] or 0
            user_scores.append((profile.user, total_minutes))
        
        # Sort users by score in descending order
        user_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Update leaderboard entries
        for rank, (user, score) in enumerate(user_scores, 1):
            entry, created = LeaderboardEntry.objects.update_or_create(
                user=user,
                leaderboard_type=LeaderboardType.ACTIVE_MINUTES,
                week_start=week_start,
                defaults={
                    'score': score,
                    'rank': rank
                }
            )
        
        # Update workouts completed leaderboard
        user_scores = []
        for profile in users:
            workout_count = Workout.objects.filter(
                user=profile.user,
                date__date__gte=week_start,
                date__date__lte=today
            ).count()
            user_scores.append((profile.user, workout_count))
        
        # Sort users by score in descending order
        user_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Update leaderboard entries
        for rank, (user, score) in enumerate(user_scores, 1):
            entry, created = LeaderboardEntry.objects.update_or_create(
                user=user,
                leaderboard_type=LeaderboardType.WORKOUTS_COMPLETED,
                week_start=week_start,
                defaults={
                    'score': score,
                    'rank': rank
                }
            )
        
        # Check for badge awards
        user_profile.check_and_award_badges()
        
        return JsonResponse({
            'success': True,
            'message': 'Workout logged successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
def get_suggestions(request):
    """Get personalized workout suggestions using Gemini API."""
    try:
        # Check if we should force refresh
        force_refresh = request.GET.get('refresh') == 'true'
        
        # Get existing suggestions if available and not forcing refresh
        if not force_refresh:
            existing_suggestions = WorkoutSuggestion.objects.filter(user=request.user)
            if existing_suggestions.exists():
                return render(request, 'workouts/suggestions.html', {
                    'suggestions': existing_suggestions
                })

        # Get user's fitness profile and goals
        profile = request.user.profile
        goals = WorkoutGoal.objects.filter(user=request.user)
        
        # Prepare context for Gemini
        context = {
            'fitness_level': profile.fitness_level,
            'goals': [f"{goal.get_goal_type_display()}: {goal.target}" for goal in goals],
            'preferences': "No specific preferences"  # Default value since workout_preferences doesn't exist
        }
        
        # Get suggestions from Gemini
        suggestions = get_workout_suggestions(context)
        
        # Delete existing suggestions
        WorkoutSuggestion.objects.filter(user=request.user).delete()
        
        # Save new suggestions
        for suggestion in suggestions:
            WorkoutSuggestion.objects.create(
                user=request.user,
                name=suggestion['name'],
                description=suggestion['description'],
                duration=suggestion['duration'],
                calories=suggestion['calories']
            )
        
        return render(request, 'workouts/suggestions.html', {
            'suggestions': WorkoutSuggestion.objects.filter(user=request.user)
        })
    except Exception as e:
        logger.error(f"Error getting workout suggestions: {str(e)}")
        return render(request, 'workouts/suggestions.html', {
            'error': f'Error generating workout suggestions: {str(e)}'
        })

@login_required
def update_goal_progress(request, goal_id):
    """Update goal progress and trigger suggestions refresh."""
    try:
        goal = WorkoutGoal.objects.get(id=goal_id, user=request.user)
        progress = int(request.POST.get('progress', 0))
        
        if not 0 <= progress <= 100:
            return JsonResponse({'success': False, 'message': 'Progress must be between 0 and 100'})
        
        goal.progress = progress
        goal.save()
        
        # Clear workout suggestions
        WorkoutSuggestion.objects.filter(user=request.user).delete()
        
        return JsonResponse({'success': True})
    except WorkoutGoal.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Goal not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
