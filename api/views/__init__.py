"""
Handling HTTP requests/responses
All view categories are exported centrally for easy referencing in urls.py.
"""
from .auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
)
from .item_views import (
    ItemListCreateView,
    ItemDetailView,
    # ItemViewSet,
    # CategoryListView,
    # LocationListView,
    # MyItemsView,
)
from .report_views import (
    ItemReportView,
    UnclaimedItemReportView,
    ItemStatusSummaryView,
    TriggerExpirationView,
    TaskResultView
)
from .category_views import CategoryListView
from .location_views import LocationListView


__all__ = [
    # Auth
    "RegisterView",
    "LoginView",
    "LogoutView",
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "UserProfileView",
    # Items
    "ItemListCreateView",
    "ItemDetailView",
    "LocationListView" "CategoryListView"
    # Reports
    "ItemReportView",
    "UnclaimedItemReportView",
    "ItemStatusSummaryView",
    "TriggerExpirationView",
    "TaskResultView"
]
