import os
import uuid

from django.core.files.storage import default_storage
from django.utils.text import slugify
from PIL import Image


def generate_unique_filename(instance, filename):
    """Generate unique filename with UUID"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return filename


def resize_image(image_path, max_width=800, max_height=600):
    """Resize image while maintaining aspect ratio"""
    with Image.open(image_path) as img:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        img.save(image_path, optimize=True, quality=85)


def create_slug(text):
    """Create URL-friendly slug from text"""
    return slugify(text)


def calculate_age(birth_date):
    """Calculate age from birth date"""
    from datetime import date

    today = date.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


class FileUploadHelper:
    """Helper class for file upload operations"""

    @staticmethod
    def validate_image(image):
        """Validate uploaded image"""
        if image.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValueError("Image size must be less than 5MB")

        valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in valid_extensions:
            raise ValueError("Invalid image format")

    @staticmethod
    def validate_video(video):
        """Validate uploaded video"""
        if video.size > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError("Video size must be less than 100MB")

        valid_extensions = [".mp4", ".avi", ".mov", ".wmv"]
        ext = os.path.splitext(video.name)[1].lower()
        if ext not in valid_extensions:
            raise ValueError("Invalid video format")
