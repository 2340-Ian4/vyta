from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='achievements.index'),  # Main achievements page
    path('badges/', views.badges, name='achievements.badges'),  # Badges page
]