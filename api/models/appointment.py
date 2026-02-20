from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    claim = models.ForeignKey(
        "Claim",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        indexes = [
            models.Index(fields=["scheduled_at"], name="idx_appointments_scheduled_at"),
            models.Index(fields=["status"], name="idx_appointments_status"),
        ]

    def __str__(self):
        return f"Appointment {self.id} for Claim {self.claim_id}"