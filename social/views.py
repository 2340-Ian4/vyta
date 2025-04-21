from django.shortcuts import render, redirect
from django.http import HttpResponse

# Dummy data for simplicity
users = [
    {'id': 1, 'name': 'Alice', 'followers': 10, 'friends': [2]},
    {'id': 2, 'name': 'Bob', 'followers': 5, 'friends': [1]},
]

# Update posts data to include likes and comments
posts = [
    {
        'id': 1, 
        'user_id': 1, 
        'content': 'Hello world!', 
        'author': 'Alice',
        'likes': [],
        'comments': []
    },
    {
        'id': 2, 
        'user_id': 2, 
        'content': 'Django is awesome!', 
        'author': 'Bob',
        'likes': [1],  # User IDs who liked the post
        'comments': [
            {'user_id': 1, 'author': 'Alice', 'content': 'Yes it is!'}
        ]
    },
    {
        'id': 3, 
        'user_id': 1, 
        'content': 'Learning to code...', 
        'author': 'Alice',
        'likes': [],
        'comments': []
    },
]

def profile(request, id):
    user = next((u for u in users if u['id'] == id), None)
    if not user:
        return HttpResponse("User not found", status=404)
    # Check if users are friends
    current_user = users[0]  # Hardcoded as Alice for demo
    is_friend = id in current_user['friends']
    return render(request, 'social/profile.html', {'user': user, 'is_friend': is_friend})

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
# Profile-related functions have been moved to the profiles app

def add_friend(request, id):
    user = next((u for u in users if u['id'] == id), None)
    current_user = users[0]  # Hardcoded as Alice for demo
    if user and id not in current_user['friends']:
        current_user['friends'].append(id)
        user['friends'].append(current_user['id'])
    return redirect('social.profile', id=id)

def remove_friend(request, id):
    user = next((u for u in users if u['id'] == id), None)
    current_user = users[0]  # Hardcoded as Alice for demo
    if user and id in current_user['friends']:
        current_user['friends'].remove(id)
        user['friends'].remove(current_user['id'])
    return redirect('social.profile', id=id)

def feed(request):
    current_user = users[0]  # Hardcoded as Alice for demo
    friends = [u for u in users if u['id'] in current_user['friends']]
    return render(request, 'social/feed.html', {
        'users': users,
        'posts': posts,
        'friends': friends
    })

def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        new_post = {
            'id': len(posts) + 1,
            'user_id': 1,
            'content': content,
            'author': 'Alice',
            'likes': [],
            'comments': []
        }
        posts.insert(0, new_post)
    return redirect('social.feed')

def like_post(request, post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    current_user_id = 1  # Hardcoded as Alice for demo
    if post:
        if current_user_id in post['likes']:
            post['likes'].remove(current_user_id)
        else:
            post['likes'].append(current_user_id)
    return redirect('social.feed')

def add_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('comment')
        post = next((p for p in posts if p['id'] == post_id), None)
        if post and content:
            comment = {
                'user_id': 1,  # Hardcoded as Alice for demo
                'author': 'Alice',
                'content': content
            }
            post['comments'].append(comment)
    return redirect('social.feed')

    """View the social feed, with links to profiles"""
    return render(request, 'social/feed.html', {'users': users})
