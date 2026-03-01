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