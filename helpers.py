from flask import session, request, jsonify, flash, redirect, url_for, render_template


def get_sizes():
    from routes.admin_routes import SIZES
    return SIZES


def get_cart():
    # Return cart list from session or empty
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
    # Redirects back to previous page or collection if no referrer
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
