from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import UserConnection, Post, PostReport, Like, Comment, Activity
from django.utils import timezone

@admin.register(UserConnection)
class UserConnectionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'is_friend', 'created_at')
    list_filter = ('is_friend', 'created_at')
    search_fields = ('follower__username', 'following__username')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_link', 'content_preview', 'created_at', 'is_hidden', 'reports_count', 'posting_frequency')
    list_filter = ('is_hidden', 'created_at', 'author')
    search_fields = ('content', 'author__username', 'author__email')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count', 'reports_count')
    actions = ['hide_posts', 'unhide_posts', 'delete_posts']
    
    def author_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = 'Author'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def posting_frequency(self, obj):
        return f"{obj.get_posting_frequency():.2f} posts/day"
    posting_frequency.short_description = 'Posting Frequency'
    
    def hide_posts(self, request, queryset):
        queryset.update(is_hidden=True)
    hide_posts.short_description = "Hide selected posts"
    
    def unhide_posts(self, request, queryset):
        queryset.update(is_hidden=False)
    unhide_posts.short_description = "Unhide selected posts"
    
    def delete_posts(self, request, queryset):
        queryset.delete()
    delete_posts.short_description = "Delete selected posts"
    
    fieldsets = (
        ('Post Information', {
            'fields': ('author', 'content', 'created_at', 'updated_at')
        }),
        ('Statistics', {
            'fields': ('likes_count', 'comments_count', 'reports_count')
        }),
        ('Moderation', {
            'fields': ('is_hidden',)
        }),
    )

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_link', 'reporter_link', 'reason', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'reason', 'created_at')
    search_fields = ('post__content', 'reporter__username', 'description')
    readonly_fields = ('created_at',)
    actions = ['resolve_reports', 'unresolve_reports']
    
    def post_link(self, obj):
        url = reverse('admin:social_post_change', args=[obj.post.id])
        return format_html('<a href="{}">Post #{}</a>', url, obj.post.id)
    post_link.short_description = 'Post'
    
    def reporter_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.reporter.id])
        return format_html('<a href="{}">{}</a>', url, obj.reporter.username)
    reporter_link.short_description = 'Reporter'
    
    def resolve_reports(self, request, queryset):
        queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
    resolve_reports.short_description = "Mark selected reports as resolved"
    
    def unresolve_reports(self, request, queryset):
        queryset.update(is_resolved=False, resolved_at=None, resolved_by=None)
    unresolve_reports.short_description = "Mark selected reports as unresolved"
    
    fieldsets = (
        ('Report Information', {
            'fields': ('post', 'reporter', 'reason', 'description', 'created_at')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
    )

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
