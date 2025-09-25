# In api/admin.py
from django.contrib import admin, messages
from django.db.models import Sum
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.utils.html import format_html

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

from .models import (
    Group, Category, Event, Contestant, Registration, Result, GalleryImage, CarouselImage, IndividualChampion
)
from .forms import EventResultForm # Import the one correct form

# --- Import/Export Resource ---
class ContestantResource(resources.ModelResource):
    group = Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, 'name'))

    category = Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name'))
        
    registered_events = Field(
        column_name='registered_events',
        attribute='registered_events',
        readonly=True  # This field is not directly mapped to a model field
    )

    class Meta:
        model = Contestant
        fields = ('id', 'full_name', 'email', 'state', 'gender', 'group', 'category', 'course', 'phone_number', 'registered_events')
        export_order = fields

    def dehydrate_registered_events(self, contestant):
        registrations = Registration.objects.filter(contestant=contestant)
        event_names = [reg.event.name for reg in registrations]
        return ", ".join(event_names)

    def before_import_row(self, row, **kwargs):
        """Process registered_events during import"""
        full_name = row.get('full_name', 'Unknown')
        print(f"=== IMPORTING: {full_name} ===")
        
        # Store registered_events for later processing
        if 'registered_events' in row:
            self._registered_events = row.get('registered_events', '').strip()
            print(f"Registered events: '{self._registered_events}'")
        else:
            self._registered_events = ''
        
        # Check if Group and Category exist
        group_name = row.get('group', '').strip()
        category_name = row.get('category', '').strip()
        
        if group_name:
            if Group.objects.filter(name=group_name).exists():
                print(f"✓ Group found: '{group_name}'")
            else:
                print(f"✗ Group NOT found: '{group_name}'")
                print(f"Available groups: {list(Group.objects.values_list('name', flat=True))}")
        
        if category_name:
            if Category.objects.filter(name=category_name).exists():
                print(f"✓ Category found: '{category_name}'")
            else:
                print(f"✗ Category NOT found: '{category_name}'")
                print(f"Available categories: {list(Category.objects.values_list('name', flat=True))}")
        
        return super().before_import_row(row, **kwargs)
    
    def before_save_instance(self, instance, *args, **kwargs):
        """Debug before saving the contestant"""
        # Extract parameters from args/kwargs to handle different django-import-export versions
        using_transactions = kwargs.get('using_transactions', args[0] if args else True)
        dry_run = kwargs.get('dry_run', args[1] if len(args) > 1 else False)
        
        print(f"=== BEFORE SAVE INSTANCE ===")
        print(f"Instance: {instance}")
        print(f"Full name: {instance.full_name}")
        print(f"Email: {instance.email}")
        print(f"Group: {instance.group}")
        print(f"Category: {instance.category}")
        print(f"Dry run: {dry_run}")
        
        # Check for potential issues
        if not instance.full_name:
            print(f"⚠️ WARNING: Empty full_name!")
        if not instance.email:
            print(f"⚠️ WARNING: Empty email!")
        if not instance.group:
            print(f"⚠️ WARNING: Empty group!")
        if not instance.category:
            print(f"⚠️ WARNING: Empty category!")
            
        # Check if email already exists (unique constraint)
        if instance.email:
            existing_contestant = Contestant.objects.filter(email=instance.email).first()
            if existing_contestant and existing_contestant.id != instance.id:
                print(f"⚠️ WARNING: Email '{instance.email}' already exists for contestant: {existing_contestant.full_name}")
        
        print(f"=== END BEFORE SAVE ===")
        return super().before_save_instance(instance, *args, **kwargs)
    
    def save_instance(self, instance, *args, **kwargs):
        """Override save to add transaction debugging"""
        try:
            print(f"=== SAVING INSTANCE: {instance.full_name} ===")
            result = super().save_instance(instance, *args, **kwargs)
            print(f"✓ Successfully saved: {instance.full_name} (ID: {instance.id})")
            return result
        except Exception as e:
            print(f"✗ Error saving {instance.full_name}: {e}")
            raise

    def import_row(self, row, instance_loader, **kwargs):
        """Override import_row to catch and debug any errors"""
        try:
            print(f"=== STARTING IMPORT ROW FOR {row.get('full_name', 'Unknown')} ===")
            result = super().import_row(row, instance_loader, **kwargs)
            print(f"=== ROW IMPORT RESULT: {result} ===")
            return result
        except Exception as e:
            print(f"=== ERROR IMPORTING ROW: {e} ===")
            print(f"Row data was: {dict(row)}")
            raise  # Re-raise the exception so import process can handle it

    def after_save_instance(self, instance, *args, **kwargs):
        """Handle registered_events after saving contestant"""
        print(f"🔥 AFTER_SAVE_INSTANCE CALLED FOR: {instance.full_name}")
        
        # Extract parameters from args/kwargs to handle different django-import-export versions
        using_transactions = kwargs.get('using_transactions', args[0] if args else True)
        dry_run = kwargs.get('dry_run', args[1] if len(args) > 1 else False)
        
        print(f"=== AFTER SAVE INSTANCE: {instance.full_name} (ID: {instance.id}) ===")
        print(f"Dry run: {dry_run}")
        print(f"Has _registered_events: {hasattr(self, '_registered_events')}")
        
        if hasattr(self, '_registered_events'):
            print(f"_registered_events value: '{self._registered_events}'")
        
        if not dry_run and hasattr(self, '_registered_events') and self._registered_events:
            print(f"🚀 PROCESSING EVENTS FOR: {instance.full_name}")
            print(f"Events string: '{self._registered_events}'")
            
            # Process the registered_events string
            event_names = [name.strip() for name in self._registered_events.split(',') if name.strip()]
            print(f"Parsed event names: {event_names}")
            
            # Check each event exists BEFORE processing
            print(f"🔍 CHECKING EVENTS EXIST:")
            for event_name in event_names:
                exists = Event.objects.filter(name=event_name).exists()
                print(f"  Event '{event_name}': {'✓ EXISTS' if exists else '✗ NOT FOUND'}")
            
            # Clear existing registrations
            existing_count = Registration.objects.filter(contestant=instance).count()
            if existing_count > 0:
                Registration.objects.filter(contestant=instance).delete()
                print(f"Cleared {existing_count} existing registrations")
            
            # Create new registrations
            for event_name in event_names:
                try:
                    event = Event.objects.get(name=event_name)
                    registration, created = Registration.objects.get_or_create(
                        contestant=instance,
                        event=event
                    )
                    print(f"✅ {'CREATED' if created else 'EXISTS'}: {instance.full_name} → {event_name}")
                except Event.DoesNotExist:
                    print(f"❌ FAILED: Event '{event_name}' not found")
                except Exception as e:
                    print(f"❌ ERROR creating registration: {e}")
            
            # Verify registrations were created
            final_count = Registration.objects.filter(contestant=instance).count()
            print(f"📊 FINAL COUNT: {final_count} registrations for {instance.full_name}")
            
        else:
            print(f"⚠️ SKIPPING EVENT PROCESSING:")
            print(f"  - Dry run: {dry_run}")
            print(f"  - Has _registered_events: {hasattr(self, '_registered_events')}")
            if hasattr(self, '_registered_events'):
                print(f"  - _registered_events: '{self._registered_events}'")
        
        print(f"=== END AFTER SAVE: {instance.full_name} ===")
        
        # Call parent method
        try:
            result = super().after_save_instance(instance, *args, **kwargs)
            print(f"✓ Parent after_save_instance completed for {instance.full_name}")
            return result
        except Exception as e:
            print(f"❌ Error in parent after_save_instance: {e}")
            raise

