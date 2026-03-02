import os
import io
import uuid
import imghdr
import struct
# ---

from PIL import Image as PilImage
from django.conf import settings
from django.core.exceptions import ValidationError

from api.models import Image

# ──────────────────────────────────────────
# Settings (override in settings.py if needed)
# ──────────────────────────────────────────
MAX_FILE_SIZE_MB = getattr(settings, "IMAGE_MAX_FILE_SIZE_MB", 3)
MAX_IMAGE_COUNT = getattr(settings, "IMAGE_MAX_COUNT", 1)
MAX_DIMENSION = getattr(settings, "IMAGE_MAX_DIMENSION", 1920)
ALLOWED_EXTENSIONS = getattr(settings, "IMAGE_ALLOWED_EXTENSIONS", {"jpg", "jpeg", "png", "webp"})
STORAGE_ROOT = getattr(settings, "IMAGE_STORAGE_ROOT", os.path.join(settings.MEDIA_ROOT, "items"))

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
        if header[:len(magic)] == magic:
            # Special case: RIFF must also contain WEBP at bytes 8-12
            if fmt == "webp" and header[8:12] != b"WEBP":
                continue
            is_valid = True
            break

    if not is_valid:
        raise ValidationError("File content does not match a valid image format.")


def validate_image_count(files):
    """Check the number of files being uploaded at once."""
    if len(files) > MAX_IMAGE_COUNT:
        raise ValidationError(f"Too many images. Max allowed per upload: {MAX_IMAGE_COUNT}.")


# ──────────────────────────────────────────
# 2. Optimization
# ──────────────────────────────────────────
# def optimize_image(file):
#     """
#     - Resize to max dimension (preserving aspect ratio)
#     - Convert to WebP
#     - Strip EXIF metadata
#     - Compress (quality=82)
#     Returns: BytesIO of the optimized image
#     """
#     img = PilImage.open(file)

#     # Strip EXIF by converting to RGB (drops all metadata)
#     if img.mode in ("RGBA", "P"):
#         img = img.convert("RGBA")
#     else:
#         img = img.convert("RGB")

#     # Resize if needed
#     w, h = img.size
#     if max(w, h) > MAX_DIMENSION:
#         ratio = MAX_DIMENSION / max(w, h)
#         img = img.resize((int(w * ratio), int(h * ratio)), PilImage.LANCZOS)

#     # Save as WebP to BytesIO
#     output = io.BytesIO()
#     img.save(output, format="WEBP", quality=82, method=6)
#     output.seek(0)
#     return output


# ──────────────────────────────────────────
# 3. Storage
# ──────────────────────────────────────────
def upload_to_storage(item_id, file):
    """
    Saves optimized image to local storage.
    Returns the relative file_path stored in DB.

    To switch to cloud (e.g. S3), replace only this function.
    """
    folder = os.path.join(STORAGE_ROOT, str(item_id))
    os.makedirs(folder, exist_ok=True)

    original_name = getattr(file, 'name', '')
    ext = os.path.splitext(original_name)[1].lower()  # e.g. '.jpg', '.png'
    
    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(folder, filename)

    with open(abs_path, "wb") as f:
        f.write(file.read())
    
    # Store relative path for portability
    rel_path = os.path.relpath(abs_path, settings.MEDIA_ROOT)
    return rel_path


def delete_from_storage(file_path):
    """Delete a file from local storage. Extend for cloud."""
    abs_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)


# ──────────────────────────────────────────
# 4. DB Record
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
# 5. Main entry points
# ──────────────────────────────────────────
def process_images(item, files):
    """
    Full pipeline for a list of uploaded files:
    validate → optimize → upload → save to DB
    
    The first image in the list is set as primary.
    Called inside a transaction from the view.
    """
    validate_image_count(files)

    saved_images = []
    for index, file in enumerate(files):
        validate_image(file)
        # optimized = optimize_image(file)
        file_path = upload_to_storage(item.id, file)
        is_primary = (index == 0)
        record = save_image_record(item, file_path, file.name, is_primary=is_primary)
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