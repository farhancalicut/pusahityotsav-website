from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    EventViewSet,
    GroupViewSet,
    GalleryImageViewSet,
    CarouselImageViewSet,
    ContestantViewSet,
    ResultViewSet,
    PointsView,
    GenerateEventPostersView,
    RegistrationViewSet,
    EventsForRegistrationView,
    debug_cloudinary_vars,
    debug_gallery_images, # <-- ADD THIS NEW IMPORT
    ping_database,
    WinnersExportView  # Add the new export view
)
from . import views

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'gallery', GalleryImageViewSet, basename='gallery')
router.register(r'carousel', CarouselImageViewSet, basename='carousel')
router.register(r'contestants', ContestantViewSet)
router.register(r'results', ResultViewSet)
router.register(r'registrations', RegistrationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('points/', PointsView.as_view(), name='points'),
    path('generate-event-posters/<int:event_id>/', GenerateEventPostersView.as_view(), name='generate-event-posters'),
    path('events-for-registration/<int:category_id>/', EventsForRegistrationView.as_view(), name='events-for-registration'),

    # Winners Export endpoints
    path('export-winners/', WinnersExportView.as_view(), name='export-all-winners'),
    path('export-winners/<int:event_id>/', WinnersExportView.as_view(), name='export-event-winners'),

    # Debug endpoints
    path('debug-vars/', debug_cloudinary_vars, name='debug-vars'),
    path('debug-gallery/', debug_gallery_images, name='debug-gallery'),
    
    # Keep database awake endpoint
    path('ping/', ping_database, name='ping-database'),
]