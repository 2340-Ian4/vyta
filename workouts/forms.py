from django import forms
from .models import Workout, WorkoutGoal

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'description', 'duration', 'calories_burned', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'duration': forms.NumberInput(attrs={'min': 1}),
            'calories_burned': forms.NumberInput(attrs={'min': 0}),
        }

class WorkoutGoalForm(forms.ModelForm):
    class Meta:
        model = WorkoutGoal
        fields = ['goal_type', 'target', 'end_date', 'progress']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        } 