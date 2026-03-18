import uuid

def generate_coupon_code():
    return str(uuid.uuid4()).replace("-", "")[:10].upper()