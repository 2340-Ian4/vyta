from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:id>/', views.profile, name='social.profile'),  # View a user's profile
    path('follow/<int:user_id>/', views.follow_user, name='social.follow_user'),  # Follow/unfollow a user
    path('friend/<int:user_id>/', views.add_friend, name='social.add_friend'),  # Add/remove friend
    path('feed/', views.feed, name='social.feed'),  # View the social feed
    path('search/', views.search_users, name='social.search_users'),
    path('post/create/', views.create_post, name='social.create_post'),  # Create a post
    path('post/<int:post_id>/like/', views.like_post, name='social.like_post'),  # Like/unlike a post
    path('post/<int:post_id>/comment/', views.add_comment, name='social.add_comment'),  # Add a comment
    path('report-post/', views.report_post, name='social.report_post'),
    path('delete-post/', views.delete_post, name='social.delete_post'),
]