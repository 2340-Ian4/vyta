from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='user.index'),
    path('lifetime-stats/', views.lifetime_stats, name='user.lifetime_stats'),
    path('profile/', views.profile, name='user.profile'),  # Current user's profile
    path('profile/<str:username>/', views.profile, name='user.profile.other'),  # Another user's profile
    path('upload-profile-pic/', views.upload_profile_pic, name='user.upload_profile_pic'),  # Profile picture upload
]