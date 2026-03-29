from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone
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
