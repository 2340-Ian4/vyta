from django.contrib import admin
from .models import WorkoutStat, AchievementStat

# Register your models here.
admin.site.register(WorkoutStat)
admin.site.register(AchievementStat)
