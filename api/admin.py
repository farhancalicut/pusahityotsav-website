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
        
        # Store registered_events for later processing
        if 'registered_events' in row:
            self._registered_events = row.get('registered_events', '').strip()
        else:
            self._registered_events = ''
        
        # Check if Group and Category exist
        group_name = row.get('group', '').strip()
        category_name = row.get('category', '').strip()
        
        if group_name:
            if not Group.objects.filter(name=group_name).exists():
                # Group doesn't exist - could add logging here if needed
                pass
        
        if category_name:
            if not Category.objects.filter(name=category_name).exists():
                # Category doesn't exist - could add logging here if needed  
                pass
        
        return super().before_import_row(row, **kwargs)
    
    def before_save_instance(self, instance, *args, **kwargs):
        """Process before saving the contestant"""
        # Extract parameters from args/kwargs to handle different django-import-export versions
        using_transactions = kwargs.get('using_transactions', args[0] if args else True)
        dry_run = kwargs.get('dry_run', args[1] if len(args) > 1 else False)
        
        
        # Check for potential data issues
        if not instance.full_name:
            # Empty full_name - could log if needed
            pass
        if not instance.email:
            # Empty email - could log if needed
            pass
        if not instance.group:
            # Empty group - could log if needed
            pass
        if not instance.category:
            # Empty category - could log if needed
            pass
            
        # Check if email already exists (unique constraint)
        if instance.email:
            existing_contestant = Contestant.objects.filter(email=instance.email).first()
            if existing_contestant and existing_contestant.id != instance.id:
                # Duplicate email - could log if needed
                pass
        
        return super().before_save_instance(instance, *args, **kwargs)
    
    def save_instance(self, instance, *args, **kwargs):
        """Override save to handle transactions properly"""
        try:
            result = super().save_instance(instance, *args, **kwargs)
            return result
        except Exception as e:
            # Could add logging here if needed
            raise

    def import_row(self, row, instance_loader, **kwargs):
        """Override import_row to handle errors gracefully"""
        try:
            result = super().import_row(row, instance_loader, **kwargs)
            return result
        except Exception as e:
            # Could add logging here if needed
            raise  # Re-raise the exception so import process can handle it

    def after_save_instance(self, instance, *args, **kwargs):
        """Handle registered_events after saving contestant"""
        
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
                # Clear existing results for this event
                Result.objects.filter(registration__event=event).delete()
                
                data = form.cleaned_data
                result_number = data.get('result_number')
                saved_count = 0
                
                # Process winners for each position
                for position in [1, 2, 3]:
                    winners = data.get(f'winners_{position}')
                    points = data.get(f'points_{position}', 0)
                    
                    if winners and points is not None:
                        display_order = 1
                        for registration in winners:
                            Result.objects.create(
                                registration=registration,
                                position=position,
                                points=points,
                                resultNumber=result_number,
                                include_in_poster=True,
                                display_order=display_order
                            )
                            display_order += 1
                            saved_count += 1
                            print(f"✅ Saved: {registration.contestant.full_name} - Position {position}, Points {points}")
                
                # Process non-poster participants
                non_poster_participants = data.get('non_poster_participants')
                non_poster_points = data.get('non_poster_points', 0)
                
                if non_poster_participants and non_poster_points is not None:
                    for registration in non_poster_participants:
                        # Use position 4 for non-poster participants (outside poster range 1-3)
                        Result.objects.create(
                            registration=registration,
                            position=4,  # Outside poster range
                            points=non_poster_points,
                            resultNumber=result_number,
                            include_in_poster=False,  # Won't appear on posters
                            display_order=1
                        )
                        saved_count += 1
                        print(f"✅ Saved (Non-poster): {registration.contestant.full_name} - Points {non_poster_points}")
                
                self.message_user(
                    request, 
                    f"Results for {event.name} saved successfully! {saved_count} results created.", 
                    messages.SUCCESS
                )
                return redirect(reverse('admin:api_event_changelist'))
            else:
                self.message_user(request, "Please correct the errors below.", messages.ERROR)
        else:
            # Pre-populate form with existing results
            initial_data = {}
            existing_results = Result.objects.filter(registration__event=event)
            
            if existing_results.exists():
                initial_data['result_number'] = existing_results.first().resultNumber
                
                # Group results by position
                for position in [1, 2, 3]:
                    position_results = existing_results.filter(position=position, include_in_poster=True).order_by('display_order')
                    if position_results.exists():
                        initial_data[f'winners_{position}'] = [r.registration for r in position_results]
                        initial_data[f'points_{position}'] = position_results.first().points
                
                # Non-poster participants (position > 3 or include_in_poster=False)
                non_poster_results = existing_results.filter(include_in_poster=False)
                if non_poster_results.exists():
                    initial_data['non_poster_participants'] = [r.registration for r in non_poster_results]
                    initial_data['non_poster_points'] = non_poster_results.first().points
                    
            form = EventResultForm(initial=initial_data, event=event)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['event'] = event
        context['registered_participants'] = Registration.objects.filter(event=event).select_related('contestant', 'contestant__group').count()
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
class PublishedResultsAdmin(admin.ModelAdmin):
    """Simple view for published results - one row per event with winners"""
    
    list_display = [
        'get_event_name', 
        'get_total_results',
        'get_result_number',
        'view_winners_button'
    ]
    list_filter = [
        ('registration__event', admin.RelatedOnlyFieldListFilter),
        'resultNumber',
    ]
    search_fields = [
        'registration__event__name',
        'resultNumber'
    ]
    ordering = ['registration__event__name', '-id']
    
    # Make it read-only
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        # Check if this is a "winners view" (filtered by event and position)
        if request.GET.get('registration__event__id__exact') and request.GET.get('position__in'):
            # Show individual winner results for specific event
            return super().get_queryset(request).select_related(
                'registration__event', 'registration__contestant'
            ).order_by('position', 'display_order')
        else:
            # Show one result per event (main view)
            qs = super().get_queryset(request)
            from django.db.models import Min
            event_result_ids = qs.values('registration__event').annotate(
                min_id=Min('id')
            ).values_list('min_id', flat=True)
            
            return qs.filter(id__in=event_result_ids).select_related(
                'registration__event', 'registration__contestant'
            ).order_by('registration__event__name', '-id')
    
    def get_list_display(self, request):
        # Different display for winners view vs main view
        if request.GET.get('registration__event__id__exact') and request.GET.get('position__in'):
            return ['get_position_display', 'get_winner_name', 'back_to_events_button']
        else:
            return ['get_event_name', 'get_total_results', 'get_result_number', 'view_winners_button']
    
    # Custom display methods for main view
    @admin.display(description='Event', ordering='registration__event__name')
    def get_event_name(self, obj):
        return obj.registration.event.name
    
    @admin.display(description='Published Results')
    def get_total_results(self, obj):
        total = Result.objects.filter(registration__event=obj.registration.event).count()
        return f"{total} results"
    
    @admin.display(description='Result #', ordering='resultNumber')
    def get_result_number(self, obj):
        return obj.resultNumber or '-'
    
    @admin.display(description='Winners')
    def view_winners_button(self, obj):
        event_id = obj.registration.event.id
        url = reverse('admin:api_result_changelist') + f'?registration__event__id__exact={event_id}&position__in=1,2,3'
        return format_html('<a class="button" href="{}">View Winners</a>', url)
    
    # Custom display methods for winners view
    @admin.display(description='Position')
    def get_position_display(self, obj):
        medals = {1: '🥇 First', 2: '🥈 Second', 3: '🥉 Third'}
        return medals.get(obj.position, f'Position {obj.position}')
    
    @admin.display(description='Winner')
    def get_winner_name(self, obj):
        return obj.registration.contestant.full_name
    
    @admin.display(description='')
    def back_to_events_button(self, obj):
        url = reverse('admin:api_result_changelist')
        return format_html('<a href="{}">← Back to Events</a>', url)

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