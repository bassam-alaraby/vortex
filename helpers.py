import imghdr
import os
from urllib.parse import urlparse

from flask import session, request, jsonify, flash, redirect, url_for, render_template
from werkzeug.utils import secure_filename


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png"}

DELIVERY_REGION_LABELS = {
    "menoufia": "المنوفية",
    "delta": "باقي محافظات الدلتا",
    "upper_egypt": "الصعيد",
}

DELIVERY_REGION_ORDER = ["menoufia", "delta", "upper_egypt"]

DELIVERY_FEE_SETTINGS = {
    "menoufia": ("delivery_fee_menoufia", 40),
    "delta": ("delivery_fee_delta", 80),
    "upper_egypt": ("delivery_fee_upper_egypt", 100),
}


def get_sizes():
    from routes.admin_routes import SIZES
    return SIZES


def get_cart():
    return session.get('cart', [])

def normalize_size(size):
    if not size:
        return None
    return str(size).strip().upper()

def get_cart_count(cart):
    return sum(item["quantity"] for item in cart)

def calculate_cart_total(cart, db):
    total = 0
    for item in cart:
        if item.get("is_custom"):
            unit_price = item.get("unit_price")

            if unit_price is None:
                row = db.execute("""
                    SELECT products.price
                    FROM variants
                    JOIN products ON variants.product_id = products.id
                    WHERE variants.id = ?
                """, item["variant_id"])

                if not row:
                    continue

                unit_price = float(row[0]["price"]) + get_custom_fee(db)

            total += float(unit_price) * item["quantity"]
            continue

        row = db.execute("""
            SELECT products.price
            FROM variants
            JOIN products ON variants.product_id = products.id
            WHERE variants.id = ?
        """, item["variant_id"])

        if not row:
            continue

        total += row[0]["price"] * item["quantity"]

    return total


def get_custom_fee(db):
    row = db.execute('SELECT value FROM settings WHERE key = "custom_fee"')
    if not row:
        return 0.0

    try:
        return float(row[0]["value"])
    except (TypeError, ValueError, KeyError):
        return 0.0


def get_delivery_fees(db):
    fees = {}
    for region_key, (setting_key, default_value) in DELIVERY_FEE_SETTINGS.items():
        row = db.execute('SELECT value FROM settings WHERE key = ?', setting_key)
        if not row:
            fees[region_key] = float(default_value)
            continue

        try:
            fees[region_key] = float(row[0]["value"])
        except (TypeError, ValueError, KeyError):
            fees[region_key] = float(default_value)

    return fees


def _safe_redirect(fallback_url):
    referrer = request.referrer
    if referrer:
        ref_host = urlparse(referrer).netloc
        own_host = urlparse(request.host_url).netloc
        if ref_host == own_host:
            return redirect(referrer)
    return redirect(fallback_url)


def validate_image_upload(file_obj):
    if not file_obj or not file_obj.filename:
        return None, "Image file is required."

    filename = secure_filename(file_obj.filename)
    if not filename:
        return None, "Invalid file name."

    extension = os.path.splitext(filename)[1].lower().lstrip(".")
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return None, "Only JPG and PNG images are allowed."

    if file_obj.mimetype not in ALLOWED_IMAGE_MIME_TYPES:
        return None, "Invalid image MIME type."

    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    file_obj.seek(0, 2)
    size = file_obj.tell()
    file_obj.seek(0)
    if size > MAX_IMAGE_SIZE:
        return None, "Image must be under 5MB."

    header = file_obj.read(512)
    file_obj.seek(0)
    detected = imghdr.what(None, h=header)
    if detected not in {"jpeg", "png"}:
        return None, "Invalid image file."

    return filename, None

def wants_json_response():
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.is_json
    )

def handle_cart_error(message, status_code):
    if wants_json_response():
        return jsonify({
            "success": False,
            "message": message
        }), status_code

    flash(message, "error")
    return redirect(request.referrer or url_for('collection'))

def render_error_response(status_code, template_name, title, message):
    if wants_json_response():
        return jsonify({
            "success": False,
            "message": message,
            "status_code": status_code
        }), status_code

    return render_template(
        template_name,
        error_title=title,
        error_message=message
    ), status_code
