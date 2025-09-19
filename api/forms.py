# In api/forms.py
from django import forms
from .models import Registration, Event, Contestant

class EventResultForm(forms.Form):
    winner_1 = forms.ModelChoiceField(queryset=Registration.objects.none(), required=False, label="Winner 1st Place")
    points_1 = forms.IntegerField(required=False, label="Points for 1st")

    winner_2 = forms.ModelChoiceField(queryset=Registration.objects.none(), required=False, label="Winner 2nd Place")
    points_2 = forms.IntegerField(required=False, label="Points for 2nd")

    winner_3 = forms.ModelChoiceField(queryset=Registration.objects.none(), required=False, label="Winner 3rd Place")
    points_3 = forms.IntegerField(required=False, label="Points for 3rd")

    result_number = forms.CharField(max_length=100, required=False, label="Result Number")

    def __init__(self, *args, **kwargs):
        # Get the event object passed from the admin view
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

        if event:
            # This is the single source of truth for our queryset
            registrations = Registration.objects.filter(event=event).select_related('contestant', 'contestant__category')

            # Apply this queryset to all three winner dropdowns
            for i in range(1, 4):
                self.fields[f'winner_{i}'].queryset = registrations
                # Customize the display to show the contestant's name and their category
                self.fields[f'winner_{i}'].label_from_instance = (
                    lambda obj: f"{obj.contestant.full_name} ({obj.contestant.category.name})"
                )