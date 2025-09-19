from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    EventViewSet,
    GroupViewSet,
    GalleryImageViewSet,
    ContestantViewSet,
    ResultViewSet,
    PointsView,
    GenerateEventPostersView,
    RegistrationViewSet,
    EventsForRegistrationView,
    debug_cloudinary_vars # <-- 1. ADD THIS IMPORT
)
from . import views

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'gallery', GalleryImageViewSet, basename='gallery')
router.register(r'contestants', ContestantViewSet)
router.register(r'results', ResultViewSet)
router.register(r'registrations', RegistrationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('points/', PointsView.as_view(), name='points'),
    path('generate-event-posters/<int:event_id>/', GenerateEventPostersView.as_view(), name='generate-event-posters'),
    path('events-for-registration/<int:category_id>/', EventsForRegistrationView.as_view(), name='events-for-registration'),

    # 2. ADD THIS NEW LINE AT THE BOTTOM
    path('debug-vars/', debug_cloudinary_vars, name='debug-vars'),
]