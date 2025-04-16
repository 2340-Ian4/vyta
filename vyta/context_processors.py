def user_profile_pic(request):
    if request.user.is_authenticated:
        return {'user_data': {'profile_pic': 'img/default-profile.png'}}  # Replace with actual logic to fetch the profile pic later
    return {}