from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fa-medal')  # Font Awesome icon class
    requirement_type = models.CharField(max_length=50, choices=[
        ('workouts_completed', 'Workouts Completed'),
        ('calories_burned', 'Calories Burned'),
        ('active_minutes', 'Active Minutes'),
        ('streak_days', 'Streak Days'),
        ('special', 'Special Achievement')
    ])
    requirement_value = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['requirement_type', 'requirement_value']

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default-profile.png')
    
    # Profile completion status
    is_profile_complete = models.BooleanField(default=False)
    
    # Ban related fields
    is_banned = models.BooleanField(default=False)
    ban_start_date = models.DateTimeField(null=True, blank=True)
    ban_duration_days = models.PositiveIntegerField(default=0)
    
    # Fitness specific data
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    fitness_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='beginner')
    
    # Social stats
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    allow_following = models.BooleanField(default=True)
    
    # Fitness stats
    workouts_completed = models.PositiveIntegerField(default=0)
    calories_burned = models.PositiveIntegerField(default=0)
    active_minutes = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)
    last_workout_date = models.DateField(null=True, blank=True)
    
    # Badge related
    badges = models.ManyToManyField(Badge, through='UserBadge')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
        
    def get_ban_remaining_days(self):
        if not self.is_banned or not self.ban_start_date:
            return 0
        ban_end_date = self.ban_start_date + timedelta(days=self.ban_duration_days)
        if timezone.now() > ban_end_date:
            self.is_banned = False
            self.ban_start_date = None
            self.ban_duration_days = 0
            self.save()
            return 0
        return (ban_end_date - timezone.now()).days

    def check_and_award_badges(self):
        """Check if user qualifies for any new badges based on their stats"""
        # Get all badges that haven't been earned yet
        earned_badges = self.badges.all()
        available_badges = Badge.objects.exclude(id__in=earned_badges)
        
        for badge in available_badges:
            should_award = False
            
            if badge.requirement_type == 'workouts_completed':
                should_award = self.workouts_completed >= badge.requirement_value
            elif badge.requirement_type == 'calories_burned':
                should_award = self.calories_burned >= badge.requirement_value
            elif badge.requirement_type == 'active_minutes':
                should_award = self.active_minutes >= badge.requirement_value
            elif badge.requirement_type == 'streak_days':
                should_award = self.streak_days >= badge.requirement_value
            elif badge.requirement_type == 'special':
                # Special badges are awarded through other means (e.g., weekly champions)
                continue
            
            if should_award:
                UserBadge.objects.create(user_profile=self, badge=badge)
                logger.info(f"Awarded {badge.name} to {self.user.username}")

class UserBadge(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user_profile', 'badge']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.badge.name}"

class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('complaint', 'Complaint'),
        ('feedback', 'General Feedback'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    type = models.CharField(max_length=20, choices=COMPLAINT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    admin_response = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.get_type_display()})"
