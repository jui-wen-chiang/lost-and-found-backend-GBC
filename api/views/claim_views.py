from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.models import Claim, Item
from api.serializers.claim_serializers import ClaimSerializer, ClaimStatusUpdateSerializer


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
    """
    Admin updates claim status
    """
    queryset = Claim.objects.all()
    serializer_class = ClaimStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]