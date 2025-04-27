from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default-profile.png')
    
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
