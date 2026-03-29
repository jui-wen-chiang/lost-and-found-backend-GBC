from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    UserDashboardView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ItemListCreateView,
    ItemDetailView,
    LostItemsReportView,
    FoundItemsReportView,
    ItemStatusStatsView,
    AuditQueueView,
    ApprovePostView,
    RejectPostView,
    AdminDeletePostView,
    AdminEditPostView,
    AdminUserListView,
    AdminUserRoleUpdateView,
    VerifiedItemsListView,
    CategoryListView,
    LocationListView,
    ItemReportView,
    UnclaimedItemReportView,
    ItemStatusSummaryView,
    TriggerExpirationView,
    TaskResultView,
    QRCodeGenerateView,
    QRCodeVerifyView,
    ClaimCreateView,
    ClaimListView,
    ClaimStatusUpdateView,
    AdminClaimListView,
    AppointmentCreateView,
    AppointmentStatusUpdateView,
    AppointmentReminderView,
    UserCouponListView,
    ActivateCouponView,
    VerifyCouponView,
    CouponStatsView,
)

router = DefaultRouter()

auth_patterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("dashboard/", UserDashboardView.as_view(), name="user_dashboard"),
]

admin_patterns = [
    path("audit/posts/", AuditQueueView.as_view(), name="audit-queue"),
    path("items/<int:pk>/approve/", ApprovePostView.as_view(), name="approve-post"),
    path("items/<int:pk>/reject/", RejectPostView.as_view(), name="reject-post"),
    path(
        "items/<int:pk>/delete/",
        AdminDeletePostView.as_view(),
        name="delete-post",
    ),
    path("items/<int:pk>/edit/", AdminEditPostView.as_view(), name="edit-post"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("users/<int:pk>/role/", AdminUserRoleUpdateView.as_view(), name="admin-user-role"),
    path("items/verified/", VerifiedItemsListView.as_view(), name="verified-items"),
]

items_patterns = [
    path("", ItemListCreateView.as_view(), name="item-list-create"),
    path("<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
    path("items/<int:item_id>/verify/", QRCodeVerifyView.as_view(), name="item-verify"),
]

categories_patterns = [
    path("", CategoryListView.as_view(), name="category-list"),
]

locations_patterns = [
    path("", LocationListView.as_view(), name="location-list"),
]

report_patterns = [
    path("lost/", LostItemsReportView.as_view(), name="lost-report"),
    path("found/", FoundItemsReportView.as_view(), name="found-report"),
    path("stats/", ItemStatusStatsView.as_view(), name="status-stats"),
    path("items/", ItemReportView.as_view(), name="item_report"),
    path(
        "unclaimed-item/",
        UnclaimedItemReportView.as_view(),
        name="unclaimed_item_report",
    ),
    path(
        "status-summary/", ItemStatusSummaryView.as_view(), name="status_summary_report"
    ),
    path(
        "trigger-expire/", TriggerExpirationView.as_view(), name="trigger_expire_report"
    ),
    path(
        "automatic-update-expired-items /",
        TaskResultView.as_view(),
        name="automatic_update_expired_items_report",
    ),
]

qrCode_patterns = [
    path("generate/", QRCodeGenerateView.as_view(), name="qr-generate"),
]

claims_patterns = [
    path("", ClaimCreateView.as_view(), name="claim-create"),
    path("my/", ClaimListView.as_view(), name="my-claims"),
    path("all/", AdminClaimListView.as_view(), name="all-claims"),
    path("<int:pk>/status/", ClaimStatusUpdateView.as_view(), name="claim-status"),
]

appointments_patterns = [
    path("", AppointmentCreateView.as_view(), name="create-appointment"),
    path(
        "<int:pk>/status/",
        AppointmentStatusUpdateView.as_view(),
        name="appointment-status",
    ),
    path("reminders/", AppointmentReminderView.as_view(), name="appointment-reminders"),
]

coupons_patterns = [
    path("", UserCouponListView.as_view(), name="user-coupons"),
    path("activate/", ActivateCouponView.as_view(), name="activate-coupon"),
    path("verify/", VerifyCouponView.as_view(), name="verify-coupon"),
    path("stats/", CouponStatsView.as_view(), name="coupon-stats"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include(auth_patterns)),
    path("admin/", include(admin_patterns)),
    path("items/", include(items_patterns)),
    path("categories/", include(categories_patterns)),
    path("locations/", include(locations_patterns)),
    path("reports/", include(report_patterns)),
    path("qr/", include(qrCode_patterns)),
    path("claims/", include(claims_patterns)),
    path("appointments/", include(appointments_patterns)),
    path("coupons/", include(coupons_patterns)),
]
