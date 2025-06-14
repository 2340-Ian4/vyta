from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text='Duration in minutes')
    date = models.DateTimeField(default=timezone.now)
    calories_burned = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.date.strftime('%Y-%m-%d')}"

class WorkoutGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_goals')
    goal_type = models.CharField(max_length=50, choices=[
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance'),
        ('flexibility', 'Flexibility'),
        ('general_fitness', 'General Fitness')
    ])
    target = models.CharField(max_length=100)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    progress = models.IntegerField(default=0, help_text='Progress percentage')
    
    def __str__(self):
        return f"{self.user.username}'s {self.goal_type} goal"

class WorkoutSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_suggestions')
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    calories = models.IntegerField(help_text="Estimated calories burned")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} for {self.user.username}"
