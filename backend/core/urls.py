"""
Enterprise Master URL Configuration for iles_backend.
Delegates traffic to application-specific routing files.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# Auto-Documentation Engine
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # --------------------------------------------------------
    # DJANGO ADMIN PORTAL
    # --------------------------------------------------------
    path("admin/", admin.site.urls),

    # --------------------------------------------------------
    # SYSTEM APIS (Delegated to App URL Confs)
    # --------------------------------------------------------
    # Resolves to: /api/users/v1/...
    path("api/users/", include("users.urls")),
    
    # Resolves to: /api/issues/v1/...
    path("api/issues/", include("issues.urls")),

    # --------------------------------------------------------
    # UNIFIED API DOCUMENTATION
    # --------------------------------------------------------
    # Placed at the root so it generates a single cohesive 
    # document containing both Identity and Issue endpoints.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Serve static files locally during development.
# In production (DEBUG=False), WhiteNoise handles this automatically.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)