# --- Admin Classes ---

# Inline for managing registrations within Contestant admin
class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 1  # Show 1 empty form by default
    autocomplete_fields = ['event']
    verbose_name = "Event Registration"
    verbose_name_plural = "Event Registrations"

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # The 'categories' field is now a ManyToManyField
    list_display = ('name', 'display_categories', 'add_results_button')
    list_filter = ('categories',) # Filter by the new field
    search_fields = ('name',)
    # Use filter_horizontal for a better multi-select UI
    filter_horizontal = ('categories',)

    def display_categories(self, obj):
        """Creates a string for the admin list display."""
        return ", ".join([cat.name for cat in obj.categories.all()])
    display_categories.short_description = 'Categories'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/add-results/',
                self.admin_site.admin_view(self.add_results_view),
                name='api_event_add_results',
            ),
        ]
        return custom_urls + urls

    def add_results_button(self, obj):
        url = reverse('admin:api_event_add_results', args=[obj.pk])
        return format_html('<a class="button" href="{}">Add/Edit Results</a>', url)
    add_results_button.short_description = 'Manage Results'

    def add_results_view(self, request, object_id):
        event = self.get_object(request, object_id)
        if request.method == 'POST':
            form = EventResultForm(request.POST, event=event)
            if form.is_valid():
                # ... (Your saving logic is correct here)
                data = form.cleaned_data
                result_number = data.get('result_number')
                winners_data = [
                    (1, data.get('winner_1'), data.get('points_1')),
                    (2, data.get('winner_2'), data.get('points_2')),
                    (3, data.get('winner_3'), data.get('points_3')),
                ]
                for position, registration, points in winners_data:
                    if registration:
                        Result.objects.update_or_create(
                            registration=registration,
                            defaults={
                                'position': position,
                                'points': points or 0,
                                'resultNumber': result_number,
                            }
                        )
                self.message_user(request, f"Results for {event.name} saved successfully.", messages.SUCCESS)
                return redirect(reverse('admin:api_event_changelist'))
        else:
            initial_data = {}
            existing_results = Result.objects.filter(registration__event=event)
            if existing_results.exists():
                initial_data['result_number'] = existing_results.first().resultNumber
            for result in existing_results:
                if result.position in [1, 2, 3]:
                    initial_data[f'winner_{result.position}'] = result.registration
                    initial_data[f'points_{result.position}'] = result.points
            form = EventResultForm(initial=initial_data, event=event)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['event'] = event
        return render(request, 'admin/api/event/change_form_results.html', context)



