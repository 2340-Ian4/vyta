from django.shortcuts import render

def index(request):
    # Dummy data for now
    progress = {'goal': 'Lose Weight', 'progress': 75}
    ai_workouts = [
        {'name': 'Full Body Workout', 'description': 'A 30-minute full-body workout.'},
        {'name': 'Cardio Blast', 'description': 'A 20-minute high-intensity cardio session.'},
        {'name': 'Strength Training', 'description': 'A 40-minute strength training session.'},
    ]
    return render(request, 'workouts/index.html', {
        'progress': progress,
        'ai_workouts': ai_workouts,
    })

def history(request):
    # Dummy data for now
    workout_history = [
        {'date': '2025-04-10', 'workout': 'Full Body Workout', 'duration': '30 mins'},
        {'date': '2025-04-12', 'workout': 'Cardio Blast', 'duration': '20 mins'},
        {'date': '2025-04-14', 'workout': 'Strength Training', 'duration': '40 mins'},
    ]
    return render(request, 'workouts/history.html', {'workout_history': workout_history})
