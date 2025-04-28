from django.db import migrations

def create_initial_badges(apps, schema_editor):
    Badge = apps.get_model('user', 'Badge')
    
    # Weekly leaderboard badges
    Badge.objects.create(
        name="Weekly Champion - Calories",
        description="Won the weekly calories burned leaderboard",
        icon="fa-fire",
        requirement_type="special",
        requirement_value=0
    )
    
    Badge.objects.create(
        name="Weekly Champion - Workouts",
        description="Won the weekly workouts completed leaderboard",
        icon="fa-dumbbell",
        requirement_type="special",
        requirement_value=0
    )
    
    Badge.objects.create(
        name="Weekly Champion - Active Minutes",
        description="Won the weekly active minutes leaderboard",
        icon="fa-clock",
        requirement_type="special",
        requirement_value=0
    )
    
    # Milestone badges
    Badge.objects.create(
        name="Calorie Crusher",
        description="Burned 1,000 calories in a week",
        icon="fa-fire",
        requirement_type="calories_burned",
        requirement_value=1000
    )
    
    Badge.objects.create(
        name="Workout Warrior",
        description="Completed 5 workouts in a week",
        icon="fa-dumbbell",
        requirement_type="workouts_completed",
        requirement_value=5
    )
    
    Badge.objects.create(
        name="Time Master",
        description="Accumulated 300 active minutes in a week",
        icon="fa-clock",
        requirement_type="active_minutes",
        requirement_value=300
    )

def remove_initial_badges(apps, schema_editor):
    Badge = apps.get_model('user', 'Badge')
    Badge.objects.filter(
        name__in=[
            "Weekly Champion - Calories",
            "Weekly Champion - Workouts",
            "Weekly Champion - Active Minutes",
            "Calorie Crusher",
            "Workout Warrior",
            "Time Master"
        ]
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('user', '0006_badge_userprofile_last_workout_date_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_badges, remove_initial_badges),
    ] 