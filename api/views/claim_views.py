from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from api.utils.coupon_utils import generate_coupon_code
from api.models import Claim
from api.serializers.claim_serializers import ClaimSerializer, ClaimStatusUpdateSerializer
from api.models import Coupon
from api.permissions.rbac import IsAppAdmin

class ClaimCreateView(generics.CreateAPIView):
    """
    Submit a claim request for an item
    """
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        item = serializer.validated_data["item"]

        if item.owner == self.request.user:
            raise ValidationError("You cannot claim your own item.")

        if item.status != "approved":
            raise ValidationError("This item is not available for claiming.")

        if Claim.objects.filter(item=item, status="approved").exists():
            raise ValidationError("This item has already been claimed.")

        if Claim.objects.filter(item=item, claimant=self.request.user).exclude(status="rejected").exists():
            raise ValidationError("You already have an active claim on this item.")

        serializer.save(claimant=self.request.user)


class ClaimListView(generics.ListAPIView):
    """
    View my claims
    """
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Claim.objects.filter(claimant=self.request.user)


class AdminClaimListView(generics.ListAPIView):
    """
    Admin: view all claims
    """
    serializer_class = ClaimSerializer
    permission_classes = [IsAppAdmin]

    def get_queryset(self):
        return Claim.objects.all().order_by("-created_at")


class ClaimStatusUpdateView(generics.UpdateAPIView):

    queryset = Claim.objects.all()
    serializer_class = ClaimStatusUpdateSerializer
    permission_classes = [IsAppAdmin]

    VALID_TRANSITIONS = {
        "pending": {"approved", "rejected"},
        "approved": {"completed", "rejected"},
        "rejected": set(),
        "completed": set(),
    }

    def perform_update(self, serializer):
        claim = self.get_object()
        new_status = serializer.validated_data.get("status", claim.status)
        allowed = self.VALID_TRANSITIONS.get(claim.status, set())
        if new_status != claim.status and new_status not in allowed:
            raise ValidationError(
                f"Cannot transition claim from '{claim.status}' to '{new_status}'."
            )

        with transaction.atomic():
            claim = serializer.save()

            if claim.status == "approved":
                if claim.item and claim.item.status != "claimed":
                    claim.item.status = "claimed"
                    claim.item.save()

            if claim.status == "completed":
                if claim.item and claim.item.status != "completed":
                    claim.item.status = "completed"
                    claim.item.save()
                coupon_recipient = claim.item.owner if claim.item else claim.claimant
                if not Coupon.objects.filter(claim=claim).exists():
                    Coupon.objects.create(
                        user=coupon_recipient,
                        claim=claim,
                        code=generate_coupon_code(),
                        expires_at=timezone.now() + timedelta(days=7)
                    )
