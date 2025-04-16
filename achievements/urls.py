from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='achievements.index'),
    path('badges/', views.badges, name='achievements.badges'),
]