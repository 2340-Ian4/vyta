from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import UserConnection, Post, Like, Comment, Activity, PostReport
from user.models import UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.contrib import messages
from django.db.models import Sum, Count
from workouts.models import Workout

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
    profile_user = get_object_or_404(User, id=id)
    is_own_profile = (request.user == profile_user)
    
    # Get profile
    profile = profile_user.profile
    
    # Check if current user is following this user
    is_following = UserConnection.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()
    
    # Get followers and following
    followers = User.objects.filter(
        id__in=UserConnection.objects.filter(following=profile_user).values_list('follower', flat=True)
    ).select_related('profile')
    
    following = User.objects.filter(
        id__in=UserConnection.objects.filter(follower=profile_user).values_list('following', flat=True)
    ).select_related('profile')
    
    # Calculate workout statistics
    workout_stats = Workout.objects.filter(user=profile_user).aggregate(
        total_workouts=Count('id'),
        total_calories=Sum('calories_burned'),
        total_minutes=Sum('duration')
    )
    
    # Update profile with calculated statistics
    profile.workouts_completed = workout_stats['total_workouts'] or 0
    profile.calories_burned = workout_stats['total_calories'] or 0
    profile.active_minutes = workout_stats['total_minutes'] or 0
    profile.save()
    
    # Get recent workouts
    recent_workouts = Workout.objects.filter(user=profile_user).order_by('-date')[:5]
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'followers': followers,
        'following': following,
        'followers_count': followers.count(),
        'following_count': following.count(),
        'recent_workouts': recent_workouts,
    }
    
    return render(request, 'social/profile.html', context)

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
    """View the social feed with posts from followed users"""
    # Get users that the current user follows
    following = UserConnection.objects.filter(follower=request.user).values_list('following', flat=True)
    
    # Get all users except current user for suggestions
    all_users = User.objects.exclude(id=request.user.id).select_related('profile')
    
    # Get recent posts from followed users and current user
    posts = Post.objects.filter(
        models.Q(author__in=following) | models.Q(author=request.user),
        is_hidden=False
    ).select_related(
        'author',
        'author__profile'
    ).prefetch_related(
        'likes',
        'comments',
        'comments__user',
        'comments__user__profile'
    ).order_by('-created_at')
    
    # Get suggested users (users not followed)
    suggested_users = all_users.exclude(id__in=following)[:3]
    
    # Set current user on each post for like checking
    for post in posts:
        post._current_user = request.user
    
    return render(request, 'social/feed.html', {
        'posts': posts,
        'suggested_users': suggested_users,
        'show_suggestions': True,  # Always show suggestions
    })

@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        content = request.POST.get('content')
        media = request.FILES.get('media')
        
        if content or media:
            post = Post.objects.create(
                author=request.user,
                content=content,
                media=media
            )
            
            # Create activity
            Activity.objects.create(
                user=request.user,
                activity_type='post',
                content_id=post.id,
                details={'post_content': content}
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
        post.likes_count = max(0, post.likes_count - 1)
    else:
        post.likes_count += 1
        
    post.save()
    
    # Create activity
    if created:
        Activity.objects.create(
            user=request.user,
            activity_type='like',
            content_id=post.id,
            details={'post_author': post.author.username}
        )
    
    return redirect('social.feed')

@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    if request.method == 'POST':
        content = request.POST.get('comment')
        if content:
            post = get_object_or_404(Post, id=post_id)
            comment = Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )
            post.comments_count += 1
            post.save()
            
            # Create activity
            Activity.objects.create(
                user=request.user,
                activity_type='comment',
                content_id=post.id,
                details={
                    'post_author': post.author.username,
                    'comment_content': content
                }
            )
            
    return redirect('social.feed')

@login_required
def report_post(request):
    """Report a post"""
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        
        if post_id and reason:
            post = get_object_or_404(Post, id=post_id)
            PostReport.objects.create(
                post=post,
                reporter=request.user,
                reason=reason,
                description=description
            )
            
    return redirect('social.feed')

@login_required
def delete_post(request):
    """Delete a post"""
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        if post_id:
            post = get_object_or_404(Post, id=post_id)
            if post.author == request.user:
                post.delete()
                
    return redirect('social.feed')

@login_required
def follow_user(request, user_id):
    """Follow or unfollow a user"""
    user_to_follow = get_object_or_404(User, id=user_id)
    connection, created = UserConnection.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    # Get or create profiles
    follower_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    following_profile, _ = UserProfile.objects.get_or_create(user=user_to_follow)
    
    if not created:
        # Unfollow
        connection.delete()
        follower_profile.following_count = max(0, follower_profile.following_count - 1)
        following_profile.followers_count = max(0, following_profile.followers_count - 1)
    else:
        # Follow
        follower_profile.following_count += 1
        following_profile.followers_count += 1
    
    follower_profile.save()
    following_profile.save()
    
    return redirect('social.profile', id=user_id)

@login_required
def search_users(request):
    """Search for users"""
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            username__icontains=query
        ).exclude(
            id=request.user.id
        ).select_related('profile')[:5]
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON for AJAX requests
            results = [{
                'id': user.id,
                'username': user.username,
                'profile_pic': user.profile.profile_pic.url if user.profile.profile_pic else None,
                'is_following': UserConnection.objects.filter(
                    follower=request.user,
                    following=user
                ).exists()
            } for user in users]
            return JsonResponse({'results': results})
        
        # For regular requests, return the full page
        return render(request, 'social/search_results.html', {
            'search_results': users,
            'query': query
        })
    
    return JsonResponse({'results': []})

@login_required
def discover_users(request):
    """View for discovering users to follow"""
    # Get users that the current user follows
    following = UserConnection.objects.filter(follower=request.user).values_list('following', flat=True)
    
    # Get all users except current user and those already followed
    users = User.objects.exclude(
        id__in=following
    ).exclude(
        id=request.user.id
    ).select_related('profile')
    
    # Get workout stats for all users in one query
    workout_stats = Workout.objects.filter(
        user__in=users
    ).values('user').annotate(
        total_workouts=Count('id'),
        total_calories=Sum('calories_burned'),
        total_minutes=Sum('duration')
    )
    
    # Create a dictionary of stats by user ID
    stats_dict = {stat['user']: stat for stat in workout_stats}
    
    # Attach stats to each user
    for user in users:
        user.stats = stats_dict.get(user.id, {
            'total_workouts': 0,
            'total_calories': 0,
            'total_minutes': 0
        })
    
    return render(request, 'social/discover_users.html', {
        'users': users,
    })

