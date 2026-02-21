from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    health,
    CategoryListView,
    LocationListView,
    ItemListCreateView,
    ItemDetailView,
)

from .views.auth_views import RegisterView, LoginView, LogoutView

# ============================================
# ViewSets Router (future CRUD APIs)
# ============================================
router = DefaultRouter()
# router.register(r"items", ItemViewSet, basename="item")

# ============================================
# Auth APIs
# ============================================
auth_patterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

# ============================================
# Main URL Patterns
# ============================================
urlpatterns = [
    # Router
    path("", include(router.urls)),

    # Health check
    path("health/", health, name="health"),

    # Categories & Locations
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("locations/", LocationListView.as_view(), name="location-list"),

    # Item CRUD
    path("items/", ItemListCreateView.as_view(), name="item-list-create"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),

    # Auth
    path("auth/", include(auth_patterns)),
]