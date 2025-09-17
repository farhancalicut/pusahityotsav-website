from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Sum
from django.http import JsonResponse
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

from .models import Registration
from .serializers import RegistrationSerializer

import io
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
from .models import Category, Event, Group, Result, GalleryImage, Contestant
from .serializers import (
    CategorySerializer, 
    EventSerializer, 
    GroupSerializer, 
    ResultSerializer, 
    GalleryImageSerializer,
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

class ContestantViewSet(viewsets.ModelViewSet):
    queryset = Contestant.objects.all()
    serializer_class = ContestantSerializer
class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class PointsView(APIView):
    def get(self, request):
        group_points = Group.objects.annotate(
            total_points=Sum('contestant__registration__result__points')
        ).order_by('-total_points')

        data = [{'group_name': group.name, 'total_points': group.total_points or 0} for group in group_points]
        return Response(data)

# In api/views.py

class GenerateEventPostersView(APIView):
    def get(self, request, event_id):
        try:
            # 1. Fetch results using the CORRECT database query
            event = Event.objects.get(id=event_id)
            results = Result.objects.filter(event=event, position__in=[1, 2, 3]).order_by('position')

            if not results.exists():
                return Response({"error": "No results published for this event yet."}, status=404)

            result_number_to_display = results.first().resultNumber or ""
            template_files = ['template_black.png', 'template_pink.png', 'template_purple.png']
            generated_posters_urls = []

            # 2. Loop through each template to generate posters
            for template_name in template_files:
                template_path = os.path.join(settings.BASE_DIR, 'assets', template_name)
                image = Image.open(template_path)
                draw = ImageDraw.Draw(image)

                # --- Font and Color Definitions ---
                font_main_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Poppins-Bold.ttf')
                font_secondary_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Poppins-Regular.ttf')
                font_event = ImageFont.truetype(font_main_path, 105)
                font_winner = ImageFont.truetype(font_main_path, 78)
                font_department = ImageFont.truetype(font_secondary_path, 62)
                even_name_color = (252, 224, 9)
                color_primary = (255, 255, 255)
                color_secondary = (255, 255, 255)

                # --- Drawing Text ---
                draw.text((1750, 1700), event.name.upper(), font=font_event, fill=even_name_color)
                start_y = 2290
                for result in results:
                    winner_name = result.contestant.name
                    department_name = result.contestant.group.name
                    draw.text((2100, start_y), winner_name, font=font_winner, fill=color_primary)
                    draw.text((2100, start_y + 95), department_name, font=font_department, fill=color_secondary)
                    start_y += 450

                # 3. Save the generated image to a memory buffer
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                buffer.seek(0)

                # 4. Upload the image from memory to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    buffer,
                    folder="generated_posters",
                    public_id=f'event_{event_id}_{template_name.split(".")[0]}'
                )

                # 5. Get the secure URL from the upload result
                image_url = upload_result.get('secure_url')
                if image_url:
                    generated_posters_urls.append({'id': template_name, 'url': image_url})

            return Response(generated_posters_urls)

        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=404)
        except Exception as e:
            # This will print the exact error to your Render logs for future debugging
            print(f"ERROR in GenerateEventPostersView: {e}")
            return Response({'error': 'An unexpected error occurred on the server.'}, status=500)

def get_registrations_for_event(request, event_id):
    """
    An API endpoint that returns all contestants registered for a given event.
    """
    if not request.user.is_staff: # Basic security
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    registrations = Registration.objects.filter(event_id=event_id).select_related('contestant')
    data = [
        {
            'id': reg.id,
            'name': reg.contestant.full_name
        }
        for reg in registrations
    ]
    return JsonResponse(data, safe=False)