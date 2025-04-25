from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Workout, WorkoutGoal
from .forms import WorkoutForm, WorkoutGoalForm

@login_required
def index(request):
    workouts = Workout.objects.filter(user=request.user)[:5]  # Get recent workouts
    goals = WorkoutGoal.objects.filter(user=request.user)  # Get all goals for the user
    
    # AI-generated workout suggestions (placeholder for now)
    ai_workouts = [
        {'name': 'Full Body Workout', 'description': 'A 30-minute full-body workout focusing on strength and endurance.'},
        {'name': 'Cardio Blast', 'description': 'A 20-minute high-intensity cardio session to boost metabolism.'},
        {'name': 'Strength Training', 'description': 'A 40-minute strength training session targeting major muscle groups.'},
    ]
    
    return render(request, 'workouts/index.html', {
        'workouts': workouts,
        'goals': goals,
        'ai_workouts': ai_workouts,
    })

@login_required
def history(request):
    workouts = Workout.objects.filter(user=request.user)
    return render(request, 'workouts/history.html', {'workouts': workouts})

@login_required
def log_workout(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            messages.success(request, 'Workout logged successfully!')
            return redirect('workouts.index')
    else:
        form = WorkoutForm()
    
    return render(request, 'workouts/log_workout.html', {'form': form})

@login_required
def set_goal(request):
    try:
        goal = WorkoutGoal.objects.get(user=request.user)
    except WorkoutGoal.DoesNotExist:
        goal = None
    
    if request.method == 'POST':
        form = WorkoutGoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('workouts.index')
    else:
        form = WorkoutGoalForm(instance=goal)
    
    return render(request, 'workouts/set_goal.html', {'form': form})

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
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    workout.delete()
    return JsonResponse({'success': True})
