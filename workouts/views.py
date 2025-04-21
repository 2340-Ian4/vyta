from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workout, WorkoutGoal
from .forms import WorkoutForm, WorkoutGoalForm

@login_required
def index(request):
    workouts = Workout.objects.filter(user=request.user)[:5]  # Get recent workouts
    try:
        goal = WorkoutGoal.objects.get(user=request.user)
    except WorkoutGoal.DoesNotExist:
        goal = None
    
    # AI-generated workout suggestions (placeholder for now)
    ai_workouts = [
        {'name': 'Full Body Workout', 'description': 'A 30-minute full-body workout focusing on strength and endurance.'},
        {'name': 'Cardio Blast', 'description': 'A 20-minute high-intensity cardio session to boost metabolism.'},
        {'name': 'Strength Training', 'description': 'A 40-minute strength training session targeting major muscle groups.'},
    ]
    
    return render(request, 'workouts/index.html', {
        'workouts': workouts,
        'goal': goal,
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
