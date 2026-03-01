from rest_framework.views import APIView
from rest_framework.response import Response
from api.services import ItemStatisticsService

class ItemReportView(APIView):
    """
    Obtain statistical data from the lost and found platform. 
    Return comprehensive statistical data for dashboard display.
    """
    def get(self, request):
        stats = ItemStatisticsService.get_dashboard_stats()
        return Response(stats)