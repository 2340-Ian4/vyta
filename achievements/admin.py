from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import LeaderboardEntry

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'leaderboard_type', 'score', 'rank', 'week_start')
    list_filter = ('leaderboard_type', 'week_start')
    search_fields = ('user__username', 'user__email')
    ordering = ('-week_start', 'rank')
    date_hierarchy = 'week_start'

    def get_queryset(self, request):
        # Get the base queryset
        qs = super().get_queryset(request)
        
        # Calculate the date 5 weeks ago
        five_weeks_ago = timezone.now().date() - timedelta(weeks=5)
        
        # Filter to show only current and past 5 weeks, and top 10 ranks per week
        return qs.filter(week_start__gte=five_weeks_ago).extra(
            where=['rank <= 10']
        ).order_by('-week_start', 'rank')
