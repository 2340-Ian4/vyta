from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='workouts.index'),
    path('history/', views.history, name='workouts.history'),
    path('log/', views.log_workout, name='workouts.log'),
    path('goal/', views.set_goal, name='workouts.goal'),
]