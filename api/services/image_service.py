import os
import io
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from api.models import Image
from supabase import create_client
import logging
from django.core.cache import cache

# ──────────────────────────────────────────
# Constants
# ──────────────────────────────────────────
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE_MB = 5
MAX_IMAGE_COUNT = 5
STORAGE_ROOT = os.path.join(settings.MEDIA_ROOT, "items")

CONTENT_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

# Magic bytes for supported formats
MAGIC_BYTES = {
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG": "png",
    b"RIFF": "webp",  # RIFF....WEBP
}

# ──────────────────────────────────────────
# 1. Validation
# ──────────────────────────────────────────
def validate_image(file):
    """
    Validates file extension, size, and magic bytes.
    Raises ValidationError on failure.
    """
    # Extension check
    ext = file.name.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported file type: .{ext}. Allowed: {ALLOWED_EXTENSIONS}")

    # Size check
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"File too large. Max size is {MAX_FILE_SIZE_MB}MB.")

    # Magic bytes check
    header = file.read(12)
    file.seek(0)  # Reset after reading

    is_valid = False
    for magic, fmt in MAGIC_BYTES.items():
        if header[: len(magic)] == magic:
            # Special case: RIFF must also contain WEBP at bytes 8–12
            if fmt == "webp" and header[8:12] != b"WEBP":
                continue
            is_valid = True
            break

    if not is_valid:
        raise ValidationError("File content does not match a valid image format.")


def validate_image_count(files):
    """Check the number of files being uploaded at once."""
    if len(files) > MAX_IMAGE_COUNT:
        raise ValidationError(
            f"Too many images. Max allowed per upload: {MAX_IMAGE_COUNT}."
        )


# ──────────────────────────────────────────
# 2. Storage backend (Automatically switches based on environment)
# ──────────────────────────────────────────
if getattr(settings, "USE_SUPABASE_STORAGE", False):
    # # ── Supabase Storage ──────────────────
    _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    _bucket = settings.SUPABASE_BUCKET
    logger = logging.getLogger(__name__)

    # Free plan limit: 1 GB
    SUPABASE_FREE_QUOTA_BYTES = getattr(
        settings, "SUPABASE_STORAGE_QUOTA_BYTES", 1 * 1024 * 1024 * 1024
    )
    SUPABASE_WARN_THRESHOLD  = getattr(settings, "SUPABASE_STORAGE_WARN_THRESHOLD",  0.8)
    SUPABASE_BLOCK_THRESHOLD = getattr(settings, "SUPABASE_STORAGE_BLOCK_THRESHOLD", 0.9)
 
    CACHE_KEY = "supabase_bucket_used_bytes"
    CACHE_TTL  = getattr(settings, "SUPABASE_STORAGE_CACHE_TTL", 300)

    def get_bucket_used_bytes(force_refresh=False):
        """
        Calculate the total size (in bytes) of all files within the bucket.
        The result is cached in CACHE_TTL seconds to avoid scanning every time an upload occurs.
        """
        if not force_refresh:
            cached = cache.get(CACHE_KEY)
            if cached is not None:
                return cached

        total = 0
        folders_to_visit = [""]

        while folders_to_visit:
            prefix = folders_to_visit.pop()
            items = _supabase.storage.from_(_bucket).list(prefix)
            for item in items:
                if item.get("id") is None:
                    sub_prefix = f"{prefix}/{item['name']}" if prefix else item["name"]
                    folders_to_visit.append(sub_prefix)
                else:
                    total += item.get("metadata", {}).get("size", 0)

        cache.set(CACHE_KEY, total, CACHE_TTL)
        return total
 
    def check_storage_quota(incoming_file_size_bytes):
        """
        Before uploading, check if there is enough space.
        Judgment benchmark: Estimated usage / quota after upload.
        """
        used = get_bucket_used_bytes()
        after_upload = used + incoming_file_size_bytes
        usage_ratio = after_upload / SUPABASE_FREE_QUOTA_BYTES
 
        used_mb  = used / (1024 * 1024)
        quota_mb = SUPABASE_FREE_QUOTA_BYTES / (1024 * 1024)
        file_mb  = incoming_file_size_bytes / (1024 * 1024)
 
        if usage_ratio >= SUPABASE_BLOCK_THRESHOLD:
            raise ValidationError(
                f"Storage is almost full ({usage_ratio * 100:.1f}% after upload). "
                f"Used: {used_mb:.1f} MB / {quota_mb:.0f} MB, "
                f"File: {file_mb:.1f} MB. "
                f"Please free up space before uploading."
            )
 
        if usage_ratio >= SUPABASE_WARN_THRESHOLD:
            logger.warning(
                f"[Storage] Usage at {usage_ratio * 100:.1f}% after this upload "
                f"({used_mb:.1f} MB used / {quota_mb:.0f} MB). "
                f"Approaching block threshold ({SUPABASE_BLOCK_THRESHOLD * 100:.0f}%)."
            )
 
    def upload_to_storage(item_id, file):
        ext = os.path.splitext(getattr(file, "name", ""))[1].lower()
        object_path = f"{item_id}/{uuid.uuid4().hex}{ext}"
        content_type = CONTENT_TYPE_MAP.get(ext, "application/octet-stream")
 
        # Quota check before uploading
        check_storage_quota(file.size)
 
        file.seek(0)
        _supabase.storage.from_(_bucket).upload(
            path=object_path,
            file=file.read(),
            file_options={"content-type": content_type},
        )
        return object_path
 
    def delete_from_storage(file_path):
        _supabase.storage.from_(_bucket).remove([file_path])
        cache.delete(CACHE_KEY)
 
    def get_image_url(file_path):
        """
        Return the public Supabase URL.
        If the bucket is private, use create_signed_url instead.
        """
        return _supabase.storage.from_(_bucket).get_public_url(file_path)
 
    def get_storage_usage():
        """
        Report the current storage usage status for admin or debug users to view.
        """
        used = get_bucket_used_bytes()
        quota = SUPABASE_FREE_QUOTA_BYTES
        return {
            "used_mb": round(used / (1024 * 1024), 2),
            "quota_mb": round(quota / (1024 * 1024), 2),
            "usage_percent": round(used / quota * 100, 1),
            "remaining_mb": round((quota - used) / (1024 * 1024), 2),
        }

