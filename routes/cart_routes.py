from flask import request, session, jsonify, redirect, flash, render_template

# Make sure importing from helpers is at the top level
from helpers import (
    get_cart, normalize_size, get_cart_count, handle_cart_error, 
    calculate_cart_total
)

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
            return redirect('/checkout')
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
                    product_images.image
                FROM variants
                JOIN products 
                    ON products.id = variants.product_id
                JOIN product_images
                    ON product_images.product_id = products.id
                WHERE variants.id = ?
                AND product_images.is_primary = 1
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
            total=total
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
