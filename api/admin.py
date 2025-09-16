from django.contrib import admin,messages
from django.db.models import Sum
from .models import Group, Category, Event, Contestant, Registration, Result, GalleryImage,IndividualChampion
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ForeignKeyWidget
from .forms import EventResultForm # Import our new form
from django.urls import path,reverse
from django.shortcuts import render, redirect
from django.utils.html import format_html

class ContestantResource(resources.ModelResource):
    group = Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, 'name'))

    category = Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name'))
        
    registered_events = Field(column_name='registered_events')

    class Meta:
        model = Contestant
        fields = ('id', 'full_name', 'email', 'state', 'gender', 'group', 'category', 'course', 'phone_number', 'registered_events')
        export_order = fields

    def dehydrate_registered_events(self, contestant):
        registrations = Registration.objects.filter(contestant=contestant)
        event_names = [reg.event.name for reg in registrations]
        return ", ".join(event_names)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class EventInline(admin.TabularInline):
    model = Event
    extra = 1
    fields = ('name',) 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = [EventInline]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'add_results_button')
    list_filter = ('category',)
    search_fields = ('name',)
    autocomplete_fields = ['category']

    def get_urls(self):
        """Adds our custom URL to the admin."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/add-results/',
                self.admin_site.admin_view(self.add_results_view),
                name='event_add_results',
            ),
        ]
        return custom_urls + urls

    def add_results_button(self, obj):
        """A button that links to our custom view."""
        url = reverse('admin:event_add_results', args=[obj.pk])
        return format_html('<a class="button" href="{}">Add/Edit Results</a>', url)
    add_results_button.short_description = 'Manage Results'
    add_results_button.allow_tags = True

    def add_results_view(self, request, object_id):
        """The main view for handling our custom form."""
        event = self.get_object(request, object_id)

        if request.method == 'POST':
            form = EventResultForm(request.POST)
            if form.is_valid():
                # Get the data from the form
                data = form.cleaned_data
                result_number = data['result_number']

                # List of winners and their positions/points
                winners_data = [
                    (1, data.get('winner_1'), data.get('points_1')),
                    (2, data.get('winner_2'), data.get('points_2')),
                    (3, data.get('winner_3'), data.get('points_3')),
                ]

                # Loop through winners and save them
                for position, registration, points in winners_data:
                    if registration and points is not None:
                        Result.objects.update_or_create(
                            registration=registration,
                            defaults={
                                'position': position,
                                'points': points,
                                'resultNumber': result_number,
                            }
                        )

                self.message_user(request, "Results for {} have been saved successfully.".format(event.name), messages.SUCCESS)
                return redirect(reverse('admin:api_event_changelist'))

        else: # This is a GET request
            # Pre-populate the form with existing results for this event
            initial_data = {'event': event, 'result_number': ''}
            existing_results = Result.objects.filter(registration__event=event)

            if existing_results.exists():
                initial_data['result_number'] = existing_results.first().resultNumber

            for result in existing_results:
                if result.position in [1, 2, 3]:
                    initial_data[f'winner_{result.position}'] = result.registration
                    initial_data[f'points_{result.position}'] = result.points

            form = EventResultForm(initial=initial_data)

        context = dict(
           self.admin_site.each_context(request),
           opts=self.model._meta,
           form=form,
           event=event,
        )
        return render(request, 'admin/api/event/change_form_results.html', context)

class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 1
    autocomplete_fields = ['event']

@admin.register(Contestant)
class ContestantAdmin(ImportExportModelAdmin):
    resource_class = ContestantResource
    list_display = ('full_name', 'email', 'group', 'category', 'gender')
    list_filter = ('gender', 'group', 'category')
    search_fields = ('full_name', 'email')
    autocomplete_fields = ['group', 'category']
    inlines = [RegistrationInline]

class ResultInline(admin.TabularInline):
    model = Result
    extra = 0
    fields = ('position', 'points') 

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('contestant', 'event')
    search_fields = ('contestant__full_name', 'event__name')
    autocomplete_fields = ['contestant', 'event']
    inlines = [ResultInline]

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('get_contestant_name', 'get_event_name', 'position', 'points')
    list_filter = ('registration__event__category', 'registration__event__name', 'position')
    search_fields = ('registration__contestant__full_name',)
    autocomplete_fields = ['registration']
    list_display = ('get_contestant_name', 'get_event_name', 'position', 'points', 'resultNumber') # <-- Add here
    list_filter = ('registration__event__category', 'registration__event__name', 'position')
    search_fields = ('registration__contestant__full_name', 'resultNumber',) # <-- And also add here
    autocomplete_fields = ['registration']
    
    # It's also good practice to define the fields for the edit form
    fields = ('registration', 'position', 'points', 'resultNumber')

    @admin.display(description='Contestant')
    def get_contestant_name(self, obj):
        return obj.registration.contestant.full_name

    @admin.display(description='Event')
    def get_event_name(self, obj):
        return obj.registration.event.name

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'year', 'uploaded_at')
    list_filter = ('year',)

@admin.register(IndividualChampion)
class IndividualChampionAdmin(admin.ModelAdmin):
    # Define the columns to display
    list_display = ['full_name', 'group', 'total_points']

    def get_queryset(self, request):
        # Calculate the total points for each contestant
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            total_points=Sum('registration__result__points')
        ).order_by('-total_points')
        return queryset

    @admin.display(description='Total Points', ordering='total_points')
    def total_points(self, obj):
        # Helper to display the annotated field
        return obj.total_points

    def has_add_permission(self, request):
        # This is a read-only page, so disable the "Add" button
        return False

    def has_change_permission(self, request, obj=None):
        # Disable editing
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable deleting
        return False