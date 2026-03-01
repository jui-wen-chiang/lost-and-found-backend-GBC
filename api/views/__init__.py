"""
Handling HTTP requests/responses
All view categories are exported centrally for easy referencing in urls.py.
"""

# Authentication & Items
from .auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
    # PasswordResetRequestView,
    # PasswordResetConfirmView,
    # UserProfileView,
)

from .item_views import (
    ItemListCreateView,
    ItemDetailView,
    # ItemViewSet,
    # CategoryListView,
    # LocationListView,
    # MyItemsView,
)

from .item_report_views import ItemReportView

# from .claim_views import (
#     ClaimViewSet,
#     AppointmentViewSet,
#     MyClaimsView,
# )

# from .admin_views import (
#     AuditQueueViewSet,
#     AdminDashboardView,
#     UserManagementViewSet,
# )

# from .report_views import (
#     ItemStatisticsView,
#     UserStatisticsView,
#     UnclaimedItemReportView,
#     ExportReportView,
# )

# from .coupon_views import (
#     CouponViewSet,
#     MyCouponsView,
#     CouponActivateView,
#     CouponVerifyView,
# )

__all__ = [
    # Auth
    "RegisterView",
    "LoginView",
    "LogoutView",
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "UserProfileView",
    # # Items
    "ItemListCreateView",
    "ItemDetailView",
    # 'LocationListView',
    # 'MyItemsView',

    # # Claims
    # 'ClaimViewSet',
    # 'AppointmentViewSet',
    # 'MyClaimsView',
    
    # # Admin
    # 'AuditQueueViewSet',
    # 'AdminDashboardView',
    # 'UserManagementViewSet',

    # # Reports
    "ItemReportView",
    # 'ItemStatisticsView',
    # 'UserStatisticsView',
    # 'UnclaimedItemReportView',
    # 'ExportReportView',
    # # Coupons
    # 'CouponViewSet',
    # 'MyCouponsView',
    # 'CouponActivateView',
    # 'CouponVerifyView',
]
