import hmac
import os
from functools import wraps
from math import ceil

from flask import flash, redirect, render_template, request, session, url_for

from cloudinary_utils import cloudinary_image_url, upload_image
from helpers import validate_image_upload


SIZES = ["XL", "L", "M", "S"]

VALID_ORDER_STATUSES = {"pending", "confirmed", "shipped", "delivered"}
VALID_SEASONS = {"summer", "winter", "all"}
ORDER_STATUS_SEQUENCE = ["pending", "confirmed", "shipped", "delivered"]

def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def register_admin_routes(app, db):
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        error_message = None

        if "admin" in session:
            return redirect(url_for("admin_orders"))

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            admin_username = os.environ.get("ADMIN_USERNAME") or ""
            admin_password = os.environ.get("ADMIN_PASSWORD") or ""

            username_match = hmac.compare_digest(username, admin_username)
            password_match = hmac.compare_digest(password, admin_password)

            if username_match and password_match and admin_username and admin_password:
                session["admin"] = True
                return redirect(url_for("admin_orders"))

            error_message = "بيانات الدخول غير صحيحة"

        return render_template("admin/login.html", error_message=error_message)

    @app.route("/admin/logout")
    @admin_required
    def admin_logout():
        session.clear()
        return redirect(url_for("admin_login"))

    @app.route("/admin/orders")
    @admin_required
    def admin_orders():
        page = request.args.get("page")

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        if page < 1:
            page = 1

        per_page = 8

        total_count = db.execute("SELECT COUNT(*) as count FROM orders")[0]["count"]
        total_pages = ceil(total_count / per_page) if total_count else 1

        if page > total_pages:
            page = total_pages

        offset = (page - 1) * per_page

        orders = db.execute(
            """
            SELECT id, name, phone, total_price, status, created_at
            FROM orders
            ORDER BY created_at DESC, id DESC
            LIMIT ? OFFSET ?
            """,
            per_page,
            offset,
        )

        return render_template(
            "admin/orders.html",
            orders=orders,
            page=page,
            total_pages=total_pages,
            valid_statuses=ORDER_STATUS_SEQUENCE,
        )

    @app.route("/admin/orders/<int:order_id>/status", methods=["POST"])
    @admin_required
    def admin_update_order_status(order_id):
        status = (request.form.get("status") or "").strip().lower()

        if status not in VALID_ORDER_STATUSES:
            flash("Invalid order status", "error")
            return redirect(url_for("admin_orders"))

        row = db.execute("SELECT id FROM orders WHERE id = ?", order_id)
        if not row:
            flash("Order not found", "error")
            return redirect(url_for("admin_orders"))

        db.execute("UPDATE orders SET status = ? WHERE id = ?", status, order_id)
        flash("Order status updated", "success")
        return redirect(url_for("admin_orders"))

    @app.route("/admin/orders/<int:order_id>")
    @admin_required
    def admin_order_details(order_id):
        order_rows = db.execute(
            """
            SELECT id, name, phone, address, notes, total_price, status, created_at
            FROM orders
            WHERE id = ?
            """,
            order_id,
        )

        if not order_rows:
            flash("Order not found", "error")
            return redirect(url_for("admin_orders"))

        order = order_rows[0]

        items = db.execute(
            """
            SELECT
                order_items.size,
                order_items.quantity,
                order_items.price,
                order_items.custom_image,
                order_items.is_custom,
                variants.name AS variant_name,
                variants.color,
                variants.style,
                variants.design,
                products.fit,
                products.season,
                variant_images.image AS variant_image
            FROM order_items
            JOIN variants ON variants.id = order_items.variant_id
            JOIN products ON products.id = variants.product_id
            LEFT JOIN variant_images
                ON variant_images.variant_id = variants.id
                AND variant_images.is_primary = 1
            WHERE order_items.order_id = ?
            ORDER BY order_items.id ASC
            """,
            order_id,
        )

        return render_template(
            "admin/order_details.html",
            order=order,
            items=items,
            cloudinary_image_url=cloudinary_image_url,
        )

    @app.route("/admin/settings", methods=["GET", "POST"])
    @admin_required
    def admin_settings():
        if request.method == "POST":
            season = (request.form.get("season") or "").strip().lower()
            custom_fee_raw = (request.form.get("custom_fee") or "").strip()

            if season not in VALID_SEASONS:
                flash("Invalid season value", "error")
                return redirect(url_for("admin_settings"))

            try:
                custom_fee_value = int(custom_fee_raw)
            except ValueError:
                flash("Custom design fee must be a whole number.", "error")
                return redirect(url_for("admin_settings"))

            if custom_fee_value < 0:
                flash("Custom design fee cannot be negative.", "error")
                return redirect(url_for("admin_settings"))

            try:
                db.execute("BEGIN")
                current_row = db.execute('SELECT key FROM settings WHERE key = "season"')
                custom_fee_row = db.execute('SELECT key FROM settings WHERE key = "custom_fee"')

                if current_row:
                    db.execute('UPDATE settings SET value = ? WHERE key = "season"', season)
                else:
                    db.execute(
                        'INSERT INTO settings (key, value) VALUES ("season", ?)', season
                    )

                if custom_fee_row:
                    db.execute(
                        'UPDATE settings SET value = ? WHERE key = "custom_fee"',
                        str(int(custom_fee_value)),
                    )
                else:
                    db.execute(
                        'INSERT INTO settings (key, value) VALUES ("custom_fee", ?)',
                        str(int(custom_fee_value)),
                    )

                db.execute("COMMIT")
                flash("Settings updated.", "success")
            except Exception:
                db.execute("ROLLBACK")
                flash("Failed to update settings.", "error")

            return redirect(url_for("admin_settings"))

        row = db.execute('SELECT value FROM settings WHERE key = "season"')
        current_season = row[0]["value"] if row else "summer"
        if current_season not in VALID_SEASONS:
            current_season = "summer"

        custom_fee_row = db.execute('SELECT value FROM settings WHERE key = "custom_fee"')
        try:
            current_custom_fee = int(float(custom_fee_row[0]["value"])) if custom_fee_row else 80
        except (TypeError, ValueError, KeyError):
            current_custom_fee = 80

        return render_template(
            "admin/settings.html",
            current_season=current_season,
            current_custom_fee=current_custom_fee,
        )

    @app.route("/admin/products")
    @admin_required
    def admin_products():
        page = request.args.get("page")
        variants_page = request.args.get("variants_page")

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        try:
            variants_page = int(variants_page)
        except (TypeError, ValueError):
            variants_page = 1

        if page < 1:
            page = 1
        if variants_page < 1:
            variants_page = 1

        per_page = 12
        total_count = db.execute("SELECT COUNT(*) AS count FROM products")[0]["count"]
        total_pages = ceil(total_count / per_page) if total_count else 1

        variants_per_page = 12
        variants_total_count = db.execute("SELECT COUNT(*) AS count FROM variants")[0]["count"]
        variants_total_pages = (
            ceil(variants_total_count / variants_per_page) if variants_total_count else 1
        )

        if page > total_pages:
            page = total_pages
        if variants_page > variants_total_pages:
            variants_page = variants_total_pages

        offset = (page - 1) * per_page
        variants_offset = (variants_page - 1) * variants_per_page

        products = db.execute(
            """
            SELECT
                products.id,
                products.name,
                products.fit,
                products.price,
                products.season,
                product_images.image AS primary_image
            FROM products
            LEFT JOIN (
                SELECT
                    variants.product_id,
                    MAX(variant_images.id) AS image_id
                FROM variants
                JOIN variant_images
                    ON variant_images.variant_id = variants.id
                    AND variant_images.is_primary = 1
                GROUP BY variants.product_id
            ) AS product_image_ids
                ON product_image_ids.product_id = products.id
            LEFT JOIN variant_images AS product_images
                ON product_images.id = product_image_ids.image_id
            ORDER BY products.id DESC
            LIMIT ? OFFSET ?
            """,
            per_page,
            offset,
        )

        variants = db.execute(
            """
            SELECT
                variants.id,
                variants.product_id,
                variants.name,
                variants.color,
                variants.style,
                variants.design,
                products.name AS product_name,
                variant_images.image AS primary_image
            FROM variants
            JOIN products ON products.id = variants.product_id
            LEFT JOIN variant_images
                ON variant_images.variant_id = variants.id
                AND variant_images.is_primary = 1
            ORDER BY variants.id DESC
            LIMIT ? OFFSET ?
            """,
            variants_per_page,
            variants_offset,
        )

        has_prev = page > 1
        has_next = page < total_pages
        variants_has_prev = variants_page > 1
        variants_has_next = variants_page < variants_total_pages

        return render_template(
            "admin/products.html",
            products=products,
            variants=variants,
            cloudinary_image_url=cloudinary_image_url,
            page=page,
            total_pages=total_pages,
            has_prev=has_prev,
            has_next=has_next,
            variants_page=variants_page,
            variants_total_pages=variants_total_pages,
            variants_has_prev=variants_has_prev,
            variants_has_next=variants_has_next,
        )

    @app.route("/admin/products/add", methods=["GET", "POST"])
    @admin_required
    def admin_add_product():
        fits = _get_distinct_values(db, "products", "fit")
        seasons = _get_distinct_values(db, "products", "season")

        if request.method == "POST":
            name = _normalize_text(request.form.get("name"))
            fit = _resolve_dynamic_value(request.form, "fit")
            season = _resolve_dynamic_value(request.form, "season")
            price_value, price_error = _parse_price(request.form.get("price"))

            errors = []
            if not name:
                errors.append("Product name is required.")
            if not fit:
                errors.append("Fit is required.")
            if not season:
                errors.append("Season is required.")
            if price_error:
                errors.append(price_error)

            if errors:
                for error in errors:
                    flash(error, "error")
                return render_template(
                    "admin/add_product.html",
                    fits=fits,
                    seasons=seasons,
                    form=request.form,
                )

            try:
                db.execute("BEGIN")
                db.execute(
                    """
                    INSERT INTO products (name, fit, price, season)
                    VALUES (?, ?, ?, ?)
                    """,
                    name,
                    fit,
                    price_value,
                    season,
                )
                db.execute("COMMIT")
            except Exception:
                db.execute("ROLLBACK")
                flash("Failed to create product.", "error")
                return render_template(
                    "admin/add_product.html",
                    fits=fits,
                    seasons=seasons,
                    form=request.form,
                )

            flash("Product created.", "success")
            return redirect(url_for("admin_products"))

        return render_template("admin/add_product.html", fits=fits, seasons=seasons, form={})

    @app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_edit_product(product_id):
        row = db.execute(
            """
            SELECT id, name, fit, price, season
            FROM products
            WHERE id = ?
            """,
            product_id,
        )

        if not row:
            flash("Product not found.", "error")
            return redirect(url_for("admin_products"))

        product = row[0]
        fits = _get_distinct_values(db, "products", "fit")
        seasons = _get_distinct_values(db, "products", "season")

        if request.method == "POST":
            name = _normalize_text(request.form.get("name"))
            fit = _resolve_dynamic_value(request.form, "fit")
            season = _resolve_dynamic_value(request.form, "season")
            price_value, price_error = _parse_price(request.form.get("price"))

            errors = []
            if not name:
                errors.append("Product name is required.")
            if not fit:
                errors.append("Fit is required.")
            if not season:
                errors.append("Season is required.")
            if price_error:
                errors.append(price_error)

            if errors:
                for error in errors:
                    flash(error, "error")
                return render_template(
                    "admin/edit_product.html",
                    product=product,
                    fits=fits,
                    seasons=seasons,
                    form=request.form,
                )

            try:
                db.execute("BEGIN")
                db.execute(
                    """
                    UPDATE products
                    SET name = ?, fit = ?, price = ?, season = ?
                    WHERE id = ?
                    """,
                    name,
                    fit,
                    price_value,
                    season,
                    product_id,
                )
                db.execute("COMMIT")
            except Exception:
                db.execute("ROLLBACK")
                flash("Failed to update product.", "error")
                return render_template(
                    "admin/edit_product.html",
                    product=product,
                    fits=fits,
                    seasons=seasons,
                    form=request.form,
                )

            flash("Product updated.", "success")
            return redirect(url_for("admin_products"))

        return render_template(
            "admin/edit_product.html",
            product=product,
            fits=fits,
            seasons=seasons,
            form=product,
        )

    @app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
    @admin_required
    def admin_delete_product(product_id):
        has_variants = db.execute(
            "SELECT id FROM variants WHERE product_id = ? LIMIT 1",
            product_id,
        )
        if has_variants:
            flash("Delete variants before removing this product.", "error")
            return redirect(url_for("admin_products"))

        db.execute("DELETE FROM products WHERE id = ?", product_id)
        flash("Product deleted.", "success")
        return redirect(url_for("admin_products"))

    @app.route("/admin/variants/add/<int:product_id>", methods=["GET", "POST"])
    @admin_required
    def admin_add_variant_for_product(product_id):
        products = _get_products(db)
        product = next((p for p in products if p["id"] == product_id), None)
        if not product:
            flash("Product not found.", "error")
            return redirect(url_for("admin_products"))

        if request.method == "POST":
            return _handle_variant_create(db, products, locked_product_id=product_id)

        return _render_variant_form(
            db=db,
            template="admin/add_variant.html",
            products=products,
            selected_product_id=product_id,
            form={},
            variant=None,
            existing_images=[],
            lock_product=True,
        )

    @app.route("/admin/variants/add", methods=["GET", "POST"])
    @admin_required
    def admin_add_variant():
        products = _get_products(db)
        if not products:
            flash("Create a product before adding variants.", "error")
            return redirect(url_for("admin_products"))

        if request.method == "POST":
            return _handle_variant_create(db, products)

        return _render_variant_form(
            db=db,
            template="admin/add_variant.html",
            products=products,
            selected_product_id=None,
            form={},
            variant=None,
            existing_images=[],
            lock_product=False,
        )

    @app.route("/admin/variants/<int:variant_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_edit_variant(variant_id):
        row = db.execute(
            """
            SELECT id, product_id, name, description, color, style, design
            FROM variants
            WHERE id = ?
            """,
            variant_id,
        )
        if not row:
            flash("Variant not found.", "error")
            return redirect(url_for("admin_products"))

        variant = row[0]
        products = _get_products(db)
        existing_images = db.execute(
            """
            SELECT id, image, is_primary
            FROM variant_images
            WHERE variant_id = ?
            ORDER BY id DESC
            """,
            variant_id,
        )

        if request.method == "POST":
            return _handle_variant_update(db, variant, products, existing_images)

        return _render_variant_form(
            db=db,
            template="admin/edit_variant.html",
            products=products,
            selected_product_id=variant["product_id"],
            form=variant,
            variant=variant,
            existing_images=existing_images,
            lock_product=False,
        )

    @app.route("/admin/variants/<int:variant_id>/delete", methods=["POST"])
    @admin_required
    def admin_delete_variant(variant_id):
        db.execute("DELETE FROM variant_images WHERE variant_id = ?", variant_id)
        db.execute("DELETE FROM variants WHERE id = ?", variant_id)
        flash("Variant deleted.", "success")
        return redirect(url_for("admin_products"))


def _get_distinct_values(db, table, column):
    rows = db.execute(
        f"SELECT DISTINCT {column} AS value FROM {table} WHERE {column} IS NOT NULL AND {column} != ''"
    )
    values = [row["value"] for row in rows if row["value"]]
    return values


def _resolve_dynamic_value(form, field_name):
    manual_value = _normalize_text(form.get(f"{field_name}_new"))
    if manual_value:
        return manual_value
    return _normalize_text(form.get(field_name))


def _normalize_text(value):
    value = (value or "").strip()
    return value or None


def _parse_price(value):
    value = (value or "").strip()
    if not value:
        return None, "Price is required."

    try:
        price_value = float(value)
    except ValueError:
        return None, "Price must be a number."

    if price_value <= 0:
        return None, "Price must be greater than 0."

    return price_value, None


def _get_products(db):
    return db.execute("SELECT id, name FROM products ORDER BY id DESC")


def _render_variant_form(
    *,
    db,
    template,
    products,
    selected_product_id,
    form,
    variant,
    existing_images,
    lock_product,
):
    colors = _get_distinct_values(db, "variants", "color")
    styles = _get_distinct_values(db, "variants", "style")
    designs = _get_distinct_values(db, "variants", "design")

    return render_template(
        template,
        products=products,
        selected_product_id=selected_product_id,
        colors=colors,
        styles=styles,
        designs=designs,
        form=form,
        variant=variant,
        existing_images=existing_images,
        cloudinary_image_url=cloudinary_image_url,
        lock_product=lock_product,
    )


def _validate_variant_inputs(db, product_id, name, description, color, style):
    errors = []
    if not product_id or not product_id.isdigit():
        errors.append("Product selection is required.")
    if not name:
        errors.append("Variant name is required.")
    if not description:
        errors.append("Description is required.")
    if not color:
        errors.append("Color is required.")
    if not style:
        errors.append("Style is required.")

    if product_id and product_id.isdigit():
        exists = db.execute("SELECT id FROM products WHERE id = ?", int(product_id))
        if not exists:
            errors.append("Selected product does not exist.")

    return errors


def _set_primary_image(db, variant_id, image_id):
    db.execute("UPDATE variant_images SET is_primary = 0 WHERE variant_id = ?", variant_id)
    db.execute(
        "UPDATE variant_images SET is_primary = 1 WHERE id = ? AND variant_id = ?",
        image_id,
        variant_id,
    )


def _handle_variant_uploads(db, variant_id, allow_empty):
    files = request.files.getlist("images")
    valid_files = []

    for file_obj in files:
        if not file_obj or not file_obj.filename:
            continue

        _, validation_error = validate_image_upload(file_obj)
        if validation_error:
            flash(validation_error, "error")
            return None

        valid_files.append(file_obj)

    if not valid_files:
        return [] if allow_empty else None

    uploaded_images = []
    for index, file_obj in enumerate(valid_files, start=1):
        try:
            public_id = upload_image(file_obj)
        except Exception:
            flash("Image upload failed.", "error")
            return None

        db.execute(
            """
            INSERT INTO variant_images (variant_id, image, is_primary)
            VALUES (?, ?, 0)
            """,
            variant_id,
            public_id,
        )
        image_id = db.execute("SELECT last_insert_rowid() AS id")[0]["id"]
        uploaded_images.append((index, image_id))

    return uploaded_images


def _handle_variant_create(db, products, locked_product_id=None):
    form = request.form
    if locked_product_id is not None:
        product_id = str(locked_product_id)
    else:
        product_id = (form.get("product_id") or "").strip()

    name = _normalize_text(form.get("name"))
    description = _normalize_text(form.get("description"))
    color = _resolve_dynamic_value(form, "color")
    style = _resolve_dynamic_value(form, "style")
    design = _normalize_text(_resolve_dynamic_value(form, "design"))

    errors = _validate_variant_inputs(db, product_id, name, description, color, style)
    if errors:
        for error in errors:
            flash(error, "error")
        return _render_variant_form(
            db=db,
            template="admin/add_variant.html",
            products=products,
            selected_product_id=int(product_id) if product_id.isdigit() else None,
            form=form,
            variant=None,
            existing_images=[],
            lock_product=locked_product_id is not None,
        )

    product_id_int = int(product_id)

    try:
        db.execute("BEGIN")
        db.execute(
            """
            INSERT INTO variants (product_id, name, description, color, style, design)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            product_id_int,
            name,
            description,
            color,
            style,
            design or "",
        )
        variant_id = db.execute("SELECT last_insert_rowid() AS id")[0]["id"]

        uploaded_images = _handle_variant_uploads(db, variant_id, allow_empty=False)
        if uploaded_images is None:
            raise RuntimeError("Image upload failed")

        primary_upload = (form.get("primary_upload") or "").strip()
        primary_id = None
        if primary_upload.isdigit():
            selected_index = int(primary_upload)
            for index, image_id in uploaded_images:
                if index == selected_index:
                    primary_id = image_id
                    break

        if primary_id is None:
            primary_id = uploaded_images[0][1]

        _set_primary_image(db, variant_id, primary_id)
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        if not request.files.getlist("images"):
            flash("At least one image is required.", "error")
        else:
            flash("Failed to create variant.", "error")
        return _render_variant_form(
            db=db,
            template="admin/add_variant.html",
            products=products,
            selected_product_id=product_id_int,
            form=form,
            variant=None,
            existing_images=[],
            lock_product=locked_product_id is not None,
        )

    flash("Variant created.", "success")
    return redirect(url_for("admin_edit_variant", variant_id=variant_id))


def _handle_variant_update(db, variant, products, existing_images):
    form = request.form
    product_id = (form.get("product_id") or "").strip()

    name = _normalize_text(form.get("name"))
    description = _normalize_text(form.get("description"))
    color = _resolve_dynamic_value(form, "color")
    style = _resolve_dynamic_value(form, "style")
    design = _normalize_text(_resolve_dynamic_value(form, "design"))

    errors = _validate_variant_inputs(db, product_id, name, description, color, style)
    if errors:
        for error in errors:
            flash(error, "error")
        return _render_variant_form(
            db=db,
            template="admin/edit_variant.html",
            products=products,
            selected_product_id=int(product_id) if product_id.isdigit() else None,
            form=form,
            variant=variant,
            existing_images=existing_images,
            lock_product=False,
        )

    product_id_int = int(product_id)

    existing_primary_id = next(
        (image["id"] for image in existing_images if image["is_primary"]),
        None,
    )

    try:
        db.execute("BEGIN")
        db.execute(
            """
            UPDATE variants
            SET product_id = ?, name = ?, description = ?, color = ?, style = ?, design = ?
            WHERE id = ?
            """,
            product_id_int,
            name,
            description,
            color,
            style,
            design or "",
            variant["id"],
        )

        uploaded_images = _handle_variant_uploads(db, variant["id"], allow_empty=True)
        if uploaded_images is None:
            raise RuntimeError("Image upload failed")

        primary_upload = (form.get("primary_upload") or "").strip()
        primary_image = (form.get("primary_image") or "").strip()

        if primary_upload.isdigit() and uploaded_images:
            selected_index = int(primary_upload)
            selected_id = None
            for index, image_id in uploaded_images:
                if index == selected_index:
                    selected_id = image_id
                    break

            if selected_id is not None:
                _set_primary_image(db, variant["id"], selected_id)
        elif primary_image.isdigit():
            _set_primary_image(db, variant["id"], int(primary_image))
        elif uploaded_images and existing_primary_id is None:
            _set_primary_image(db, variant["id"], uploaded_images[0][1])

        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        flash("Failed to update variant.", "error")
        return _render_variant_form(
            db=db,
            template="admin/edit_variant.html",
            products=products,
            selected_product_id=product_id_int,
            form=form,
            variant=variant,
            existing_images=existing_images,
            lock_product=False,
        )

    flash("Variant updated.", "success")
    return redirect(url_for("admin_edit_variant", variant_id=variant["id"]))
