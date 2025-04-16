from django.shortcuts import render, redirect
from django.http import HttpResponse

# Dummy data for simplicity
users = [
    {'id': 1, 'name': 'Alice', 'followers': 10},
    {'id': 2, 'name': 'Bob', 'followers': 5},
]

def profile(request, id):
    user = next((u for u in users if u['id'] == id), None)
    if not user:
        return HttpResponse("User not found", status=404)
    return render(request, 'social/profile.html', {'user': user})

def follow(request, id):
    user = next((u for u in users if u['id'] == id), None)
    if user:
        user['followers'] += 1
    return redirect('social.profile', id=id)

def unfollow(request, id):
    user = next((u for u in users if u['id'] == id), None)
    if user and user['followers'] > 0:
        user['followers'] -= 1
    return redirect('social.profile', id=id)

def feed(request):
    return render(request, 'social/feed.html', {'users': users})
