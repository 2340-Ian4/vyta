from django.shortcuts import render
from django.shortcuts import redirect
from .forms import CustomUserCreationForm, CustomErrorList, ProfileSetupForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from user.models import UserProfile
from django.contrib.auth.models import User
from workouts.models import WorkoutGoal
from django.contrib import messages

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
    
    # Get or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        template_data['form'] = ProfileSetupForm(instance=profile)
        return render(request, 'accounts/profile_setup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = ProfileSetupForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
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
            # Get the first error message
            first_error = next(iter(form.errors.values()))[0]
            template_data['error'] = first_error
            template_data['form'] = form
            return render(request, 'accounts/profile_setup.html',
                {'template_data': template_data})
        
def about(request):
    return render(request, 'accounts/about.html')