from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_celery_results.models import TaskResult
from api.permissions.rbac import RoleBasedPermission
from api.serializers import ItemSerializer
from api.utils import ItemStatisticsService, ReportUtils

class ItemReportView(APIView):
    """
    Obtain statistical data from the lost and found platform.
    Return comprehensive statistical data for dashboard display.
    """

    permission_classes = [RoleBasedPermission]
    allowed_roles = ["admin"]

    def get(self, request):
        stats = ItemStatisticsService.get_dashboard_stats()
        return Response(stats)


class UnclaimedItemReportView(APIView):
    permission_classes = [RoleBasedPermission]
    allowed_roles = ["admin"]

    def get(self, request):
        items = ReportUtils.get_unclaimed_expired_items()

        items_data = []
        for item in items:
            item_dict = ItemSerializer(item).data
            item_dict["expire_at"] = item.expire_at
            item_dict["days_overdue"] = round(item.days_overdue, 1)
            items_data.append(item_dict)

        return Response({"count": items.count(), "items": items_data})

class ItemStatusSummaryView(APIView):
    """
    Return the status distribution of all found items.
    This corresponds to the Item Status Tracking System requirement.
    """
    permission_classes = [RoleBasedPermission]
    allowed_roles = ["admin"]

    def get(self, request):
        summary = ReportUtils.get_status_summary()
        return Response({
            "status_summary": summary,
            "total": sum(summary.values()),
        })

class TriggerExpirationView(APIView):
    """
    The Admin can manually trigger an expiration scan once,
    which is normally executed automatically by a Celery cron job.
    """
    permission_classes = [RoleBasedPermission]
    allowed_roles = ["admin"]

    def post(self, request):
        result = ReportUtils.auto_expire_items()
        return Response(result, status=status.HTTP_200_OK)

class TaskResultView(APIView):
    """View Celery schedule execution records"""
    permission_classes = [RoleBasedPermission]
    allowed_roles = ["admin"]

    def get(self, request):
        results = (
            TaskResult.objects
            .filter(task_name="api.tasks.scheduled_auto_expire")
            .order_by("-date_done")[:30]
            .values("status", "date_done", "result")
        )
        return Response(list(results))