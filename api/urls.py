from django.urls import path

from api.views.auth_views import RegisterView, LoginView, LogoutView

from api.views.item_views import (
health,
CategoryListView,
LocationListView,
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
)

from api.views.claim_views import (
ClaimCreateView,
ClaimListView,
ClaimStatusUpdateView,
AppointmentCreateView,
AppointmentStatusUpdateView,
AppointmentReminderView,
)

urlpatterns = [


# -------- Health Check --------
path("health/", health, name="health"),

# -------- Auth --------
path("auth/register/", RegisterView.as_view(), name="register"),
path("auth/login/", LoginView.as_view(), name="login"),
path("auth/logout/", LogoutView.as_view(), name="logout"),

# -------- Categories & Locations --------
path("categories/", CategoryListView.as_view(), name="category-list"),
path("locations/", LocationListView.as_view(), name="location-list"),

# -------- Items CRUD --------
path("items/", ItemListCreateView.as_view(), name="item-list-create"),
path("items/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),

# -------- Reports --------
path("reports/lost/", LostItemsReportView.as_view(), name="lost-report"),
path("reports/found/", FoundItemsReportView.as_view(), name="found-report"),
path("reports/stats/", ItemStatusStatsView.as_view(), name="status-stats"),


path("admin/audit/posts/", AuditQueueView.as_view(), name="audit-queue"),
path("admin/items/<int:pk>/approve/", ApprovePostView.as_view(), name="approve-post"),
path("admin/items/<int:pk>/reject/", RejectPostView.as_view(), name="reject-post"),
path("admin/items/<int:pk>/delete/", AdminDeletePostView.as_view(), name="delete-post"),
path("admin/items/<int:pk>/edit/", AdminEditPostView.as_view(), name="edit-post"),

# -------- Claims --------
path("claims/", ClaimCreateView.as_view(), name="claim-create"),
path("claims/my/", ClaimListView.as_view(), name="my-claims"),
path("claims/<int:pk>/status/", ClaimStatusUpdateView.as_view(), name="claim-status"),

#----------appointments-------
path("appointments/", AppointmentCreateView.as_view(), name="create-appointment"),
path("appointments/<int:pk>/status/", AppointmentStatusUpdateView.as_view(), name="appointment-status"),
path("appointments/reminders/", AppointmentReminderView.as_view(), name="appointment-reminders"),
]
