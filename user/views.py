from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile

@login_required
def upload_profile_pic(request):
    """Handle profile picture uploads from the profile page"""
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            # Get the uploaded file
            profile_pic = request.FILES['profile_pic']
            
            # Update the profile picture
            profile.profile_pic = profile_pic
            profile.save()
            
            # Log success message
            messages.success(request, 'Profile picture updated successfully!')
        except Exception as e:
            # Log error if something went wrong
            messages.error(request, f'Error updating profile picture: {str(e)}')
    
    # Redirect back to profile page
    return redirect('user.profile')

@login_required
def index(request):
    # Get or create UserProfile for the current user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle form submissions
    if request.method == 'POST':
        # Profile picture upload
        if 'update_picture' in request.POST and request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('user.index')
        
        # Personal information update
        elif 'update_personal' in request.POST:
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            
            profile.bio = request.POST.get('bio', '')
            profile.location = request.POST.get('location', '')
            profile.save()
            
            messages.success(request, 'Personal information updated successfully!')
            return redirect('user.index')
        
        # Fitness information update
        elif 'update_fitness' in request.POST:
            profile.height = request.POST.get('height', None)
            profile.weight = request.POST.get('weight', None)
            profile.fitness_level = request.POST.get('fitness_level', 'beginner')
            profile.save()
            
            messages.success(request, 'Fitness information updated successfully!')
            return redirect('user.index')
            
        # Privacy settings update
        elif 'update_privacy' in request.POST:
            # These would be additional fields you'd need to add to the UserProfile model
            profile.show_email = 'show_email' in request.POST
            profile.show_stats = 'show_stats' in request.POST
            profile.allow_following = 'allow_following' in request.POST
            profile.save()
            
            messages.success(request, 'Privacy settings updated successfully!')
            return redirect('user.index')
            
        # Password change
        elif 'update_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Basic validation
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep user logged in
                messages.success(request, 'Password changed successfully!')
            
            return redirect('user.index')
    
    # Prepare user data for the template
    user_data = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'profile_pic': profile.profile_pic.url if profile.profile_pic else 'img/default-profile.png',
        'bio': profile.bio,
        'location': profile.location,
        'height': profile.height,
        'weight': profile.weight,
        'fitness_level': profile.fitness_level,
        # These would be additional fields you'd need to add to the UserProfile model
        'show_email': getattr(profile, 'show_email', False),
        'show_stats': getattr(profile, 'show_stats', False),
        'allow_following': getattr(profile, 'allow_following', True),
    }
    
    return render(request, 'user/index.html', {'user_data': user_data})

@login_required
def lifetime_stats(request):
    # Get the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Real data from profile
    stats = {
        'workouts_completed': profile.workouts_completed,
        'calories_burned': profile.calories_burned,
        'active_minutes': profile.active_minutes,
    }
    return render(request, 'user/lifetime_stats.html', {'stats': stats})

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
    
    # Get the user's achievements and workouts
    # In a real implementation, this would query the related models
    achievements = [
        {'name': 'Early Bird', 'description': 'Complete 5 workouts before 8am'},
        {'name': 'Marathon Runner', 'description': 'Run a total of 42.2km'},
    ]
    
    recent_workouts = [
        {'date': '2023-04-15', 'name': 'Morning Run', 'duration': '30 minutes'},
        {'date': '2023-04-12', 'name': 'Weight Training', 'duration': '45 minutes'},
    ]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'achievements': achievements,
        'recent_workouts': recent_workouts,
    }
    
    return render(request, 'user/profile.html', context)
