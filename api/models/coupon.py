from django.db import models
from django.conf import settings


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coupons",
    )
    claim = models.ForeignKey(
        "Claim",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coupons",
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "coupons"
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        indexes = [
            models.Index(fields=["code"], name="idx_coupons_code"),
            models.Index(fields=["is_redeemed"], name="idx_coupons_is_redeemed"),
            models.Index(fields=["expires_at"], name="idx_coupons_expires_at"),
        ]

    def __str__(self):
        return self.code