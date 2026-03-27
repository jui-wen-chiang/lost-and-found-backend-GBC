from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from api.models import Claim, Item
from api.serializers.claim_serializers import ClaimSerializer, ClaimStatusUpdateSerializer
from api.models import Coupon
from api.utils.coupon_utils import generate_coupon_code

class ClaimCreateView(generics.CreateAPIView):
    """
    Submit a claim request for an item
    """
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        item = serializer.validated_data["item"]

        # verification logic
        if Claim.objects.filter(item=item, status="approved").exists():
            raise ValidationError("This item has already been claimed.")

        serializer.save(claimant=self.request.user)


class ClaimListView(generics.ListAPIView):
    """
    View my claims
    """
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Claim.objects.filter(claimant=self.request.user)


class ClaimStatusUpdateView(generics.UpdateAPIView):

    queryset = Claim.objects.all()
    serializer_class = ClaimStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    def perform_update(self, serializer):
        claim = serializer.save()

        if claim.status == "completed":
            if not Coupon.objects.filter(user=claim.claimant, claim=claim).exists():
                Coupon.objects.create(
                    user=claim.claimant,
                    claim=claim,
                    code=generate_coupon_code(),
                    expires_at=timezone.now() + timedelta(days=7)
                )


from api.models import Appointment


class AppointmentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        claim_id = request.data.get("claim")
        scheduled_at = request.data.get("scheduled_at")

        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            return Response({"error": "Claim not found"}, status=404)

        # check claim approved
        if claim.status != "approved":
            return Response({"error": "Claim must be approved first"}, status=400)

        # conflict detection
        if Appointment.objects.filter(scheduled_at=scheduled_at).exists():
            return Response({"error": "Time slot already booked"}, status=400)

        appointment = Appointment.objects.create(
            claim=claim,
            scheduled_at=scheduled_at
        )

        return Response({
            "message": "Appointment scheduled",
            "appointment_id": appointment.id
        })



class AppointmentStatusUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=404)

        status_value = request.data.get("status")

        if status_value not in ["approved", "rejected", "completed"]:
            return Response({"error": "Invalid status"}, status=400)

        appointment.status = status_value
        appointment.save()

        return Response({
            "message": "Appointment status updated",
            "status": appointment.status
        })
    



from django.utils import timezone
from datetime import timedelta


class AppointmentReminderView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):

        upcoming = timezone.now() + timedelta(hours=24)

        appointments = Appointment.objects.filter(
            scheduled_at__lte=upcoming
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