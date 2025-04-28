from django.shortcuts import render
from django.shortcuts import redirect
from .forms import CustomUserCreationForm, CustomErrorList, ProfileSetupForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from user.models import UserProfile
from django.contrib.auth.models import User
from workouts.models import WorkoutGoal
from django.contrib import messages
from django.utils import timezone

# Create your views here.


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')


def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            # Check if user is banned
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.is_banned:
                    remaining_days = profile.get_ban_remaining_days()
                    if remaining_days > 0:
                        template_data['error'] = f'Your account has been temporarily banned. You can log in again in {remaining_days} days.'
                        return render(request, 'accounts/login.html',
                            {'template_data': template_data})
            except UserProfile.DoesNotExist:
                pass
                
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            # Create a UserProfile for the new user with is_profile_complete=False
            UserProfile.objects.create(user=user, is_profile_complete=False)
            # Log the user in
            auth_login(request, user)
            # Redirect to profile setup
            return redirect('accounts.profile_setup')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})

@login_required
def profile_setup(request):
    template_data = {}
    template_data['title'] = 'Complete Your Profile'
    template_data['today_date'] = timezone.now().date().isoformat()
    
    # Get or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        template_data['form'] = ProfileSetupForm(instance=profile)
        return render(request, 'accounts/profile_setup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = ProfileSetupForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user's first and last name
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            # Save the profile
            profile = form.save(commit=False)
            profile.is_profile_complete = True
            profile.save()
            
            # Create the workout goal
            WorkoutGoal.objects.create(
                user=request.user,
                goal_type=form.cleaned_data['goal_type'],
                target=form.cleaned_data['target'],
                end_date=form.cleaned_data['end_date'],
                progress=0
            )
            
            return redirect('home.index')
        else:
            # Get all error messages
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{form.fields[field].label}: {error}")
            
            template_data['error'] = error_messages[0] if error_messages else "Please correct the errors below."
            template_data['form'] = form
            template_data['form_errors'] = form.errors
            return render(request, 'accounts/profile_setup.html',
                {'template_data': template_data})
        
def about(request):
    return render(request, 'accounts/about.html')