from django.contrib import admin
from django.db.models import Sum
from .models import Group, Category, Event, Contestant, Registration, Result, GalleryImage,IndividualChampion
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ForeignKeyWidget

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
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    autocomplete_fields = ['category']

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