"""
Data verification and format conversion

How to use:
from api.serializers import UserRegistrationSerializer, ItemSerializer
"""

# Week 5 - User & Auth Serializers (Person D)
from .user_serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    # UserProfileSerializer,
    # PasswordResetRequestSerializer,
    # PasswordResetConfirmSerializer,
    # UserDetailSerializer,
    # UserListSerializer,
)

from .item_serializers import (
    ItemSerializer,
    # ItemCreateSerializer,
    # ItemUpdateSerializer,
    # ItemDetailSerializer,
    # ItemListSerializer,
    # CategorySerializer,
    # LocationSerializer,
    # ItemImageSerializer,
)

from .image_serializers import (
    ImageSerializer,
)


from .category_serializer import CategorySerializer

from .location_serializer import LocationSerializer


# # Week 6 & 7 - Claim Serializers (Person E)
# from .claim_serializers import (
#     ClaimSerializer,
#     ClaimCreateSerializer,
#     ClaimDetailSerializer,
#     ClaimStatusUpdateSerializer,
#     AppointmentSerializer,
#     AppointmentCreateSerializer,
#     AppointmentUpdateSerializer,
# )

# # Week 7 - Admin & Audit Serializers (Person D)
# from .admin_serializers import (
#     AuditQueueSerializer,
#     AuditActionSerializer,
#     AdminItemEditSerializer,
#     UserManagementSerializer,
# )

# # Week 7 - Report Serializers (Person D)
# from .report_serializers import (
#     ItemStatisticsSerializer,
#     UserStatisticsSerializer,
#     UnclaimedItemReportSerializer,
#     DashboardStatsSerializer,
#     CategoryStatsSerializer,
#     LocationStatsSerializer,
# )

# # Week 9 - Coupon Serializers (Person E)
# from .coupon_serializers import (
#     CouponSerializer,
#     CouponCreateSerializer,
#     CouponActivateSerializer,
#     CouponVerifySerializer,
#     CouponUsageSerializer,
#     MyCouponListSerializer,
# )

# # Week 9 - QR Code Serializers (Person D)
# from .qrcode_serializers import (
#     QRCodeSerializer,
#     QRCodeGenerateSerializer,
#     QRCodeVerifySerializer,
# )


__all__ = [
    # User & Auth
    "UserRegistrationSerializer",
    "UserLoginSerializer",
    "UserLogoutSerializer",
    # 'UserProfileSerializer',
    # 'PasswordResetRequestSerializer',
    # 'PasswordResetConfirmSerializer',
    # 'UserDetailSerializer',
    # 'UserListSerializer',
    # Items
    "ItemSerializer",
    "ImageSerializer",
    # 'ItemCreateSerializer',
    # 'ItemUpdateSerializer',
    # 'ItemDetailSerializer',
    # 'ItemListSerializer',
    # 'CategorySerializer',
    # 'LocationSerializer',
    # 'ItemImageSerializer',
    "CategorySerializer",
    "LocationSerializer",
    # Claims & Appointments
    # 'ClaimSerializer',
    # 'ClaimCreateSerializer',
    # 'ClaimDetailSerializer',
    # 'ClaimStatusUpdateSerializer',
    # 'AppointmentSerializer',
    # 'AppointmentCreateSerializer',
    # 'AppointmentUpdateSerializer',
    # Admin & Audit
    # 'AuditQueueSerializer',
    # 'AuditActionSerializer',
    # 'AdminItemEditSerializer',
    # 'UserManagementSerializer',
    # Reports
    # 'ItemStatisticsSerializer',
    # 'UserStatisticsSerializer',
    # 'UnclaimedItemReportSerializer',
    # 'DashboardStatsSerializer',
    # 'CategoryStatsSerializer',
    # 'LocationStatsSerializer',
    # Coupons
    # 'CouponSerializer',
    # 'CouponCreateSerializer',
    # 'CouponActivateSerializer',
    # 'CouponVerifySerializer',
    # 'CouponUsageSerializer',
    # 'MyCouponListSerializer',
    # QR Code
    # 'QRCodeSerializer',
    # 'QRCodeGenerateSerializer',
    # 'QRCodeVerifySerializer',
]
