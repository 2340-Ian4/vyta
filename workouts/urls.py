from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='workouts.index'),
    path('history/', views.history, name='workouts.history'),
    path('log/', views.log_workout, name='workouts.log_workout'),
    path('log/ajax/', views.log_workout_ajax, name='workouts.log_workout_ajax'),
    path('goal/', views.set_goal, name='workouts.set_goal'),
    path('suggestions/', views.get_suggestions, name='workouts.suggestions'),
    path('api/goal-progress/<int:goal_id>/', views.get_goal_progress, name='workouts.goal_progress'),
    path('api/goal/<int:goal_id>/', views.get_goal, name='workouts.get_goal'),
    path('api/goal/<int:goal_id>/update/', views.update_goal, name='workouts.update_goal'),
    path('api/goal/<int:goal_id>/update-progress/', views.update_goal_progress, name='workouts.update_goal_progress'),
    path('api/goal/<int:goal_id>/delete/', views.delete_goal, name='workouts.delete_goal'),
    path('api/goal/add/', views.add_goal, name='workouts.add_goal'),
    path('api/workout/<int:workout_id>/delete/', views.delete_workout, name='workouts.delete_workout'),
]