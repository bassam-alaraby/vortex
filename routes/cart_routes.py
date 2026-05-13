from flask import request, session, jsonify, redirect, flash, render_template, url_for

from helpers import (
    DELIVERY_REGION_LABELS,
    DELIVERY_REGION_ORDER,
    calculate_cart_total,
    get_cart,
    get_cart_count,
    get_custom_fee,
    get_delivery_fees,
    handle_cart_error,
    normalize_phone,
    normalize_size,
    normalize_spaces,
    validate_checkout_input,
    wants_json_response,
    _safe_redirect,
)
from cloudinary_utils import cloudinary_image_url
from extensions import send_order_telegram_notification


def _regular_cart_item_id(variant_id, size):
    return f"regular-{variant_id}-{size}"


def _ensure_cart_item_id(item, index):
    existing = item.get("cart_item_id")
    if existing:
        return existing

    if item.get("is_custom"):
        return f"custom-{item.get('variant_id', 'x')}-{item.get('size', '-')}-{index}"

    return _regular_cart_item_id(item.get("variant_id"), item.get("size"))

def register_cart_routes(app, db):
    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        try:
            variant_id = int(request.form.get('variant_id'))
        except (TypeError, ValueError):
            return handle_cart_error('Invalid request data', 400)

        variant_exists = db.execute(
            "SELECT id FROM variants WHERE id = ?", variant_id
        )

        if not variant_exists:
            return handle_cart_error('Product not found', 404)

        try:
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
            if item.get('is_custom'):
                continue

            if item['variant_id'] == variant_id and item['size'] == size:
                item['quantity'] += quantity
                item['cart_item_id'] = _regular_cart_item_id(variant_id, size)
                found = True
                break

        if not found:
            cart.append({
                'variant_id': variant_id,
                'size': size,
                'quantity': quantity,
                'is_custom': 0,
                'cart_item_id': _regular_cart_item_id(variant_id, size)
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
            return redirect(request.referrer or url_for('collection'))

    @app.route("/cart")
    def cart():
        cart_list = get_cart()
        custom_fee = get_custom_fee(db)
        delivery_fees = get_delivery_fees(db)
        should_update_session = False

        cart_items = []
        for index, item in enumerate(cart_list):
            row = db.execute(
                '''
                SELECT 
                    variants.id,
                    variants.name,
                    variants.description,
                    variants.style,
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

            cart_item_id = _ensure_cart_item_id(item, index)
            if item.get("cart_item_id") != cart_item_id:
                item["cart_item_id"] = cart_item_id
                should_update_session = True

            is_custom = bool(item.get("is_custom"))
            base_price = float(row[0]["price"])
            unit_price = float(item.get("unit_price", base_price + custom_fee if is_custom else base_price))

            cart_items.append({
                'id': row[0]['id'],
                'name': row[0]['name'],
                'description': row[0]['description'],
                'price': unit_price,
                'base_price': base_price,
                'custom_fee': custom_fee if is_custom else 0,
                'image': row[0]['image'],
                'size': item['size'],
                'quantity': item['quantity'],
                'is_custom': 1 if is_custom else 0,
                'custom_image': item.get('custom_image'),
                'cart_item_id': cart_item_id,
            })

        if should_update_session:
            session['cart'] = cart_list

        total = calculate_cart_total(cart_list, db)

        return render_template(
            "cart.html",
            cart_items=cart_items,
            total=total,
            cloudinary_image_url=cloudinary_image_url,
            delivery_fees=delivery_fees,
            delivery_region_labels=DELIVERY_REGION_LABELS,
            delivery_region_order=DELIVERY_REGION_ORDER,
        )

    @app.route("/update_cart", methods=["POST"])
    def update_cart():
        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "Invalid request payload"
            }), 400

        cart_item_id = (data.get("cart_item_id") or "").strip()

        try:
            quantity = int(data.get("quantity"))
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid cart update"
            }), 400

        try:
            variant_id = int(data.get("variant_id"))
        except (TypeError, ValueError):
            variant_id = None

        size = normalize_size(data.get("size"))
        new_size = normalize_size(data.get("new_size"))

        if not cart_item_id and not size:
            return jsonify({
                "success": False,
                "message": "Missing cart item identifier"
            }), 400

        cart = get_cart()
        current_item = None

        for item in cart:
            item_id = item.get("cart_item_id")

            if cart_item_id and item_id == cart_item_id:
                current_item = item
                break

            if (
                not cart_item_id
                and variant_id is not None
                and not item.get("is_custom")
                and item["variant_id"] == variant_id
                and item["size"] == size
            ):
                current_item = item
                break

        if not current_item:
            return jsonify({
                "success": False,
                "message": "Cart item not found"
            }), 404

        if new_size:
            merge_target = None

            is_custom_item = bool(current_item.get("is_custom"))

            if not is_custom_item:
                for item in cart:
                    if item is current_item:
                        continue
                    if item.get("is_custom"):
                        continue
                    if item["variant_id"] == current_item["variant_id"] and item["size"] == new_size:
                        merge_target = item
                        break

            if merge_target:
                merge_target["quantity"] += quantity
                merge_target["cart_item_id"] = _regular_cart_item_id(
                    merge_target["variant_id"],
                    merge_target["size"],
                )
                cart.remove(current_item)
                response_item = merge_target
                merged = True
            else:
                current_item["size"] = new_size
                if not current_item.get("is_custom"):
                    current_item["cart_item_id"] = _regular_cart_item_id(
                        current_item["variant_id"],
                        new_size,
                    )
                response_item = current_item
                merged = False
        else:
            if quantity <= 0:
                cart.remove(current_item)
                response_item = None
            else:
                current_item["quantity"] = quantity
                if not current_item.get("cart_item_id"):
                    current_item["cart_item_id"] = _ensure_cart_item_id(current_item, 0)
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
                "quantity": response_item["quantity"],
                "cart_item_id": response_item.get("cart_item_id")
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
        delivery_region = (request.form.get("delivery_region") or "").strip()

        validation_errors = validate_checkout_input(name, phone, address, notes)

        delivery_fees = get_delivery_fees(db)
        delivery_fee = delivery_fees.get(delivery_region)
        if delivery_fee is None:
            validation_errors["delivery_region"] = "يرجى اختيار منطقة الشحن."
        else:
            delivery_fee = float(delivery_fee)

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
        if delivery_fee is not None:
            total_price += delivery_fee
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
            INSERT INTO orders (
                name,
                phone,
                address,
                notes,
                total_price,
                delivery_region,
                delivery_fee
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            name,
            phone,
            address,
            notes,
            total_price,
            delivery_region,
            delivery_fee
        )

        for item in cart:
            is_custom = bool(item.get("is_custom"))

            variant_rows = db.execute(
                """
                SELECT
                    variants.name AS variant_name,
                    variants.color AS variant_color,
                    variants.style AS variant_style,
                    variants.design AS variant_design,
                    products.name AS product_name,
                    products.fit AS product_fit,
                    products.season AS product_season,
                    products.price AS product_price,
                    variant_images.image AS variant_image
                FROM variants
                JOIN products ON products.id = variants.product_id
                LEFT JOIN variant_images
                    ON variant_images.variant_id = variants.id
                    AND variant_images.is_primary = 1
                WHERE variants.id = ?
                """,
                item["variant_id"],
            )

            if not variant_rows:
                continue

            variant_row = variant_rows[0]

            price_value = (
                float(item.get("unit_price", 0))
                if is_custom
                else float(variant_row["product_price"])
            )

            if price_value <= 0:
                continue

            db.execute(
                """
                INSERT INTO order_items (
                    order_id,
                    variant_id,
                    size,
                    quantity,
                    price,
                    custom_image,
                    is_custom,
                    variant_name,
                    variant_color,
                    variant_style,
                    variant_design,
                    product_name,
                    product_fit,
                    product_season,
                    variant_image
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                order_id,
                item["variant_id"],
                item["size"],
                item["quantity"],
                price_value,
                item.get("custom_image") if is_custom else None,
                1 if is_custom else 0,
                variant_row["variant_name"],
                variant_row["variant_color"],
                variant_row["variant_style"],
                variant_row["variant_design"],
                variant_row["product_name"],
                variant_row["product_fit"],
                variant_row["product_season"],
                variant_row["variant_image"],
            )

        send_order_telegram_notification(db, order_id)
        session["cart"] = []

        success_message = "تم استلام طلبك بنجاح، سيتم التواصل معك قريبًا."

        if wants_json_response():
            return jsonify({
                "success": True,
                "message": success_message
            })

        flash(success_message, "success")
        return redirect(url_for("cart"))
