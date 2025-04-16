from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='workouts.index'),
    path('history/', views.history, name='workouts.history'),
]