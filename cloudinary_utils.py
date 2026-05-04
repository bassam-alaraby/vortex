import os

import cloudinary
import cloudinary.uploader
from cloudinary import CloudinaryImage


_CLOUDINARY_ENV_KEYS = (
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
)


def configure_cloudinary():
    missing = [key for key in _CLOUDINARY_ENV_KEYS if not os.environ.get(key)]
    if missing:
        missing_display = ", ".join(missing)
        raise RuntimeError(f"Missing Cloudinary configuration: {missing_display}")

    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True,
    )


def cloudinary_image_url(public_id):
    if not public_id:
        return ""
    return CloudinaryImage(public_id).build_url(
        fetch_format="auto",
        quality="auto",
        secure=True,
    )


def cloudinary_download_url(public_id, filename=None):
    if not public_id:
        return ""

    options = {
        "fetch_format": "auto",
        "quality": "auto",
        "secure": True,
        "flags": "attachment",
    }

    if filename:
        options["filename"] = filename

    return CloudinaryImage(public_id).build_url(**options)


def upload_image(file_storage):
    result = cloudinary.uploader.upload(file_storage, resource_type="image")
    return result.get("public_id")
