from rest_framework import serializers
from api.models import Claim


class ClaimSerializer(serializers.ModelSerializer):
    item_type = serializers.CharField(source="item.item_type", read_only=True)
    item_title = serializers.CharField(source="item.title", read_only=True)

    class Meta:
        model = Claim
        fields = [
            "id",
            "item",
            "item_type",
            "item_title",
            "claimant",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "claimant", "created_at", "item_type", "item_title"]


class ClaimStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Claim
        fields = ["status"]