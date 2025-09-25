from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models import Q
import cloudinary.uploader
from django.db import connection

from PIL import Image, ImageDraw, ImageFont
import os
import io
from django.conf import settings

from .models import Registration
from .serializers import RegistrationSerializer

class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
from .models import Category, Event, Group, Result, GalleryImage, CarouselImage, Contestant
from .serializers import (
    CategorySerializer, 
    EventSerializer, 
    GroupSerializer, 
    ResultSerializer, 
    GalleryImageSerializer,
    CarouselImageSerializer,
    ContestantSerializer
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class GalleryImageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GalleryImageSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned images to a given year,
        by filtering against a `year` query parameter in the URL.
        """
        queryset = GalleryImage.objects.all().order_by('-uploaded_at')
        year = self.request.query_params.get('year')
        if year is not None:
            queryset = queryset.filter(year=year)
        return queryset

class CarouselImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for carousel images that auto-scroll on the dashboard.
    Only returns active images, ordered by their specified order.
    """
    serializer_class = CarouselImageSerializer

    def get_queryset(self):
        """
        Returns only active carousel images, ordered by their order field.
        """
        return CarouselImage.objects.filter(is_active=True).order_by('order', 'uploaded_at')

class ContestantViewSet(viewsets.ModelViewSet):
    queryset = Contestant.objects.all()
    serializer_class = ContestantSerializer
class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class PointsView(APIView):
    def get(self, request, format=None):
        groups = Group.objects.all()
        points_data = []
        for group in groups:
            # Calculate total points for each group
            total_points = Result.objects.filter(
                registration__contestant__group=group
            ).aggregate(total=Sum('points'))['total'] or 0

            points_data.append({
                'group_name': group.name,
                'total_points': total_points
            })

        # --- THIS IS THE FIX ---
        # Sort the list of dictionaries by 'total_points' in descending order.
        sorted_points_data = sorted(points_data, key=lambda x: x['total_points'], reverse=True)
        # --------------------

        return Response(sorted_points_data)


class GenerateEventPostersView(APIView):
    def get(self, request, event_id):
        try:
            # Optimized query with select_related to reduce database hits
            event = Event.objects.select_related().prefetch_related('categories').get(id=event_id)
            results = Result.objects.filter(
                registration__event=event,
                position__in=[1, 2, 3]
            ).order_by('position').select_related(
                'registration__contestant__group',
                'registration__event'
            )

            if not results.exists():
                return Response([], status=200)

            # Pre-calculate common data once
            result_number = results.first().resultNumber or ""
            category_names = [cat.name for cat in event.categories.all()]
            is_general_event = len(category_names) > 1
            
            # Ensure output directory exists once
            output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_posters')
            os.makedirs(output_dir, exist_ok=True)
            
            generated_posters_urls = []
            template_files = ['template_black.png', 'template_pink.png', 'template_purple.png']

            # Process one template at a time to minimize memory usage
            for template_name in template_files:
                try:
                    print(f"Processing template: {template_name}")
                    
                    # Load template and process immediately
                    template_path = os.path.join(settings.BASE_DIR, 'assets', template_name)
                    
                    # Open, process, and save in one go to minimize memory usage
                    with Image.open(template_path) as template_img:
                        # Copy the template to work with
                        image = template_img.copy()
                    
                    # Load fonts (do this once per template to save memory)
                    try:
                        font_main_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Poppins-Bold.ttf')
                        font_secondary_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Poppins-Regular.ttf')
                        
                        font_result_label = ImageFont.truetype(font_main_path, 65)
                        font_publication_num = ImageFont.truetype(font_main_path, 300)
                        font_category = ImageFont.truetype(font_secondary_path, 80)
                        font_event = ImageFont.truetype(font_main_path, 105)
                        font_winner = ImageFont.truetype(font_main_path, 78)
                        font_department = ImageFont.truetype(font_secondary_path, 62)
                        
                    except Exception as font_error:
                        print(f"Font loading error: {font_error}")
                        # Use default font if custom fonts fail
                        font_result_label = font_publication_num = font_category = font_event = font_winner = font_department = ImageFont.load_default()
                    
                    draw = ImageDraw.Draw(image)
                    
                    # Define colors
                    color_primary = (255, 255, 255)
                    color_secondary = (255, 255, 255)
                    even_name_color = (252, 224, 9)
                    
                    # Draw content
                    draw.text((1500, 1450), "Result", font=font_result_label, fill=color_secondary)
                    draw.text((1550, 1500), str(result_number), font=font_publication_num, fill=color_primary)
                    
                    # Draw category and event name
                    event_y_position = 1700
                    if not is_general_event and category_names:
                        category_text = category_names[0].upper()
                        draw.text((1750, 1600), category_text, font=font_category, fill=color_secondary)
                    else:
                        event_y_position = 1650
                    
                    draw.text((1750, event_y_position), event.name.upper(), font=font_event, fill=even_name_color)
                    
                    # Draw winners list
                    start_y = 2290
                    for result in results:
                        winner_name = result.registration.contestant.full_name
                        department_name = result.registration.contestant.group.name
                        
                        draw.text((2100, start_y), winner_name, font=font_winner, fill=color_primary)
                        draw.text((2100, start_y + 95), department_name, font=font_department, fill=color_secondary)
                        start_y += 450
                    
                    # Save with memory-efficient approach
                    output_filename = f'event_{event_id}_{template_name}'
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # Save without optimization to avoid PIL issues on Render
                    image.save(output_path, "PNG")
                    print(f"Saved: {output_filename}")
                    
                    # Build URL
                    image_url = request.build_absolute_uri(
                        os.path.join(settings.MEDIA_URL, 'generated_posters', output_filename)
                    )
                    generated_posters_urls.append({'id': template_name, 'url': image_url})
                    
                    # Immediately close and delete the image to free memory
                    image.close()
                    del image
                    del draw
                    
                    print(f"Completed template: {template_name}")
                    
                except Exception as template_error:
                    print(f"Error processing template {template_name}: {template_error}")
                    continue

            print(f"Generated {len(generated_posters_urls)} posters for event {event_id}")
            return Response(generated_posters_urls)

        except Event.DoesNotExist:
            return Response({"error": "Event not found."}, status=404)
        except Exception as e:
            print(f"CRITICAL ERROR in GenerateEventPostersView: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': 'An unexpected server error occurred.'}, status=500)

class EventsForRegistrationView(APIView):
    """
    A smart view that returns events for a specific category
    PLUS any events that are considered "general".
    """
    def get(self, request, category_id):
        try:
            # A "general" event is one linked to both Category A and Category B
            general_event_categories = Category.objects.filter(name__in=['Category A', 'Category B'])

            # Find events that are linked to the contestant's specific category OR are general
            events = Event.objects.filter(
                Q(categories__id=category_id) |
                Q(categories__in=general_event_categories)
            ).distinct().order_by('name')

            serializer = EventSerializer(events, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=404)
        
def debug_cloudinary_vars(request):
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    # This will print the values to your Render server logs.
    print("--- CLOUDINARY DEBUG START ---")
    print(f"DEBUG: CLOUD_NAME = {cloud_name}")
    print(f"DEBUG: API_KEY = {api_key}")
    print(f"DEBUG: API_SECRET_IS_SET = {'Yes, a value exists' if api_secret else 'No, it is empty or missing'}")
    print("--- CLOUDINARY DEBUG END ---")

    return HttpResponse("Debug information has been printed to the Render logs. Please check them now.")

def debug_gallery_images(request):
    """
    Debug endpoint to see what's happening with gallery images
    """
    from .models import GalleryImage
    from .serializers import GalleryImageSerializer
    import os
    
    debug_info = {
        'cloudinary_env_vars': {
            'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
            'API_KEY': os.environ.get('CLOUDINARY_API_KEY', 'Not set'),
            'API_SECRET': 'Set' if os.environ.get('CLOUDINARY_API_SECRET') else 'Not set'
        },
        'total_images': GalleryImage.objects.count(),
        'sample_images': []
    }
    
    # Get first 3 images for debugging
    sample_images = GalleryImage.objects.all()[:3]
    for img in sample_images:
        serializer = GalleryImageSerializer(img)
        debug_info['sample_images'].append({
            'id': img.id,
            'caption': img.caption,
            'year': img.year,
            'raw_image_name': img.image.name,
            'raw_image_url': img.image.url,
            'serialized_data': serializer.data
        })
    
    return Response(debug_info)

# Ping endpoint to keep database awake
def ping_database(request):
    """
    Simple endpoint to keep the database connection alive.
    Returns the current time and database status.
    """
    try:
        # Execute a simple query to keep database awake
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        from django.utils import timezone
        return JsonResponse({
            'status': 'ok',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'message': 'Database ping successful'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'timestamp': timezone.now().isoformat(),
            'database': 'error',
            'message': str(e)
        }, status=500)
