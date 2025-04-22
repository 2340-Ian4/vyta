from django.contrib import admin
from .models import Workout, WorkoutGoal

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'date', 'duration', 'calories_burned')
    list_filter = ('user', 'date')
    search_fields = ('name', 'description', 'notes')
    date_hierarchy = 'date'

@admin.register(WorkoutGoal)
class WorkoutGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_type', 'target', 'progress', 'start_date', 'end_date')
    list_filter = ('goal_type', 'start_date', 'end_date')
    search_fields = ('user__username', 'target')
