from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Enterprise Standard for Stateless Authentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    UserViewSet,
    StudentProfileViewSet,
    SupervisorProfileViewSet,
    AdministratorProfileViewSet,
)

app_name = "users"

# ============================================================
# ROUTER CONFIGURATION
# ============================================================
router = DefaultRouter()

# Identity & Profile Management
router.register(r"users", UserViewSet, basename="user")
router.register(r"profiles/students", StudentProfileViewSet, basename="student-profile")
router.register(r"profiles/supervisors", SupervisorProfileViewSet, basename="supervisor-profile")
router.register(r"profiles/administrators", AdministratorProfileViewSet, basename="administrator-profile")

# ============================================================
# URL PATTERNS
# ============================================================
urlpatterns = [
    # --------------------------------------------------------
    # CORE API ENDPOINTS
    # --------------------------------------------------------
    path("v1/", include(router.urls)),

    # --------------------------------------------------------
    # AUTHENTICATION (JWT)
    # --------------------------------------------------------
    # Submit username/password -> Get Access & Refresh tokens
    path("v1/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    
    # Submit valid Refresh token -> Get new Access token
    path("v1/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Submit token -> Check if it is still valid
    path("v1/auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
]