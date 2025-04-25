from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import UserConnection, Post, Like, Comment, Activity
from user.models import UserProfile
from django.contrib.auth.models import User

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

@login_required
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

def profile(request, id):
    """View a user's profile"""
    profile_user = get_object_or_404(User, id=id)
    profile = get_object_or_404(UserProfile, user=profile_user)
    
    # Check if current user follows this user
    is_following = UserConnection.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()
    
    # Check if users are friends
    is_friend = UserConnection.objects.filter(
        follower=request.user,
        following=profile_user,
        is_friend=True
    ).exists()
    
    # Get user's recent posts
    recent_posts = Post.objects.filter(author=profile_user).order_by('-created_at')[:5]
    
    # Get user's recent activities
    recent_activities = Activity.objects.filter(user=profile_user).order_by('-created_at')[:10]
    
    # Get user's followers and following counts
    followers_count = UserConnection.objects.filter(following=profile_user).count()
    following_count = UserConnection.objects.filter(follower=profile_user).count()
    
    return render(request, 'social/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'is_following': is_following,
        'is_friend': is_friend,
        'recent_posts': recent_posts,
        'recent_activities': recent_activities,
        'followers_count': followers_count,
        'following_count': following_count,
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

@login_required
def feed(request):
    """View the social feed with posts and activities from followed users"""
    # Get users that the current user follows
    following = UserConnection.objects.filter(follower=request.user).values_list('following', flat=True)
    
    # Get recent posts from followed users
    posts = Post.objects.filter(author__in=following).order_by('-created_at')[:10]
    
    # Get recent activities from followed users
    activities = Activity.objects.filter(user__in=following).order_by('-created_at')[:20]
    
    # Get suggested users to follow (users not followed by current user)
    suggested_users = User.objects.exclude(
        id__in=following
    ).exclude(
        id=request.user.id
    ).select_related('profile')[:5]
    
    # Get user's friends
    friends = UserConnection.objects.filter(
        follower=request.user,
        is_friend=True
    ).select_related('following', 'following__profile')
    
    return render(request, 'social/feed.html', {
        'posts': posts,
        'activities': activities,
        'suggested_users': suggested_users,
        'friends': friends,
    })

@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            post = Post.objects.create(
                author=request.user,
                content=content
            )
    return redirect('social.feed')

@login_required
def like_post(request, post_id):
    """Like or unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )
    if not created:
        like.delete()
    return redirect('social.feed')

@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    if request.method == 'POST':
        content = request.POST.get('comment')
        if content:
            post = get_object_or_404(Post, id=post_id)
            Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )
    return redirect('social.feed')

@login_required
def follow_user(request, user_id):
    """Follow or unfollow a user"""
    user_to_follow = get_object_or_404(User, id=user_id)
    connection, created = UserConnection.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    if not created:
        connection.delete()
    return redirect('social.feed')

    """View the social feed, with links to profiles"""
    return render(request, 'social/feed.html', {'users': users})
@login_required
def add_friend(request, user_id):
    """Add or remove a friend"""
    user_to_friend = get_object_or_404(User, id=user_id)
    connection = get_object_or_404(
        UserConnection,
        follower=request.user,
        following=user_to_friend
    )
    connection.is_friend = not connection.is_friend
    connection.save()
    return redirect('social.feed')

@login_required
def search_users(request):
    """Search for users by username"""
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    else:
        users = User.objects.none()
    
    return render(request, 'social/feed.html', {
        'search_results': users,
        'posts': Post.objects.filter(author__in=UserConnection.objects.filter(follower=request.user).values('following')).order_by('-created_at')[:10],
        'activities': Activity.objects.filter(user__in=UserConnection.objects.filter(follower=request.user).values('following')).order_by('-created_at')[:20],
        'suggested_users': User.objects.exclude(
            id__in=UserConnection.objects.filter(follower=request.user).values('following')
        ).exclude(id=request.user.id).select_related('profile')[:5],
        'friends': UserConnection.objects.filter(
            follower=request.user,
            is_friend=True
        ).select_related('following', 'following__profile'),
    })

