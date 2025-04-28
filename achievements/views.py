from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum, Count, F, Value, IntegerField
from django.db.models.functions import Coalesce
from .models import LeaderboardEntry, LeaderboardType
from user.models import UserProfile, Badge, UserBadge
from workouts.models import Workout
import logging
from django.db import models

logger = logging.getLogger(__name__)

def award_weekly_champion_badges(week_start, user_profile, leaderboard_type):
    """Award weekly champion badges to the top user in each leaderboard type"""
    # Only award badges for previous weeks (not the current week)
    today = timezone.localtime(timezone.now()).date()
    if week_start >= today:
        logger.info(f"Skipping badge award for current week {week_start}")
        return
        
    # Get the top user for this leaderboard type
    top_entry = LeaderboardEntry.objects.filter(
        week_start=week_start,
        leaderboard_type=leaderboard_type,
        user__profile__fitness_level=user_profile.fitness_level
    ).order_by('-score').first()
    
    if top_entry and top_entry.user == user_profile.user:
        # Get the corresponding badge
        badge_name = f"Weekly Champion - {leaderboard_type.replace('_', ' ').title()}"
        badge = Badge.objects.filter(name=badge_name).first()
        
        if badge and not UserBadge.objects.filter(user_profile=user_profile, badge=badge).exists():
            UserBadge.objects.create(user_profile=user_profile, badge=badge)
            logger.info(f"Awarded {badge_name} to {user_profile.user.username} for week of {week_start}")
            
            # Update the badges collected leaderboard
            badge_count = UserBadge.objects.filter(user_profile=user_profile).count()
            LeaderboardEntry.objects.update_or_create(
                user=user_profile.user,
                leaderboard_type=LeaderboardType.BADGES_COLLECTED,
                week_start=week_start,
                defaults={
                    'score': badge_count,
                    'rank': 0  # Will be updated after sorting
                }
            )

def check_weekly_milestones(user_profile, week_start, today):
    """Check and award milestone badges for weekly achievements"""
    # Get weekly stats
    workout_stats = Workout.objects.filter(
        user=user_profile.user,
        date__date__gte=week_start,
        date__date__lte=today
    ).aggregate(
        total_calories=Coalesce(Sum('calories_burned'), Value(0), output_field=IntegerField()),
        total_workouts=Count('id'),
        total_minutes=Coalesce(Sum('duration'), Value(0), output_field=IntegerField())
    )
    
    # Check calorie milestone
    if workout_stats['total_calories'] >= 1000:
        badge = Badge.objects.filter(name="Calorie Crusher").first()
        if badge and not UserBadge.objects.filter(user_profile=user_profile, badge=badge).exists():
            UserBadge.objects.create(user_profile=user_profile, badge=badge)
            logger.info(f"Awarded Calorie Crusher to {user_profile.user.username}")
    
    # Check workout milestone
    if workout_stats['total_workouts'] >= 5:
        badge = Badge.objects.filter(name="Workout Warrior").first()
        if badge and not UserBadge.objects.filter(user_profile=user_profile, badge=badge).exists():
            UserBadge.objects.create(user_profile=user_profile, badge=badge)
            logger.info(f"Awarded Workout Warrior to {user_profile.user.username}")
    
    # Check active minutes milestone
    if workout_stats['total_minutes'] >= 300:
        badge = Badge.objects.filter(name="Time Master").first()
        if badge and not UserBadge.objects.filter(user_profile=user_profile, badge=badge).exists():
            UserBadge.objects.create(user_profile=user_profile, badge=badge)
            logger.info(f"Awarded Time Master to {user_profile.user.username}")

