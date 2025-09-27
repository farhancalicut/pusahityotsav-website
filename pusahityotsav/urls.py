"""
URL configuration for pusahityotsav project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from api.views import serve_react_app, debug_routing
import os



urlpatterns = [
    path('admin/', admin.site.urls),
    # API routes
    path('api/', include('api.urls')),
    # Debug route (temporary)
    path('debug-routing/', debug_routing, name='debug_routing'),
]

# Add media files serving
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve React static files (CSS, JS, images from build)
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'frontend', 'build', 'static')
        }),
    ]

# Catch-all for React Router (must be last!)
urlpatterns += [
    re_path(r'^(?!admin|api).*$', serve_react_app, name='react_app'),
]

# This is needed to serve uploaded images during development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
