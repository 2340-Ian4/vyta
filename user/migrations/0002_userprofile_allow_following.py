# Generated by Django 5.2 on 2025-04-27 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='allow_following',
            field=models.BooleanField(default=True),
        ),
    ]