def index(request):
    # Get the start of the current week (Monday)
    today = timezone.localtime(timezone.now()).date()
    week_start = today - timedelta(days=today.weekday())
    
    logger.info(f"Current date: {today}")
    logger.info(f"Fetching leaderboard data for week of {week_start}")
    
    # Get user's fitness level
    user_profile = UserProfile.objects.get(user=request.user)
    user_fitness_level = user_profile.fitness_level
    
    logger.info(f"User fitness level: {user_fitness_level}")
    
    # Get all users with the same fitness level
    users = UserProfile.objects.filter(fitness_level=user_fitness_level)
    
    # Calculate this week's statistics for each user
    for profile in users:
        # Calculate this week's statistics
        workout_stats = Workout.objects.filter(
            user=profile.user,
            date__date__gte=week_start,
            date__date__lte=today
        ).aggregate(
            total_workouts=Count('id'),
            total_calories=Coalesce(Sum('calories_burned'), Value(0), output_field=IntegerField()),
            total_minutes=Coalesce(Sum('duration'), Value(0), output_field=IntegerField())
        )
        
        # Calculate total badges
        badge_count = UserBadge.objects.filter(user_profile=profile).count()
        
        logger.info(f"User {profile.user.username} stats: {workout_stats}, badges: {badge_count}")
        
        # Update leaderboard entries with this week's statistics
        LeaderboardEntry.objects.update_or_create(
            user=profile.user,
            leaderboard_type=LeaderboardType.CALORIES_BURNED,
            week_start=week_start,
            defaults={
                'score': workout_stats['total_calories'],
                'rank': 0  # Will be updated after sorting
            }
        )
        
        LeaderboardEntry.objects.update_or_create(
            user=profile.user,
            leaderboard_type=LeaderboardType.ACTIVE_MINUTES,
            week_start=week_start,
            defaults={
                'score': workout_stats['total_minutes'],
                'rank': 0  # Will be updated after sorting
            }
        )
        
        LeaderboardEntry.objects.update_or_create(
            user=profile.user,
            leaderboard_type=LeaderboardType.WORKOUTS_COMPLETED,
            week_start=week_start,
            defaults={
                'score': workout_stats['total_workouts'],
                'rank': 0  # Will be updated after sorting
            }
        )
        
        LeaderboardEntry.objects.update_or_create(
            user=profile.user,
            leaderboard_type=LeaderboardType.BADGES_COLLECTED,
            week_start=week_start,
            defaults={
                'score': badge_count,
                'rank': 0  # Will be updated after sorting
            }
        )
    
    # Get all leaderboard entries for the current week and user's fitness level
    entries = LeaderboardEntry.objects.filter(
        week_start=week_start,
        user__profile__fitness_level=user_fitness_level
    ).select_related('user', 'user__profile')
    
    # Sort and rank entries for each leaderboard type
    for lb_type in LeaderboardType.choices:
        leaderboard_type = lb_type[0]
        type_entries = entries.filter(leaderboard_type=leaderboard_type).order_by('-score')
        
        # Update ranks
        for rank, entry in enumerate(type_entries, 1):
            entry.rank = rank
            entry.save()
            
            # Award weekly champion badges
            if rank == 1:
                award_weekly_champion_badges(week_start, entry.user.profile, leaderboard_type)
    
    # Check weekly milestones for the current user
    check_weekly_milestones(user_profile, week_start, today)
    
    # Get updated entries with new ranks
    entries = LeaderboardEntry.objects.filter(
        week_start=week_start,
        user__profile__fitness_level=user_fitness_level
    ).select_related('user', 'user__profile')
    
    logger.info(f"Found {entries.count()} leaderboard entries")
    
    # Log each entry for debugging
    for entry in entries:
        logger.info(f"Entry: {entry.user.username} - {entry.leaderboard_type} - Score: {entry.score} - Rank: {entry.rank}")
    
    # Get user's recent badges
    recent_badges = UserBadge.objects.filter(
        user_profile=user_profile
    ).select_related('badge').order_by('-earned_at')[:5]
    
    context = {
        'leaderboard_types': LeaderboardType.choices,
        'user_fitness_level': user_fitness_level,
        'leaderboards': entries,
        'recent_badges': recent_badges,
    }
    
    return render(request, 'achievements/index.html', context)

def badges(request):
    # Get all badges and user's earned badges
    user_profile = UserProfile.objects.get(user=request.user)
    earned_badges = UserBadge.objects.filter(user_profile=user_profile).select_related('badge')
    
    # Get all badges that have valid requirements
    all_badges = Badge.objects.filter(
        requirement_type__in=['workouts_completed', 'calories_burned', 'active_minutes', 'streak_days', 'special']
    ).distinct()
    
    # Create a list of badges with earned status and progress
    badges_with_status = []
    for badge in all_badges:
        earned = earned_badges.filter(badge=badge).exists()
        
        # Calculate progress for unearned badges
        progress = 0
        if not earned:
            if badge.requirement_type == 'workouts_completed':
                progress = min(100, (user_profile.workouts_completed / badge.requirement_value) * 100)
            elif badge.requirement_type == 'calories_burned':
                progress = min(100, (user_profile.calories_burned / badge.requirement_value) * 100)
            elif badge.requirement_type == 'active_minutes':
                progress = min(100, (user_profile.active_minutes / badge.requirement_value) * 100)
            elif badge.requirement_type == 'streak_days':
                progress = min(100, (user_profile.streak_days / badge.requirement_value) * 100)
        
        badges_with_status.append({
            'name': badge.name,
            'description': badge.description,
            'icon': badge.icon,
            'earned': earned,
            'earned_at': earned_badges.get(badge=badge).earned_at if earned else None,
            'requirement_type': badge.requirement_type,
            'requirement_value': badge.requirement_value,
            'progress': progress
        })
    
    return render(request, 'achievements/badges.html', {'all_badges': badges_with_status})

# Create your views here.
