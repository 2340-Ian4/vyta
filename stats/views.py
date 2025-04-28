from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDay
from datetime import datetime, timedelta
from workouts.models import Workout
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    # Get the date range for the last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # Get all workouts for the user in the date range
    workouts = Workout.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Format workout frequency data (monthly)
    workout_frequency = (
        workouts
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Get workout types distribution (using name field)
    workout_types = (
        workouts
        .values('name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    
    # Get calories burned data (daily)
    calories_data = (
        workouts
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(total_calories=Sum('calories_burned'))
        .order_by('day')
    )
    
    # Get active minutes data (daily)
    active_minutes = (
        workouts
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(total_minutes=Sum('duration'))
        .order_by('day')
    )

    # Check if we have any data at all
    total_workouts = workouts.count()
    has_data = total_workouts > 0
    
    # Format all data into a single dictionary
    workout_data = {
        'workouts_per_month': {
            'labels': [entry['month'].strftime('%B %Y') for entry in workout_frequency],
            'data': [entry['count'] for entry in workout_frequency]
        },
        'workout_types': {
            'labels': [entry['name'] for entry in workout_types],
            'data': [entry['count'] for entry in workout_types]
        },
        'calories_data': {
            'labels': [entry['day'].strftime('%b %d') for entry in calories_data],
            'data': [float(entry['total_calories'] or 0) for entry in calories_data]
        },
        'active_minutes': {
            'labels': [entry['day'].strftime('%b %d') for entry in active_minutes],
            'data': [float(entry['total_minutes'] or 0) for entry in active_minutes]
        }
    }
    
    context = {
        'workout_data': workout_data,
        'has_data': has_data,
        'total_workouts': total_workouts
    }

    return render(request, 'stats/index.html', context)
