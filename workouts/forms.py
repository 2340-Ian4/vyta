from django import forms
from .models import Workout, WorkoutGoal
from django.utils import timezone

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
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date and end_date < timezone.now().date():
            raise forms.ValidationError("End date cannot be in the past")
        return end_date 