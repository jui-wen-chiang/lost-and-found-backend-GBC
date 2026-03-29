from django.db import models
from django.conf import settings


class Item(models.Model):
    ITEM_TYPE_CHOICES = [
        ("lost", "Lost"),
        ("found", "Found"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("claimed", "Claimed"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    category = models.ForeignKey(
        "Category",
        on_delete=models.RESTRICT,
        related_name="items",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.RESTRICT,
        related_name="items",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items",
    )
    lost_at = models.DateTimeField(null=True, blank=True)
    found_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "items"
        verbose_name = "Item"
        verbose_name_plural = "Items"
        indexes = [
            models.Index(fields=["item_type"], name="idx_items_item_type"),
            models.Index(fields=["status"], name="idx_items_status"),
            models.Index(fields=["created_at"], name="idx_items_created_at"),
            models.Index(fields=["category", "location"], name="idx_items_category_location"),
        ]

    def __str__(self):
        return f"[{self.item_type}] {self.title}"