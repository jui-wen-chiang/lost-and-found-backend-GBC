from django.utils import timezone
from django.db.models import ExpressionWrapper, F, DateTimeField, FloatField
from django.db.models.functions import Cast
from datetime import timedelta
from api.models import Item
from django.db.models import F, FloatField, ExpressionWrapper, DateTimeField
from django.db.models.functions import Cast, Extract

class ReportUtils:
    def get_unclaimed_expired_items():
        now = timezone.now()

        expire_at_expr = ExpressionWrapper(
            F("created_at") + timedelta(days=1) * Cast(F("category__expires_day"), FloatField()),
            output_field=DateTimeField()
        )

        return Item.objects.filter(
            status="approved",
            item_type="found",
        ).annotate(
            expire_at=expire_at_expr,
        ).filter(
            expire_at__lt=now
        ).annotate(
            days_overdue=ExpressionWrapper(
                Extract(now - F("expire_at"), "epoch") / 86400.0,
                output_field=FloatField()
            )
        ).select_related("category", "location", "owner")
    

    @staticmethod
    def auto_expire_items() -> dict:
        """
        Scan all approved found items that have exceeded their retention period;
        the batch update status is now expired.
        Return an execution summary for use in the log or API response.
        """
        now = timezone.now()

        expire_at_expr = ExpressionWrapper(
            F("created_at") + timedelta(days=1) * Cast(F("category__expires_day"), FloatField()),
            output_field=DateTimeField()
        )

        # Find all items that should expire.
        target_qs = Item.objects.filter(
            status="approved",
            item_type="found",
        ).annotate(
            expire_at=expire_at_expr,
        ).filter(
            expire_at__lt=now
        )

        expired_count = target_qs.count()

        # Batch updates (performance priority, no individual saves)
        target_qs.update(
            status="expired",
            updated_at=now,
        )

        return {
            "executed_at": now.isoformat(),
            "expired_count": expired_count,
        }


    @staticmethod
    def get_status_summary() -> dict:
        """Return the item quantity statistics for each state"""
        from django.db.models import Count

        counts = (
            Item.objects.filter(item_type="found")
            .values("status")
            .annotate(count=Count("id"))
        )
        return {row["status"]: row["count"] for row in counts}