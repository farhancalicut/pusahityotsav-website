# In api/forms.py
from django import forms
from django.forms import formset_factory
from .models import Registration, Event, Contestant, Result

class EventResultForm(forms.Form):
    result_number = forms.CharField(
        max_length=100, 
        required=True, 
        label="Result Number",
        help_text="This will be the same for all positions in this event"
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        self.event = event
        
        if event:
            # Get all registrations for this event
            registrations = Registration.objects.filter(event=event).select_related(
                'contestant', 'contestant__group', 'contestant__category'
            ).order_by('contestant__full_name')
            
            # Create dynamic fields for each position
            for position in [1, 2, 3]:
                # Multiple winner selection for tied positions
                self.fields[f'winners_{position}'] = forms.ModelMultipleChoiceField(
                    queryset=registrations,
                    required=False,
                    label=f"Position {position} Winners",
                    help_text=f"Select one or more winners for {position} position (for tied positions)",
                    widget=forms.CheckboxSelectMultiple
                )
                
                # Points for this position
                self.fields[f'points_{position}'] = forms.IntegerField(
                    required=False,
                    label=f"Points for Position {position}",
                    min_value=0,
                    initial=0
                )
            
            # Add non-poster participants section
            self.fields['non_poster_participants'] = forms.ModelMultipleChoiceField(
                queryset=registrations,
                required=False,
                label="Non-Poster Participants",
                help_text="Students who participated and earned points but won't appear on posters",
                widget=forms.CheckboxSelectMultiple
            )
            
            self.fields['non_poster_points'] = forms.IntegerField(
                required=False,
                label="Points for Non-Poster Participants",
                min_value=0,
                initial=0,
                help_text="Points to award each non-poster participant"
            )
            
            # Customize the display 
            for field_name in self.fields:
                if 'winners_' in field_name or field_name == 'non_poster_participants':
                    self.fields[field_name].label_from_instance = self._format_contestant_display
    
    def _format_contestant_display(self, registration):
        """Format how contestants appear in the selection lists"""
        contestant = registration.contestant
        return f"{contestant.full_name} ({contestant.group.name}) - {contestant.category.name}"
    
    def clean(self):
        cleaned_data = super().clean()
        result_number = cleaned_data.get('result_number')
        
        if not result_number:
            raise forms.ValidationError("Result number is required.")
        
        # Collect all selected registrations to check for duplicates
        all_selected_registrations = []
        has_winners = False
        
        # Validate that at least one winner is selected
        for position in [1, 2, 3]:
            winners = cleaned_data.get(f'winners_{position}')
            if winners:
                has_winners = True
                all_selected_registrations.extend(winners)
                # Ensure points are provided for positions with winners
                points = cleaned_data.get(f'points_{position}')
                if points is None or points < 0:
                    raise forms.ValidationError(f"Please provide valid points for position {position}")
        
        # Check non-poster participants
        non_poster = cleaned_data.get('non_poster_participants')
        if non_poster:
            has_winners = True
            all_selected_registrations.extend(non_poster)
            points = cleaned_data.get('non_poster_points')
            if points is None or points < 0:
                raise forms.ValidationError("Please provide valid points for non-poster participants")
        
        # Check for duplicate registrations across all fields
        seen_registrations = set()
        duplicate_registrations = set()
        for registration in all_selected_registrations:
            if registration in seen_registrations:
                duplicate_registrations.add(registration)
            seen_registrations.add(registration)
        
        if duplicate_registrations:
            duplicate_names = [reg.contestant.full_name for reg in duplicate_registrations]
            raise forms.ValidationError(
                f"The following participants are selected in multiple positions: {', '.join(duplicate_names)}. "
                "Each participant can only be assigned to one position per event."
            )
        
        if not has_winners:
            raise forms.ValidationError("Please select at least one winner or participant.")
            
        return cleaned_data