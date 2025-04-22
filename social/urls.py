from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:id>/', views.profile, name='social.profile'),  # View a user's profile
    path('follow/<int:id>/', views.follow, name='social.follow'),    # Follow a user
    path('unfollow/<int:id>/', views.unfollow, name='social.unfollow'),  # Unfollow a user
    path('feed/', views.feed, name='social.feed'),                   # View the social feed
    path('post/create/', views.create_post, name='social.create_post'),
    path('friend/add/<int:id>/', views.add_friend, name='social.add_friend'),
    path('friend/remove/<int:id>/', views.remove_friend, name='social.remove_friend'),
    path('post/<int:post_id>/like/', views.like_post, name='social.like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='social.add_comment'),
    # Profile-related URLs have been moved to the profiles app
    path('feed/', views.feed, name='social.feed'),  # View the social feed
    path('follow/<int:user_id>/', views.follow_user, name='social.follow_user'),  # Follow/unfollow a user
    path('friend/<int:user_id>/', views.add_friend, name='social.add_friend'),  # Add/remove friend
    path('feed/', views.feed, name='social.feed'),  # View the social feed
    path('search/', views.search_users, name='social.search_users'),
    path('post/create/', views.create_post, name='social.create_post'),  # Create a post
    path('post/<int:post_id>/like/', views.like_post, name='social.like_post'),  # Like/unlike a post
    path('post/<int:post_id>/comment/', views.add_comment, name='social.add_comment'),  # Add a comment
]