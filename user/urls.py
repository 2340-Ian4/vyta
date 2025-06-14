from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='user.index'),
    path('profile/update/', views.update_profile, name='user.update_profile'),
    path('profile/update-picture/', views.update_profile_picture, name='user.update_picture'),
    path('profile/remove-picture/', views.remove_profile_picture, name='user.remove_picture'),
    path('profile/<str:username>/', views.profile, name='user.profile'),
    path('profile/', views.profile, name='user.profile'),
    path('update-username/', views.update_username, name='user.update_username'),
    path('update-goals/', views.update_goals, name='user.update_goals'),
    path('submit-complaint/', views.submit_complaint, name='user.submit_complaint'),
]