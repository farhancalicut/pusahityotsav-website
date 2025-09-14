from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Sum

from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

from .models import Registration
from .serializers import RegistrationSerializer

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

class GenerateEventPostersView(APIView):
    def get(self, request, event_id):
        results = Result.objects.filter(
    registration__event__id=event_id, 
    position__in=[1, 2, 3]
).order_by('position')

        if not results:
            return Response({"error": "No results found"}, status=404)

        publication_number = results[0].id
        template_files = ['template_black.png', 'template_pink.png', 'template_purple.png']
        generated_posters_urls = []
        event_details = results[0].registration.event

        for template_name in template_files:
            try:
                template_path = os.path.join(settings.BASE_DIR, 'assets', template_name)
                image = Image.open(template_path)
                draw = ImageDraw.Draw(image)
                img_width, img_height = image.size
                font_main_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Poppins-Bold.ttf')
                font_secondary_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Poppins-Regular.ttf')

                # Create separate font objects for each text element
                font_result_label = ImageFont.truetype(font_main_path, 65)
                font_publication_num = ImageFont.truetype(font_main_path, 300)
                font_category = ImageFont.truetype(font_secondary_path, 80)
                font_event = ImageFont.truetype(font_main_path, 105)
                font_winner = ImageFont.truetype(font_main_path, 78)
                font_department = ImageFont.truetype(font_secondary_path, 62)

                # --- 2. COLOR CUSTOMIZATION ---
                # Define different colors for your text
                color_primary = (255, 255, 255) #if "black" in template_name else (0, 0, 0)
                color_secondary = (255, 255, 255) #if "black" in template_name else (100, 100, 100)
                even_name_color = (252, 224, 9) #if "black" in template_name else (255, 255, 255)
                # --- 3. TEXT AND POSITION (ALIGNMENT) CUSTOMIZATION ---
                # Adjust the (X, Y) coordinates for each draw.text() call

                # Result Label
                draw.text((1500, 1450), "Result", font=font_result_label, fill=color_secondary)

                # Publication Number
                draw.text((1550, 1500), str(publication_number), font=font_publication_num, fill=color_primary)

                # Category Name (now shown first)
                draw.text((1750, 1600), event_details.category.name.upper(), font=font_category, fill=color_secondary)

                # Event Name (now shown second)
                draw.text((1750, 1700), event_details.name.upper(), font=font_event, fill=even_name_color)
                
                # Winners List
                start_y = 2290
                for result in results:
                    winner_name = result.registration.contestant.full_name
                    department_name = result.registration.contestant.group.name 
                    
                    # Winner Name
                    draw.text((2100, start_y ), winner_name, font=font_winner, fill=color_primary)
                    # Department Name
                    draw.text((2100, start_y  + 95), department_name, font=font_department, fill=color_secondary)
                    
                    start_y += 450


                output_filename = f'event_{event_id}_{template_name}'
                output_path = os.path.join(settings.MEDIA_ROOT, 'generated_posters', output_filename)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                image.save(output_path, "PNG")

                image_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, 'generated_posters', output_filename))
                generated_posters_urls.append({'id': template_name, 'url': image_url})
            except FileNotFoundError:
                continue
        
        return Response(generated_posters_urls)
