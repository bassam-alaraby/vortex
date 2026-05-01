from flask import request, session, jsonify, redirect, flash, render_template, url_for
import re

from helpers import (
    get_cart, normalize_size, get_cart_count, handle_cart_error,
    calculate_cart_total, wants_json_response
)
from cloudinary_utils import cloudinary_image_url


ARABIC_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
EASTERN_ARABIC_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
NAME_PATTERN = re.compile(r"^[A-Za-z\u0600-\u06FF\s]+$")


def normalize_spaces(value):
    return " ".join((value or "").strip().split())


def normalize_phone(value):
    phone = (value or "").strip()
    phone = phone.translate(ARABIC_INDIC_DIGITS)
    phone = phone.translate(EASTERN_ARABIC_DIGITS)
    phone = "".join(phone.split())
    return phone


def validate_checkout_input(name, phone, address, notes):
    errors = {}

    if not name:
        errors["name"] = "يرجى إدخال الاسم."
    elif len(name) < 2:
        errors["name"] = "الاسم قصير جدًا."
    elif len(name) > 60:
        errors["name"] = "الاسم طويل جدًا."
    elif not NAME_PATTERN.fullmatch(name):
        errors["name"] = "الاسم يجب أن يحتوي على حروف ومسافات فقط."

    if not phone:
        errors["phone"] = "يرجى إدخال رقم الهاتف."
    elif not phone.isdigit():
        errors["phone"] = "رقم الهاتف يجب أن يحتوي على أرقام فقط."
    elif len(phone) < 8 or len(phone) > 15:
        errors["phone"] = "رقم الهاتف يجب أن يكون من 8 إلى 15 رقمًا."

    if not address:
        errors["address"] = "يرجى إدخال العنوان."
    elif len(address) < 8:
        errors["address"] = "العنوان قصير جدًا."
    elif len(address) > 220:
        errors["address"] = "العنوان طويل جدًا."

    if notes and len(notes) > 500:
        errors["notes"] = "الملاحظات يجب ألا تتجاوز 500 حرف."

    return errors

