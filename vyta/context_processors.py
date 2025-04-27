from user.models import UserProfile
from django.conf import settings

def user_profile_pic(request):
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if profile.profile_pic:
            return {
                'user_data': {
                    'profile_pic': profile.profile_pic.url
                }
            }
        return {
            'user_data': {
                'profile_pic': settings.STATIC_URL + 'img/default-profile.png'
            }
        }
    return {}