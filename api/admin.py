from django.contrib import admin
from .models import Group, Category, Event, Contestant, Registration, Result, GalleryImage
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

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