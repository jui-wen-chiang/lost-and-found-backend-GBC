from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from api.models import Coupon
from api.models import CouponUsage
from api.permissions.rbac import IsAppAdmin


class UserCouponListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        coupons = Coupon.objects.filter(user=request.user)

        data = [
            {
                "id": c.id,
                "code": c.code,
                "is_redeemed": c.is_redeemed,
                "expires_at": c.expires_at
            }
            for c in coupons
        ]

        return Response(data)
    
class ActivateCouponView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")

        try:
            coupon = Coupon.objects.get(code=code, user=request.user)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon"}, status=404)

        if coupon.is_redeemed:
            return Response({"error": "Already used"}, status=400)

        coupon.is_redeemed = True
        coupon.save()
        
        CouponUsage.objects.create(
        coupon=coupon,
        user=request.user)

        return Response({"message": "Coupon activated"})
    

class VerifyCouponView(APIView):
    permission_classes = [IsAppAdmin]

    def post(self, request):
        code = request.data.get("code")

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({"valid": False})

        if coupon.is_redeemed:
            return Response({"valid": False, "reason": "Already used"})

        return Response({"valid": True})


class CouponStatsView(APIView):
    permission_classes = [IsAppAdmin]

    def get(self, request):

        total = Coupon.objects.count()
        used = Coupon.objects.filter(is_redeemed=True).count()
        expired = Coupon.objects.filter(is_expired=True).count()

        return Response({
            "total_coupons": total,
            "used_coupons": used,
            "expired_coupons": expired,
        })