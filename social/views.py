from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import UserConnection, Post, Like, Comment, Activity, PostReport
from user.models import UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

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
    """View a user's profile"""
    profile_user = get_object_or_404(User, id=id)
    
    # If viewing own profile, redirect to user profile page
    if request.user == profile_user:
        return redirect('user.profile')
        
    profile, created = UserProfile.objects.get_or_create(user=profile_user)
    
    # Check if current user follows this user
    is_following = UserConnection.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()
    
    # Get user's posts
    posts = Post.objects.filter(
        author=profile_user,
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
    
    # Get user's followers and following
    followers = User.objects.filter(
        id__in=UserConnection.objects.filter(following=profile_user).values_list('follower', flat=True)
    ).select_related('profile')
    
    following = User.objects.filter(
        id__in=UserConnection.objects.filter(follower=profile_user).values_list('following', flat=True)
    ).select_related('profile')
    
    # Get counts
    followers_count = followers.count()
    following_count = following.count()
    
    return render(request, 'social/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'is_following': is_following,
        'posts': posts,
        'followers': followers,
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

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
    
    # If user isn't following anyone, show posts from all users and suggest users to follow
    if not following.exists():
        posts = Post.objects.filter(
            is_hidden=False
        ).select_related(
            'author',
            'author__profile'
        ).prefetch_related(
            'likes',
            'comments',
            'comments__user',
            'comments__user__profile'
        ).order_by('-created_at')[:10]  # Limit to 10 most recent posts
        
        # Show suggested users to follow
        suggested_users = all_users[:5]
        show_suggestions = True
    else:
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
        
        suggested_users = None
        show_suggestions = False
    
    # Set current user on each post for like checking
    for post in posts:
        post._current_user = request.user
    
    return render(request, 'social/feed.html', {
        'posts': posts,
        'suggested_users': suggested_users,
        'show_suggestions': show_suggestions,
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
    """Search for users by username"""
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    else:
        users = User.objects.none()
    
    return render(request, 'social/search_results.html', {
        'search_results': users,
    })

