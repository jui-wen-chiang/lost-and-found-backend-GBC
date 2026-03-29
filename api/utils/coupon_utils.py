import uuid
from django.db import IntegrityError


def generate_coupon_code():
    """Generate a unique 16-char coupon code. Retries on the rare collision."""
    for _ in range(5):
        code = str(uuid.uuid4()).replace("-", "")[:16].upper()
        try:
            # Import here to avoid circular imports
            from api.models import Coupon
            if not Coupon.objects.filter(code=code).exists():
                return code
        except Exception:
            return code
    # Fallback: full UUID without dashes (32 chars, virtually no collision risk)
    return str(uuid.uuid4()).replace("-", "").upper()
