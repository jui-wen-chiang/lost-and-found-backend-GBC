from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from api.models import Item


class ItemStatisticsService:
    @staticmethod
    def get_dashboard_stats():
        status_dist = Item.objects.values("status").annotate(count=Count("id"))
        location_dist = Item.objects.values("location__name").annotate(
            count=Count("id")
        )

        # Comparison of Category Lost and Found
        category_stats = Item.objects.values("category__name").annotate(
            lost_count=Count("id", filter=Q(item_type="lost")),
            found_count=Count("id", filter=Q(item_type="found")),
        )

        # Monthly Lost and Found Trends (Which Month Has the Most Lost Items?)
        monthly_trend = (
            Item.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        # Success Rate: (Completed Cases / Total Cases) * 100
        total_items = Item.objects.count()
        completed_items = Item.objects.filter(status="completed").count()
        success_rate = (completed_items / total_items * 100) if total_items > 0 else 0

        return {
            "status": list(status_dist),
            "location": list(location_dist),
            "category_comparison": list(category_stats),
            "monthly_trend": list(monthly_trend),
            "kpi": {"success_rate": round(success_rate, 2), "total_count": total_items},
        }
