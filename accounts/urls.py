from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='accounts.login'),
    path('signup/', views.signup, name='accounts.signup'),
    path('logout/', views.logout, name='accounts.logout'),
    path('about/', views.about, name='accounts.about'),
    path('profile-setup/', views.profile_setup, name='accounts.profile_setup'),
]