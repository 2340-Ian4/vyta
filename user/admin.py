from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Complaint, Badge, UserBadge

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'requirement_type', 'requirement_value', 'created_at')
    list_filter = ('requirement_type',)
    search_fields = ('name', 'description')
    ordering = ('requirement_type', 'requirement_value')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'badge', 'earned_at')
    list_filter = ('badge', 'earned_at')
    search_fields = ('user_profile__user__username', 'badge__name')
    date_hierarchy = 'earned_at'

class UserBadgeInline(admin.TabularInline):
    model = UserBadge
    extra = 0
    readonly_fields = ('earned_at',)
    can_delete = False

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('User Information', {
            'fields': ('bio', 'location', 'birth_date', 'profile_pic')
        }),
        ('Ban Management', {
            'fields': ('is_banned', 'ban_start_date', 'ban_duration_days'),
            'classes': ('collapse',)
        }),
        ('Fitness Data', {
            'fields': ('height', 'weight', 'fitness_level')
        }),
        ('Social Stats', {
            'fields': ('followers_count', 'following_count', 'allow_following')
        }),
        ('Fitness Stats', {
            'fields': ('workouts_completed', 'calories_burned', 'active_minutes', 'streak_days', 'last_workout_date')
        }),
    )

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_banned')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__is_banned')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__bio')
    
    def get_is_banned(self, obj):
        return obj.profile.is_banned if hasattr(obj, 'profile') else False
    get_is_banned.boolean = True
    get_is_banned.short_description = 'Banned'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register UserProfile separately for direct access
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_banned', 'workouts_completed', 'calories_burned', 'active_minutes', 'streak_days')
    list_filter = ('is_banned', 'fitness_level')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('ban_start_date',)
    inlines = [UserBadgeInline]
    
    def get_ban_remaining_days(self, obj):
        return obj.get_ban_remaining_days()
    get_ban_remaining_days.short_description = 'Remaining Ban Days'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'location', 'birth_date', 'profile_pic')
        }),
        ('Ban Management', {
            'fields': ('is_banned', 'ban_start_date', 'ban_duration_days'),
            'classes': ('collapse',)
        }),
        ('Fitness Data', {
            'fields': ('height', 'weight', 'fitness_level')
        }),
        ('Social Stats', {
            'fields': ('followers_count', 'following_count', 'allow_following')
        }),
        ('Fitness Stats', {
            'fields': ('workouts_completed', 'calories_burned', 'active_minutes', 'streak_days', 'last_workout_date')
        }),
    )
    actions = ['check_and_award_badges']

    def check_and_award_badges(self, request, queryset):
        for profile in queryset:
            profile.check_and_award_badges()
    check_and_award_badges.short_description = "Check and award badges for selected users"

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'status', 'created_at', 'updated_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'type', 'title', 'description')
        }),
        ('Status Information', {
            'fields': ('status', 'admin_response')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_resolved', 'mark_as_closed']

    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_as_resolved.short_description = "Mark selected complaints as resolved"

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_as_closed.short_description = "Mark selected complaints as closed"
