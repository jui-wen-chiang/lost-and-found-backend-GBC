
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from api.models import Claim, Coupon
from api.models import Appointment
from api.permissions.rbac import IsAppAdmin
from api.utils.coupon_utils import generate_coupon_code


class AppointmentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List appointments — admins see all, regular users see their own."""
        if getattr(request.user, "role", None) == "admin":
            appointments = Appointment.objects.all().order_by("-scheduled_at")
        else:
            appointments = Appointment.objects.filter(
                claim__claimant=request.user
            ).order_by("-scheduled_at")

        data = [
            {
                "id": a.id,
                "claim": a.claim_id,
                "location": a.location_id,
                "scheduled_at": a.scheduled_at.isoformat() if a.scheduled_at else None,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            }
            for a in appointments
        ]
        return Response(data)

    def post(self, request):

        claim_id = request.data.get("claim")
        scheduled_at = request.data.get("scheduled_at")
        location_id = request.data.get("location")

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            return Response({"error": "Claim not found"}, status=404)

        # Only the claimant can schedule their own appointment
        if claim.claimant != request.user:
            return Response({"error": "You can only schedule appointments for your own claims."}, status=403)

        # Claim must be approved
        if claim.status != "approved":
            return Response({"error": "Claim must be approved first"}, status=400)

        # Only one appointment per claim
        if Appointment.objects.filter(claim=claim).exclude(status="cancelled").exists():
            return Response({"error": "An appointment already exists for this claim."}, status=400)

        # Appointment must be in the future
        try:
            scheduled_dt = timezone.datetime.fromisoformat(scheduled_at)
            if timezone.is_naive(scheduled_dt):
                scheduled_dt = timezone.make_aware(scheduled_dt)
        except (TypeError, ValueError):
            return Response({"error": "Invalid date format."}, status=400)

        if scheduled_dt <= timezone.now():
            return Response({"error": "Appointment must be scheduled in the future."}, status=400)

        # Conflict detection
        if Appointment.objects.filter(scheduled_at=scheduled_dt).exclude(status="cancelled").exists():
            return Response({"error": "Time slot already booked"}, status=400)

        appointment = Appointment.objects.create(
            claim=claim,
            scheduled_at=scheduled_dt,
            location_id=location_id if location_id else None,
        )

        return Response({
            "message": "Appointment scheduled",
            "appointment_id": appointment.id
        })



class AppointmentStatusUpdateView(APIView):
    permission_classes = [IsAppAdmin]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=404)

        status_value = request.data.get("status")

        if status_value not in ["cancelled", "completed"]:
            return Response({"error": "Invalid status. Must be 'cancelled' or 'completed'."}, status=400)

        with transaction.atomic():
            appointment.status = status_value
            appointment.save()

            # When appointment is completed, also complete the claim, update item, and issue coupon
            if status_value == "completed":
                claim = appointment.claim
                if claim and claim.status != "completed":
                    claim.status = "completed"
                    claim.save()
                    # Mark the item as completed (returned)
                    if claim.item and claim.item.status != "completed":
                        claim.item.status = "completed"
                        claim.item.save()
                    # Auto-issue coupon to the item owner (finder/poster)
                    if not Coupon.objects.filter(claim=claim).exists():
                        Coupon.objects.create(
                            user=claim.item.owner if claim.item else claim.claimant,
                            claim=claim,
                            code=generate_coupon_code(),
                            expires_at=timezone.now() + timedelta(days=7),
                        )

        return Response({
            "message": "Appointment status updated",
            "status": appointment.status
        })


class AppointmentReminderView(APIView):
    permission_classes = [IsAppAdmin]

    def get(self, request):

        now = timezone.now()
        upcoming = now + timedelta(hours=24)

        appointments = Appointment.objects.filter(
            scheduled_at__gte=now,
            scheduled_at__lte=upcoming,
            status="scheduled",
        )

        data = [
            {
                "appointment_id": a.id,
                "scheduled_at": a.scheduled_at
            }
            for a in appointments
        ]

        return Response({
            "reminders": data
        })
