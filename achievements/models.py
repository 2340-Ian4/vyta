from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class LeaderboardType(models.TextChoices):
    CALORIES_BURNED = 'calories_burned', 'Calories Burned'
    BADGES_COLLECTED = 'badges_collected', 'Badges Collected'
    ACTIVE_MINUTES = 'active_minutes', 'Active Minutes'
    WORKOUTS_COMPLETED = 'workouts_completed', 'Workouts Completed'

class LeaderboardEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leaderboard_type = models.CharField(
        max_length=20,
        choices=LeaderboardType.choices,
        default=LeaderboardType.CALORIES_BURNED
    )
    score = models.IntegerField(default=0)
    rank = models.IntegerField()
    week_start = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'leaderboard_type', 'week_start']
        ordering = ['-week_start', 'rank']

    def __str__(self):
        return f"{self.user.username} - {self.leaderboard_type} - Week of {self.week_start}"
