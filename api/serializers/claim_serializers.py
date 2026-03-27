from rest_framework import serializers
from api.models import Claim


class ClaimSerializer(serializers.ModelSerializer):

    class Meta:
        model = Claim
        fields = [
            "id",
            "item",
            "claimant",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "claimant", "created_at"]


class ClaimStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Claim
        fields = ["status"]