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
    profile_user = next((u for u in users if u['id'] == id), None)
    if not profile_user:
        return HttpResponse("User not found", status=404)
    # Check if users are friends
    current_user = users[0]  # Hardcoded as Alice for demo
    is_friend = id in current_user['friends']
    
    # Check if current user is following this user
    # For the demo, we'll consider current user is following if followers > 0
    is_following = False
    if 'following_users' not in current_user:
        current_user['following_users'] = [2]  # Default Alice is following Bob
    
    is_following = id in current_user['following_users']
    
    # Add sample fitness data to match our enhanced profile template
    profile_user['fitness_level'] = 'Intermediate'
    profile_user['location'] = 'New York'
    profile_user['bio'] = 'Fitness enthusiast and yoga instructor'
    profile_user['workouts_completed'] = 125
    profile_user['calories_burned'] = 15400
    profile_user['active_minutes'] = 3250
    profile_user['following'] = 8
    
    # Sample achievements
    profile_user['achievements'] = [
        {'name': 'Early Bird', 'description': 'Complete 5 workouts before 8am'},
        {'name': 'Marathon Runner', 'description': 'Run a total of 42.2km'},
    ]
    
    # Sample workouts
    profile_user['recent_workouts'] = [
        {'date': '2023-04-15', 'name': 'Morning Run', 'duration': '30 minutes'},
        {'date': '2023-04-12', 'name': 'Weight Training', 'duration': '45 minutes'},
    ]
    
    return render(request, 'profiles/social_profile.html', {
        'profile_user': profile_user, 
        'is_friend': is_friend,
        'is_following': is_following
    })

def follow(request, id):
    user = next((u for u in users if u['id'] == id), None)
    current_user = users[0]  # Hardcoded as Alice for demo
    
    if user:
        # Add to followers
        user['followers'] += 1
        
        # Add to current user's following list
        if 'following_users' not in current_user:
            current_user['following_users'] = []
        
        if id not in current_user['following_users']:
            current_user['following_users'].append(id)
            
    return redirect('social.profile', id=id)

def unfollow(request, id):
    user = next((u for u in users if u['id'] == id), None)
    current_user = users[0]  # Hardcoded as Alice for demo
    
    if user and user['followers'] > 0:
        # Reduce followers
        user['followers'] -= 1
        
        # Remove from current user's following list
        if 'following_users' in current_user and id in current_user['following_users']:
            current_user['following_users'].remove(id)
            
    return redirect('social.profile', id=id)

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
