from django.shortcuts import render

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
