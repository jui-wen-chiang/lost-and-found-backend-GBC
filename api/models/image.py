from django.db import models


class Image(models.Model):
    item = models.ForeignKey(
        "Item",
        on_delete=models.CASCADE,
        related_name="images",
    )
    file_path = models.CharField(max_length=500)
    original_filename = models.CharField(max_length=500)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "images"
        verbose_name = "Image"
        verbose_name_plural = "Images"
        indexes = [
            models.Index(fields=["item"], name="idx_images_item_id"),
            models.Index(fields=["is_primary"], name="idx_images_is_primary"),
        ]

    def __str__(self):
        return f"Image {self.id} for Item {self.item_id}"