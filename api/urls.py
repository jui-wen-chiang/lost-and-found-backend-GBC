from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ItemListCreateView,
    ItemDetailView,
    CategoryListView,
    LocationListView,
    ItemReportView,
    UnclaimedItemReportView,
)


router = DefaultRouter()

auth_patterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path("token/refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
    # path("password-reset/", views.PasswordResetRequestView.as_view(), name="password_reset"),
    # path("password-reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # path("profile/", views.UserProfileView.as_view(), name="user_profile"),
]

admin_patterns = [
    # path("dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    # path("users/", views.UserManagementView.as_view(), name="user_management"),
    # path("statistics/", views.StatisticsView.as_view(), name="statistics"),
]

items_patterns = [
    path("items/", ItemListCreateView.as_view(), name="item-list-create"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
]

categories_patterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
]

locations_patterns = [
    path("locations/", LocationListView.as_view(), name="location-list"),
]

report_patterns = [
    path("items/", ItemReportView.as_view(), name="item_report"),
    path(
        "unclaimed-item/",
        UnclaimedItemReportView.as_view(),
        name="unclaimed_item_report",
    ),
    # path("export/", views.ExportReportView.as_view(), name="export_report"),
]

urlpatterns = [
    path("", include(router.urls)),
    # Functional endpoints
    path("auth/", include(auth_patterns)),
    path("admin/", include(admin_patterns)),
    path("items/", include(items_patterns)),
    path("categories/", include(categories_patterns)),
    path("locations/", include(locations_patterns)),
    path("reports/", include(report_patterns)),
]
