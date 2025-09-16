# in forms.py (new file)

from django import forms
from .models import Event, Registration

class EventResultForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        # --- ADD THIS WIDGET ---
        widget=forms.HiddenInput()
    )

    # Fields for 1st Place
    winner_1 = forms.ModelChoiceField(queryset=Registration.objects.none(), label="1st Place Winner")
    points_1 = forms.IntegerField(label="1st Place Points")

    # Fields for 2nd Place
    winner_2 = forms.ModelChoiceField(queryset=Registration.objects.none(), label="2nd Place Winner", required=False)
    points_2 = forms.IntegerField(label="2nd Place Points", required=False)

    # Fields for 3rd Place
    winner_3 = forms.ModelChoiceField(queryset=Registration.objects.none(), label="3rd Place Winner", required=False)
    points_3 = forms.IntegerField(label="3rd Place Points", required=False)

    # Field for the shared Result Number
    result_number = forms.CharField(label="Result Number", max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'event' in self.data:
            try:
                event_id = int(self.data.get('event'))
                registrations_queryset = Registration.objects.filter(event_id=event_id)
                self.fields['winner_1'].queryset = registrations_queryset
                self.fields['winner_2'].queryset = registrations_queryset
                self.fields['winner_3'].queryset = registrations_queryset
            except (ValueError, TypeError):
                pass