from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count

class UserConnection(models.Model):
    """Model for tracking user relationships (following/friends)"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    is_friend = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class Post(models.Model):
    """Model for social posts"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    media = models.ImageField(upload_to='post_media/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    reports_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_hidden']),
            models.Index(fields=['reports_count']),
        ]

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"
        
    def get_posting_frequency(self):
        """Calculate the average number of posts per day for the author"""
        # Get all posts by this author
        author_posts = Post.objects.filter(author=self.author)
        if not author_posts.exists():
            return 0
            
        # Get the date of the first post
        first_post_date = author_posts.earliest('created_at').created_at
        days_since_first_post = (timezone.now() - first_post_date).days or 1  # Avoid division by zero
        
        # Calculate average posts per day
        return author_posts.count() / days_since_first_post
        
    def is_liked_by(self, user):
        """Check if a post is liked by a specific user"""
        return self.likes.filter(user=user).exists()
        
    @property
    def is_liked(self):
        """Property to check if the post is liked by the current user"""
        from django.contrib.auth.models import AnonymousUser
        if not hasattr(self, '_current_user'):
            return False
        return self.is_liked_by(self._current_user)

class PostReport(models.Model):
    """Model for post reports"""
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('violence', 'Violence'),
        ('other', 'Other'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='resolved_reports')
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['reporter']),
            models.Index(fields=['reason']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Report on post {self.post.id} by {self.reporter.username}"
        
    def save(self, *args, **kwargs):
        # Update the post's reports count
        if not self.is_resolved:
            self.post.reports_count = self.post.reports.filter(is_resolved=False).count() + 1
            self.post.save()
        super().save(*args, **kwargs)

class Like(models.Model):
    """Model for post likes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f"{self.user.username} likes post {self.post.id}"

class Comment(models.Model):
    """Model for post comments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"

class Activity(models.Model):
    """Model for tracking user activities (workouts, achievements)"""
    ACTIVITY_TYPES = [
        ('workout', 'Workout'),
        ('achievement', 'Achievement'),
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('like', 'Like'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content_id = models.PositiveIntegerField()  # ID of the related content (workout, achievement, post, etc.)
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True)  # Additional activity-specific details

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.activity_type} at {self.created_at}"
