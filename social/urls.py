from django.urls import path
from . import views

urlpatterns = [
    # Profile-related URLs have been moved to the profiles app
    path('feed/', views.feed, name='social.feed'),  # View the social feed
]