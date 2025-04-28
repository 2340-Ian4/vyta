from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from .models import UserProfile, Complaint, UserBadge
from social.models import UserConnection
from workouts.models import WorkoutGoal, Workout

@login_required
def index(request):
    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    goals = WorkoutGoal.objects.filter(user=request.user)
    
    return render(request, 'user/index.html', {
        'profile': profile,
        'goals': goals
    })

@login_required
def update_username(request):
    """
    View to handle username updates.
    """
    if request.method == 'POST':
        new_username = request.POST.get('username')
        if new_username and new_username != request.user.username:
            # Check if username is already taken
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'This username is already taken.')
            else:
                request.user.username = new_username
                request.user.save()
                messages.success(request, 'Username updated successfully!')
        else:
            messages.error(request, 'Please provide a valid username.')
    
    return redirect('user.index')

@login_required
def update_goals(request):
    """
    View to handle fitness goals updates.
    """
    if request.method == 'POST':
        # This is a placeholder for now
        messages.success(request, 'Fitness goals updated successfully!')
    
    return redirect('user.index')

@login_required
def profile(request, username=None):
    """
    View function for user profile pages.
    If username is None, show the logged-in user's profile.
    Otherwise, show the profile of the specified user.
    """
    if username is None:
        # Show current user's profile
        user = request.user
        is_own_profile = True
    else:
        # Show another user's profile
        user = get_object_or_404(User, username=username)
        is_own_profile = (user == request.user)
    
    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user's followers and following
    followers = User.objects.filter(
        id__in=UserConnection.objects.filter(following=user).values_list('follower', flat=True)
    ).select_related('profile')
    
    following = User.objects.filter(
        id__in=UserConnection.objects.filter(follower=user).values_list('following', flat=True)
    ).select_related('profile')
    
    # Get counts
    followers_count = followers.count()
    following_count = following.count()
    
    # Calculate workout statistics
    workout_stats = Workout.objects.filter(user=user).aggregate(
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
    recent_workouts = Workout.objects.filter(user=user).order_by('-date')[:5]
    
    # Get user's achievements
    achievements = UserBadge.objects.filter(
        user_profile=profile
    ).select_related('badge').order_by('-earned_at')
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'followers': followers,
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
        'recent_workouts': recent_workouts,
        'achievements': achievements,
    }
    
    return render(request, 'user/profile.html', context)

@login_required
def update_profile_picture(request):
    """
    View to handle profile picture updates.
    """
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        profile = request.user.profile
        profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        messages.success(request, 'Profile picture updated successfully!')
    else:
        messages.error(request, 'Please select a valid image file.')
    
    return redirect('user.profile')

@login_required
def remove_profile_picture(request):
    """
    View to handle removing the profile picture.
    """
    profile = request.user.profile
    profile.profile_pic = None
    profile.save()
    messages.success(request, 'Profile picture removed successfully!')
    return redirect('user.profile')

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        type = request.POST.get('type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        complaint = Complaint.objects.create(
            user=request.user,
            type=type,
            title=title,
            description=description
        )
        
        messages.success(request, 'Your feedback has been submitted successfully!')
        return redirect('user.index')
    
    return redirect('user.index')