@admin.register(Contestant)
class ContestantAdmin(ImportExportModelAdmin): # <-- This is the key change
    resource_class = ContestantResource
    list_display = ('full_name', 'email', 'group', 'category', 'gender', 'registered_events_display')
    list_filter = ('gender', 'group', 'category')
    search_fields = ('full_name', 'email')
    autocomplete_fields = ['group', 'category']
    inlines = [RegistrationInline]
    
    @admin.display(description='Registered Events')
    def registered_events_display(self, obj):
        registrations = Registration.objects.filter(contestant=obj)
        event_names = [reg.event.name for reg in registrations]
        if event_names:
            return format_html('<br>'.join(event_names))
        return "No events registered"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('contestant', 'event')
    search_fields = ('contestant__full_name', 'event__name')
    autocomplete_fields = ['contestant', 'event']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('get_contestant_name', 'get_event_name', 'position', 'points', 'resultNumber')
    list_filter = ('registration__event__categories__name', 'position') # Corrected path
    search_fields = ('registration__contestant__full_name', 'resultNumber',)
    autocomplete_fields = ['registration']
    
    @admin.display(description='Contestant')
    def get_contestant_name(self, obj):
        return obj.registration.contestant.full_name

    @admin.display(description='Event')
    def get_event_name(self, obj):
        return obj.registration.event.name

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'year', 'image_status', 'uploaded_at')
    list_filter = ('year', 'uploaded_at')
    readonly_fields = ('cloudinary_url', 'uploaded_at')
    fields = ('caption', 'year', 'image', 'cloudinary_url', 'uploaded_at')
    
    @admin.display(description='Image Status')
    def image_status(self, obj):
        if obj.cloudinary_url:
            return format_html(
                '<span style="color: green;">✓ Uploaded to Cloudinary</span><br>'
                '<a href="{}" target="_blank">View Image</a>', 
                obj.cloudinary_url
            )
        elif obj.image:
            return format_html('<span style="color: orange;">⚠ Local storage only</span>')
        else:
            return format_html('<span style="color: red;">✗ No image</span>')
    
    def save_model(self, request, obj, form, change):
        """
        Custom save to ensure Cloudinary upload happens
        """
        super().save_model(request, obj, form, change)
        
        # If save was successful and we have a Cloudinary URL, show success message
        if obj.cloudinary_url:
            self.message_user(
                request, 
                f"Image '{obj.caption}' successfully uploaded to Cloudinary!", 
                level='SUCCESS'
            )
        elif obj.image:
            self.message_user(
                request, 
                f"Image '{obj.caption}' saved but Cloudinary upload may have failed. Check logs.", 
                level='WARNING'
            )

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_status', 'is_active', 'order', 'uploaded_at')
    list_filter = ('is_active', 'uploaded_at')
    list_editable = ('is_active', 'order')
    readonly_fields = ('cloudinary_url', 'uploaded_at')
    fields = ('title', 'image', 'cloudinary_url', 'is_active', 'order', 'uploaded_at')
    ordering = ['order', 'uploaded_at']
    
    @admin.display(description='Image Status')
    def image_status(self, obj):
        if obj.cloudinary_url:
            return format_html(
                '<span style="color: green;">✓ Uploaded to Cloudinary</span><br>'
                '<a href="{}" target="_blank">View Image</a>', 
                obj.cloudinary_url
            )
        elif obj.image:
            return format_html('<span style="color: orange;">⚠ Local storage only</span>')
        else:
            return format_html('<span style="color: red;">✗ No image</span>')
    
    def save_model(self, request, obj, form, change):
        """
        Custom save to ensure Cloudinary upload happens
        """
        super().save_model(request, obj, form, change)
        
        # If save was successful and we have a Cloudinary URL, show success message
        if obj.cloudinary_url:
            self.message_user(
                request, 
                f"Carousel image '{obj.title}' successfully uploaded to Cloudinary!", 
                level='SUCCESS'
            )
        elif obj.image:
            self.message_user(
                request, 
                f"Carousel image '{obj.title}' saved but Cloudinary upload may have failed. Check logs.", 
                level='WARNING'
            )

@admin.register(IndividualChampion)
class IndividualChampionAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'group', 'total_points', 'events_participated']

    def get_queryset(self, request):
        from django.db.models import Q
        queryset = super().get_queryset(request)
        # Only include contestants who have results with points > 0
        queryset = queryset.filter(
            registration__result__isnull=False,
            registration__result__points__gt=0
        ).annotate(
            total_points=Sum('registration__result__points')
        ).distinct().order_by('-total_points')
        return queryset
    
    @admin.display(description='Total Points', ordering='total_points')
    def total_points(self, obj):
        return obj.total_points if obj.total_points else 0
    
    @admin.display(description='Events Participated')
    def events_participated(self, obj):
        # Count events where the contestant has results
        events_count = Result.objects.filter(
            registration__contestant=obj,
            points__gt=0
        ).count()
        return events_count
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False