from django.contrib import admin
from .models import UserConnection, Post, Like, Comment, Activity

@admin.register(UserConnection)
class UserConnectionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'is_friend', 'created_at')
    list_filter = ('is_friend', 'created_at')
    search_fields = ('follower__username', 'following__username')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at', 'likes_count', 'comments_count')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'content')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content', 'content')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'content_id', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'details')
