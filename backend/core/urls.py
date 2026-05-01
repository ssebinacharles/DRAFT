"""
Enterprise Master URL Configuration for iles_backend.
Delegates traffic to application-specific routing files.
"""
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token
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
    path("api/users/", include("users.urls")),
    path("api/issues/", include("issues.urls")),

    # --------------------------------------------------------
    # AUTHENTICATION ENDPOINT
    # --------------------------------------------------------
    # This matches the http://localhost:8000/api/auth/login/ call from Next.js
    path("api/auth/login/", obtain_auth_token, name="api_token_auth"), # <--- ADD THIS LINE

    # --------------------------------------------------------
    # UNIFIED API DOCUMENTATION
    # --------------------------------------------------------
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

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)