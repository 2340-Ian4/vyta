from django.shortcuts import render

def index(request):
    # Dummy data for now
    leaderboard = [
        {'name': 'Alice', 'goal': 'Lose Weight', 'progress': 80},
        {'name': 'Bob', 'goal': 'Build Muscle', 'progress': 70},
        {'name': 'Charlie', 'goal': 'Lose Weight', 'progress': 60},
    ]
    challenges = [
        {'title': '10,000 Steps a Day', 'description': 'Walk 10,000 steps daily for a week.'},
        {'title': 'Burn 500 Calories', 'description': 'Burn 500 calories in a single workout.'},
    ]
    recent_badges = [
        {'name': 'Step Master', 'description': 'Walked 50,000 steps in a week.'},
        {'name': 'Calorie Burner', 'description': 'Burned 5,000 calories in a month.'},
    ]
    return render(request, 'achievements/index.html', {
        'leaderboard': leaderboard,
        'challenges': challenges,
        'recent_badges': recent_badges,
    })

def badges(request):
    # Dummy data for now
    all_badges = [
        {'name': 'Step Master', 'description': 'Walked 50,000 steps in a week.'},
        {'name': 'Calorie Burner', 'description': 'Burned 5,000 calories in a month.'},
        {'name': 'Workout Warrior', 'description': 'Completed 100 workouts.'},
        {'name': 'Marathon Runner', 'description': 'Ran a full marathon.'},
    ]
    return render(request, 'achievements/badges.html', {'all_badges': all_badges})

# Create your views here.