else:
    # ── Local Storage ─────────────────────
    def upload_to_storage(item_id, file):
        """
        Saves optimized image to local storage.
        Returns the relative file_path stored in DB.
        """
        folder = os.path.join(STORAGE_ROOT, str(item_id))
        os.makedirs(folder, exist_ok=True)

        ext = os.path.splitext(getattr(file, "name", ""))[1].lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        abs_path = os.path.join(folder, filename)

        file.seek(0)
        with open(abs_path, "wb") as f:
            for chunk in file.chunks() if hasattr(file, "chunks") else [file.read()]:
                f.write(chunk)

        return os.path.relpath(abs_path, settings.MEDIA_ROOT)

    def delete_from_storage(file_path):
        abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(abs_path):
            os.remove(abs_path)

    def get_image_url(file_path):
        return f"{settings.MEDIA_URL}{file_path}"


# ──────────────────────────────────────────
# 3. DB Record
# ──────────────────────────────────────────
def save_image_record(item, file_path, original_filename, is_primary=False):
    """Create an Image record in the database."""
    return Image.objects.create(
        item=item,
        file_path=file_path,
        original_filename=original_filename,
        is_primary=is_primary,
    )


def ensure_single_primary(item):
    """
    Make sure only one image is is_primary=True for a given item.
    If none is marked primary, set the first one.
    """
    images = Image.objects.filter(item=item)
    primary_images = images.filter(is_primary=True)

    if primary_images.count() > 1:
        # Keep only the first primary
        keep = primary_images.first()
        primary_images.exclude(pk=keep.pk).update(is_primary=False)
    elif primary_images.count() == 0 and images.exists():
        images.first().update(is_primary=True)


# ──────────────────────────────────────────
# 4. Main entry points
# ──────────────────────────────────────────
def process_images(item, files):
    """
    Full pipeline for a list of uploaded files:
    validate → upload → save to DB

    The first image in the list is set as primary.
    Called inside a transaction from the view.
    """
    validate_image_count(files)

    saved_images = []
    for index, file in enumerate(files):
        validate_image(file)
        file.seek(0)
        file_path = upload_to_storage(item.id, file)
        is_primary = index == 0
        record = save_image_record(
            item, file_path, file.name, is_primary=is_primary
        )
        saved_images.append(record)

    return saved_images


def delete_images_by_item(item):
    """
    Delete all images (files + DB records) for an item.
    Used during item update (full replace strategy).
    """
    images = Image.objects.filter(item=item)
    for image in images:
        delete_from_storage(image.file_path)
    images.delete()