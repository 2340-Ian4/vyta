def user_profile_pic(request):
    if request.user.is_authenticated:
        # Try to get the user's profile picture from their profile
        try:
            from user.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile_pic_url = profile.profile_pic.url if profile.profile_pic else 'img/default-profile.png'
            return {'user_data': {'profile_pic': profile_pic_url}}
        except:
            # Fallback to default if there's an error
            return {'user_data': {'profile_pic': 'img/default-profile.png'}}
    return {}