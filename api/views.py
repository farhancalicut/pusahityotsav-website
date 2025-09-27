from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models import Q
from django.utils import timezone
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
            
            # Get all results for this event
            all_results = Result.objects.filter(registration__event=event).select_related(
                'registration__contestant__group', 'registration__event'
            )
            
            # Get winning results (positions 1, 2, 3) that should be included in posters
            results = all_results.filter(
                position__in=[1, 2, 3], 
                include_in_poster=True
            ).order_by('position', 'display_order')  # Order by position first, then display_order for ties

            if not results.exists():
                # No poster-eligible winning results found
                return Response([], status=200)

            
            # Pre-calculate common data once
            result_number = results.first().resultNumber or ""
            
            category_names = [cat.name for cat in event.categories.all()]
            is_general_event = len(category_names) > 1
            
            # Ensure output directory exists once
            output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_posters')
            os.makedirs(output_dir, exist_ok=True)
            
            generated_posters_urls = []
            template_files = ['tmb1.png', 'tmb2.png']

            # Process one template at a time to minimize memory usage
            for template_name in template_files:
                try:
                    # Load template and process immediately
                    template_path = os.path.join(settings.BASE_DIR, 'assets', template_name)
                    
                    if not os.path.exists(template_path):
                        continue
                    
                    # Open, process, and save in one go to minimize memory usage
                    with Image.open(template_path) as template_img:
                        # Copy the template to work with and convert to RGB mode
                        # This fixes the "cannot allocate more than 256 colors" error
                        image = template_img.convert('RGB')
                    
                    # Load fonts (do this once per template to save memory)
                    try:
                        font_main_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'chinese rocks rg.otf')
                        font_secondary_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Poppins-Medium.ttf')
                        
                        print(f"Font paths - Main: {font_main_path}, Secondary: {font_secondary_path}")
                        print(f"Font files exist - Main: {os.path.exists(font_main_path)}, Secondary: {os.path.exists(font_secondary_path)}")
                        
                        # font_result_label = ImageFont.truetype(font_main_path, 40)
                        font_publication_num = ImageFont.truetype(font_main_path, 60)
                        font_category = ImageFont.truetype(font_main_path, 50)
                        font_event = ImageFont.truetype(font_main_path, 60)
                        font_winner = ImageFont.truetype(font_main_path, 45)
                        font_department = ImageFont.truetype(font_secondary_path, 25)
                        print("✅ All fonts loaded successfully")
                        
                    except Exception as font_error:
                        print(f"❌ Font loading error: {font_error}")
                        # Use default font if custom fonts fail
                        font_result_label = font_publication_num = font_category = font_event = font_winner = font_department = ImageFont.load_default()
                    
                    draw = ImageDraw.Draw(image)
                    
                    # Define colors
                    color_primary = (0, 0, 0)
                    color_secondary = (0, 0, 0) 
                    even_name_color = (167, 18, 26)
                    print(f"Colors defined - Primary: {color_primary}, Secondary: {color_secondary}, Event: {even_name_color}")
                    
                    # Get image dimensions for reference
                    img_width, img_height = image.size
                    print(f"Template dimensions: {img_width} x {img_height}")
                    
                    # ===== CUSTOMIZABLE POSITIONS =====
                    # Adjust these X,Y coordinates for any template design
                    
                    # "Result" label position
                    # result_label_x = 200
                    # result_label_y = 150
                    
                    # Result number position (01, 02, etc.)
                    result_num_x = 225
                    result_num_y = 605
                    
                    # Category position (GIRLS, BOYS, etc.)
                    category_x = 210
                    category_y = 705
                    
                    # Event name position
                    event_x = 210
                    event_y = 760
                    
                    # Winners starting position and spacing
                    winners_start_x = 280
                    winners_start_y = 885
                    winners_spacing = 95  # Vertical space between each winner
                    
                    # Department name offset (relative to winner name)
                    dept_x_offset = 0    # Horizontal offset from winner name
                    dept_y_offset = 40   # Vertical offset from winner name
                    
                    # Draw "Result" label
                    # draw.text((result_label_x, result_label_y), "Result", font=font_result_label, fill=color_secondary)
                    # print(f"Drew 'Result' label at ({result_label_x}, {result_label_y})")
                    
                    # Draw result number
                    draw.text((result_num_x, result_num_y), str(result_number), font=font_publication_num, fill=color_primary)
                    print(f"Drew result number: '{result_number}' at ({result_num_x}, {result_num_y})")
                    
                    # Draw category and event name
                    if not is_general_event and category_names:
                        category_text = category_names[0].upper()
                        draw.text((category_x, category_y), category_text, font=font_category, fill=color_secondary)
                        print(f"Drew category: '{category_text}' at ({category_x}, {category_y})")
                    else:
                        print("Skipped category (general event or no categories)")
                    
                    # Draw event name
                    event_text = event.name.upper()
                    draw.text((event_x, event_y), event_text, font=font_event, fill=even_name_color)
                    print(f"Drew event name: '{event_text}' at ({event_x}, {event_y})")
                    
                    # Draw winners list - simple X,Y positioning with tie handling
                    # Results are already sorted by position, then display_order for ties
                    
                    for i, result in enumerate(results):
                        winner_name = result.registration.contestant.full_name
                        department_name = result.registration.contestant.group.name
                        position = result.position
                        display_order = result.display_order
                        
                        print(f"  Drawing winner at position {position} (display_order: {display_order}): {winner_name} - {department_name}")
                        
                        # Calculate positions for this winner
                        winner_y = winners_start_y + (i * winners_spacing)
                        dept_x = winners_start_x + dept_x_offset
                        dept_y = winner_y + dept_y_offset
                        
                        try:
                            # Draw winner name and department
                            draw.text((winners_start_x, winner_y), winner_name, font=font_winner, fill=color_primary)
                            draw.text((dept_x, dept_y), department_name, font=font_department, fill=color_secondary)
                            print(f"    Winner drawn at ({winners_start_x}, {winner_y})")
                            print(f"    Department drawn at ({dept_x}, {dept_y})")
                        except Exception as e:
                            print(f"    ERROR drawing winner: {e}")
                    
                    # Save to memory buffer instead of local file for Cloudinary upload
                    output_filename = f'event_{event_id}_{template_name}'
                    
                    # Save image to memory buffer
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    print(f"✅ Saved {output_filename} to memory buffer")
                    
                    # Upload to Cloudinary
                    try:
                        print(f"📤 Uploading {output_filename} to Cloudinary...")
                        upload_result = cloudinary.uploader.upload(
                            img_buffer,
                            public_id=f"generated_posters/{output_filename}",
                            folder="generated_posters",
                            resource_type="image",
                            format="png"
                        )
                        
                        # Get the Cloudinary URL
                        image_url = upload_result['secure_url']
                        generated_posters_urls.append({'id': template_name, 'url': image_url})
                        print(f"✅ Successfully uploaded to Cloudinary: {image_url}")
                        
                    except Exception as cloudinary_error:
                        print(f"❌ Cloudinary upload failed: {cloudinary_error}")
                        # Fallback: save locally (won't work on Render but good for local testing)
                        try:
                            output_path = os.path.join(output_dir, output_filename)
                            image.save(output_path, "PNG")
                            image_url = request.build_absolute_uri(
                                os.path.join(settings.MEDIA_URL, 'generated_posters', output_filename)
                            )
                            generated_posters_urls.append({'id': template_name, 'url': image_url})
                            print(f"⚠️ Saved locally as fallback: {image_url}")
                        except Exception as local_error:
                            print(f"❌ Local save also failed: {local_error}")
                            continue
                    
                    # Immediately close and delete the image to free memory
                    image.close()
                    del image
                    del draw
                    
                    print(f"✅ Completed template: {template_name}")
                    
                except Exception as template_error:
                    print(f"❌ Error processing template {template_name}: {template_error}")
                    import traceback
                    traceback.print_exc()
                    continue

            print(f"🎯 Generated {len(generated_posters_urls)} posters for event {event_id}")
            print(f"Response data: {generated_posters_urls}")
            return Response(generated_posters_urls)

        except Event.DoesNotExist:
            print(f"❌ Event not found: {event_id}")
            return Response({"error": "Event not found."}, status=404)
        except Exception as e:
            print(f"💥 CRITICAL ERROR in GenerateEventPostersView: {e}")
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


def serve_react_app(request):
    """
    Serve the React app's index.html for all frontend routes.
    This handles React Router's client-side routing.
    """
    try:
        index_file_path = os.path.join(settings.BASE_DIR, 'frontend', 'build', 'index.html')
        
        # Check if the file exists
        if not os.path.exists(index_file_path):
            return HttpResponse(
                '<h1>Frontend not built</h1><p>Please run <code>npm run build</code> in the frontend directory.</p>', 
                content_type='text/html', 
                status=404
            )
        
        with open(index_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Set proper headers for SPA
        response = HttpResponse(content, content_type='text/html')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except Exception as e:
        return HttpResponse(
            f'<h1>Error serving frontend</h1><p>Error: {str(e)}</p>', 
            content_type='text/html', 
            status=500
        )


def debug_routing(request):
    """Debug view to see what's happening with routing"""
    return JsonResponse({
        'path': request.path,
        'method': request.method,
        'headers': dict(request.headers),
        'META': {
            'HTTP_HOST': request.META.get('HTTP_HOST'),
            'SERVER_NAME': request.META.get('SERVER_NAME'),
            'REQUEST_URI': request.META.get('REQUEST_URI', 'Not set'),
        }
    })