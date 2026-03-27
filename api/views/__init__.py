"""
Handling HTTP requests/responses
All view categories are exported centrally for easy referencing in urls.py.
"""

from .auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)
from .item_views import (
    ItemListCreateView,
    ItemDetailView,
    LostItemsReportView,
    LostItemsReportView,
    FoundItemsReportView,
    ItemStatusStatsView,
)
from .admin_views import (
    AuditQueueView,
    ApprovePostView,
    RejectPostView,
    AdminDeletePostView,
    AdminEditPostView,
)
from .report_views import (
    ItemReportView,
    UnclaimedItemReportView,
    ItemStatusSummaryView,
    TriggerExpirationView,
    TaskResultView,
)
from .item_qrcode_views import QRCodeGenerateView, QRCodeVerifyView
from .category_views import CategoryListView
from .location_views import LocationListView

from .claim_views import ClaimCreateView, ClaimListView, ClaimStatusUpdateView
from .appointment_views import (
    AppointmentCreateView,
    AppointmentStatusUpdateView,
    AppointmentReminderView,
)
from .coupon_views import (
    UserCouponListView,
    ActivateCouponView,
    VerifyCouponView,
    CouponStatsView,
)


__all__ = [
    # Auth
    "RegisterView",
    "LoginView",
    "LogoutView",
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "UserProfileView",
    # Admin
    "AuditQueueView",
    "ApprovePostView",
    "RejectPostView",
    "AdminDeletePostView",
    "AdminEditPostView",
    # Items
    "ItemListCreateView",
    "ItemDetailView",
    "LostItemsReportView",
    "FoundItemsReportView",
    "ItemStatusStatsView",
    # Category & Location
    "LocationListView",
    "CategoryListView",
    # Reports
    "ItemReportView",
    "UnclaimedItemReportView",
    "ItemStatusSummaryView",
    "TriggerExpirationView",
    "TaskResultView",
    # QRCode
    "QRCodeGenerateView",
    "QRCodeVerifyView",
    # Claim
    "ClaimCreateView",
    "ClaimListView",
    "ClaimStatusUpdateView",
    # Appointment
    "AppointmentCreateView",
    "AppointmentStatusUpdateView",
    "AppointmentReminderView",
    # Coupon
    UserCouponListView,
    ActivateCouponView,
    VerifyCouponView,
    CouponStatsView,
]
