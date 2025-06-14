# Generated by Django 5.2 on 2025-04-17 20:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bio", models.TextField(blank=True, max_length=500)),
                ("location", models.CharField(blank=True, max_length=100)),
                ("birth_date", models.DateField(blank=True, null=True)),
                (
                    "profile_pic",
                    models.ImageField(
                        default="img/default-profile.png", upload_to="profile_pics/"
                    ),
                ),
                (
                    "height",
                    models.FloatField(blank=True, help_text="Height in cm", null=True),
                ),
                (
                    "weight",
                    models.FloatField(blank=True, help_text="Weight in kg", null=True),
                ),
                (
                    "fitness_level",
                    models.CharField(
                        choices=[
                            ("beginner", "Beginner"),
                            ("intermediate", "Intermediate"),
                            ("advanced", "Advanced"),
                        ],
                        default="beginner",
                        max_length=20,
                    ),
                ),
                ("followers_count", models.PositiveIntegerField(default=0)),
                ("following_count", models.PositiveIntegerField(default=0)),
                ("workouts_completed", models.PositiveIntegerField(default=0)),
                ("calories_burned", models.PositiveIntegerField(default=0)),
                ("active_minutes", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
