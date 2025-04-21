from django.shortcuts import render, redirect
from django.http import HttpResponse

# Dummy data for simplicity
users = [
    {'id': 1, 'name': 'Alice', 'followers': 10},
    {'id': 2, 'name': 'Bob', 'followers': 5},
]

# Profile-related functions have been moved to the profiles app

def feed(request):
    """View the social feed, with links to profiles"""
    return render(request, 'social/feed.html', {'users': users})
