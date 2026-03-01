from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import RegisterView, LoginView, LogoutView
from .views.item_views import ItemListCreateView, ItemDetailView
from .views.report_views import ItemReportView,UnclaimedItemReportView

# from .views.claim_views import ClaimViewSet
# from .views.admin_views import AuditViewSet, AdminDashboardView
# from .views.coupon_views import CouponViewSet

# TEST
from . import views

# ============================================
# ViewSets Router (CRUD APIs)
# ============================================
router = DefaultRouter()
# router.register(r"items", ItemViewSet, basename="item")
# router.register(r"claims", ClaimViewSet, basename="claim")
# router.register(r"coupons", CouponViewSet, basename="coupon")
# router.register(r"audit", AuditViewSet, basename="audit")

# ============================================
# Module APIs
# ============================================
# TODO: Development/Testing
# test_patterns = [
#     path("hello/", views.hello, name="hello"),
#     path("health/", views.health, name="health"),
# ]

auth_patterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
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

report_patterns = [
    path("items/", views.ItemReportView.as_view(), name="item_report"),
    path("unclaimed-item/", views.UnclaimedItemReportView.as_view(), name="unclaimed_item_report"),
    # path("export/", views.ExportReportView.as_view(), name="export_report"),
]

items_patterns = [
    path("items/", ItemListCreateView.as_view(), name="item-list-create"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
]

# ============================================
# Main URL Patterns
# ============================================
urlpatterns = [
    # Router (RESTful CRUD)
    path("", include(router.urls)),
    # Functional endpoints
    path("auth/", include(auth_patterns)),
    path("admin/", include(admin_patterns)),
    path("reports/", include(report_patterns)),
    path("items/", include(items_patterns)),
    
    # Testing
    # path("test/", include(test_patterns)),
]
