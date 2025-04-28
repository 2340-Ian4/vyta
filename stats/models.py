from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class WorkoutStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_stats')
    date = models.DateField(default=timezone.now)
    duration = models.IntegerField(help_text="Duration in minutes", null=True, blank=True, default=0)
    calories_burned = models.IntegerField(null=True, blank=True, default=0)
    workout_type = models.CharField(max_length=50, null=True, blank=True, default='General')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.workout_type}"

class AchievementStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievement_stats')
    achievement_name = models.CharField(max_length=100)
    progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.achievement_name}"
