from django.shortcuts import redirect
from django.urls import reverse
from user.models import UserProfile

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for non-authenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip middleware for profile setup page and static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Skip middleware for profile setup page
        if request.path == reverse('accounts.profile_setup'):
            return self.get_response(request)

        # Check if profile is complete
        try:
            profile = UserProfile.objects.get(user=request.user)
            if not profile.is_profile_complete:
                return redirect('accounts.profile_setup')
        except UserProfile.DoesNotExist:
            # If profile doesn't exist, create one and redirect to setup
            UserProfile.objects.create(user=request.user, is_profile_complete=False)
            return redirect('accounts.profile_setup')

        return self.get_response(request) 