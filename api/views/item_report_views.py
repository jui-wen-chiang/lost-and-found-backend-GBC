from rest_framework.views import APIView
from rest_framework.response import Response
from api.services import ItemStatisticsService
from api.permissions.rbac import RoleBasedPermission
from api.serializers import ItemSerializer
from api.utils.report_utils import get_unclaimed_expired_items

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
        items = get_unclaimed_expired_items()
        serializer = ItemSerializer(items, many=True)

        items_data = []
        for item in items:
            item_dict = ItemSerializer(item).data
            item_dict["expire_at"] = item.expire_at
            item_dict["days_overdue"] = round(item.days_overdue, 1)
            items_data.append(item_dict)

        return Response({
            "count": items.count(),
            "items": items_data
        })