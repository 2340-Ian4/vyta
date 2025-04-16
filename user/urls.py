from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='user.index'),
    path('lifetime-stats/', views.lifetime_stats, name='user.lifetime_stats'),
]