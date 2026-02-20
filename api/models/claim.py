from django.db import models
from django.conf import settings


class Claim(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ]

    item = models.ForeignKey(
        "Item",
        on_delete=models.CASCADE,
        related_name="claims",
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="claims",
    )
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "claims"
        verbose_name = "Claim"
        verbose_name_plural = "Claims"
        indexes = [
            models.Index(fields=["status"], name="idx_claims_status"),
            models.Index(fields=["item"], name="idx_claims_item_id"),
            models.Index(fields=["claimant"], name="idx_claims_claimant_id"),
        ]

    def __str__(self):
        return f"Claim {self.id} on Item {self.item_id}"