def register_cart_routes(app, db):
    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        try:
            variant_id = int(request.form.get('variant_id'))
            quantity = int(request.form.get('quantity'))
        except (TypeError, ValueError):
            return handle_cart_error('Invalid product data', 400)

        size = normalize_size(request.form.get('size'))
        action = request.form.get('action')
        source = request.form.get('source')

        if not size or quantity <= 0:
            return handle_cart_error('Invalid cart selection', 400)

        cart = get_cart()
        found = False

        for item in cart:
            if item['variant_id'] == variant_id and item['size'] == size:
                item['quantity'] += quantity
                found = True
                break

        if not found:
            cart.append({
                'variant_id': variant_id,
                'size': size,
                'quantity': quantity
            })

        session['cart'] = cart

        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        is_collection_ajax = is_ajax and source == 'collection'

        if is_collection_ajax:
            return jsonify({
                "success": True,
                "cart_count": get_cart_count(cart)
            })

        if action == 'buy_now':
            return redirect(url_for('checkout'))
        else:
            flash('Added to cart successfully', "success")
            return redirect(request.referrer)

    @app.route("/cart")
    def cart():
        cart_list = get_cart()

        cart_items = []
        for item in cart_list:
            row = db.execute(
                '''
                SELECT 
                    variants.id,
                    variants.name,
                    variants.description,
                    products.price,
                    variant_images.image
                FROM variants
                JOIN products 
                    ON products.id = variants.product_id
                JOIN variant_images
                    ON variant_images.variant_id = variants.id
                WHERE variants.id = ?
                AND variant_images.is_primary = 1
                ''', item['variant_id'])

            if not row:
                continue

            cart_items.append({
                'id': row[0]['id'],
                'name': row[0]['name'],
                'description': row[0]['description'],
                'price': row[0]['price'],
                'image': row[0]['image'],
                'size': item['size'],
                'quantity': item['quantity']
            })

        total = sum(item['price'] * item['quantity'] for item in cart_items)

        return render_template(
            "cart.html",
            cart_items=cart_items,
            total=total,
            cloudinary_image_url=cloudinary_image_url,
        )

    @app.route("/update_cart", methods=["POST"])
    def update_cart():
        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "Invalid request payload"
            }), 400

        try:
            variant_id = int(data.get("variant_id"))
            quantity = int(data.get("quantity"))
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid cart update"
            }), 400

        size = normalize_size(data.get("size"))
        new_size = normalize_size(data.get("new_size"))

        if not size:
            return jsonify({
                "success": False,
                "message": "Missing cart item size"
            }), 400

        cart = get_cart()
        current_item = None

        for item in cart:
            if item["variant_id"] == variant_id and item["size"] == size:
                current_item = item
                break

        if not current_item:
            return jsonify({
                "success": False,
                "message": "Cart item not found"
            }), 404

        if new_size:
            merge_target = None

            for item in cart:
                if item is current_item:
                    continue
                if item["variant_id"] == variant_id and item["size"] == new_size:
                    merge_target = item
                    break

            if merge_target:
                merge_target["quantity"] += quantity
                cart.remove(current_item)
                response_item = merge_target
                merged = True
            else:
                current_item["size"] = new_size
                response_item = current_item
                merged = False
        else:
            if quantity <= 0:
                cart.remove(current_item)
                response_item = None
            else:
                current_item["quantity"] = quantity
                response_item = current_item
            merged = False

        session["cart"] = cart

        return jsonify({
            "success": True,
            "total": calculate_cart_total(cart, db),
            "cart_count": get_cart_count(cart),
            "item": {
                "variant_id": response_item["variant_id"],
                "size": response_item["size"],
                "quantity": response_item["quantity"]
            } if response_item else None,
            "removed": response_item is None,
            "merged": merged
        })

    @app.route("/checkout")
    def checkout():
        return redirect(url_for("cart", open_checkout=1))

    @app.route("/checkout", methods=["POST"])
    def checkout_submit():
        name = normalize_spaces(request.form.get("name"))
        phone = normalize_phone(request.form.get("phone"))
        address = normalize_spaces(request.form.get("address"))
        notes = normalize_spaces(request.form.get("notes"))
        notes = notes or None

        validation_errors = validate_checkout_input(name, phone, address, notes)

        if validation_errors:
            message = "يرجى مراجعة البيانات المدخلة."
            if wants_json_response():
                return jsonify({
                    "success": False,
                    "message": message,
                    "errors": validation_errors
                }), 400

            flash(message, "error")
            return redirect(url_for("cart", open_checkout=1))

        cart = get_cart()
        if not cart:
            message = "السلة فارغة."
            if wants_json_response():
                return jsonify({
                    "success": False,
                    "message": message
                }), 400

            flash(message, "error")
            return redirect(url_for("cart"))

        total_price = calculate_cart_total(cart, db)
        if total_price <= 0:
            message = "تعذر إتمام الطلب، يرجى مراجعة السلة."
            if wants_json_response():
                return jsonify({
                    "success": False,
                    "message": message
                }), 400

            flash(message, "error")
            return redirect(url_for("cart", open_checkout=1))

        order_id = db.execute(
            """
            INSERT INTO orders (name, phone, address, notes, total_price)
            VALUES (?, ?, ?, ?, ?)
            """,
            name,
            phone,
            address,
            notes,
            total_price
        )

        for item in cart:
            price_row = db.execute(
                """
                SELECT products.price
                FROM variants
                JOIN products ON products.id = variants.product_id
                WHERE variants.id = ?
                """,
                item["variant_id"]
            )

            if not price_row:
                continue

            db.execute(
                """
                INSERT INTO order_items (order_id, variant_id, size, quantity, price)
                VALUES (?, ?, ?, ?, ?)
                """,
                order_id,
                item["variant_id"],
                item["size"],
                item["quantity"],
                price_row[0]["price"]
            )

        session["cart"] = []

        success_message = "تم استلام طلبك بنجاح، سيتم التواصل معك قريبًا."

        if wants_json_response():
            return jsonify({
                "success": True,
                "message": success_message
            })

        flash(success_message, "success")
        return redirect(url_for("cart"))
