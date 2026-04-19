import hmac
import os
from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for


VALID_ORDER_STATUSES = {"pending", "confirmed", "shipped", "delivered"}
VALID_SEASONS = {"summer", "winter", "all"}
ORDER_STATUS_SEQUENCE = ["pending", "confirmed", "shipped", "delivered"]


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def register_admin_routes(app, db):
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        error_message = None

        if session.get("admin"):
            return redirect(url_for("admin_orders"))

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            admin_username = os.environ.get("ADMIN_USERNAME") or ""
            admin_password = os.environ.get("ADMIN_PASSWORD") or ""

            username_match = hmac.compare_digest(username, admin_username)
            password_match = hmac.compare_digest(password, admin_password)

            if username_match and password_match and admin_username and admin_password:
                session["admin"] = username
                return redirect(url_for("admin_orders"))

            error_message = "بيانات الدخول غير صحيحة"

        return render_template("admin/login.html", error_message=error_message)

    @app.route("/admin/logout")
    def admin_logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/admin/orders")
    @admin_required
    def admin_orders():
        orders = db.execute(
            """
            SELECT id, name, phone, total_price, status, created_at
            FROM orders
            ORDER BY created_at DESC, id DESC
            """
        )

        return render_template(
            "admin/orders.html",
            orders=orders,
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
                order_items.quantity,
                order_items.price,
                variants.name AS variant_name,
                variants.color,
                variants.style,
                variants.design,
                products.fit,
                products.season
            FROM order_items
            JOIN variants ON variants.id = order_items.variant_id
            JOIN products ON products.id = variants.product_id
            WHERE order_items.order_id = ?
            ORDER BY order_items.id ASC
            """,
            order_id,
        )

        return render_template("admin/order_details.html", order=order, items=items)

    @app.route("/admin/season", methods=["GET", "POST"])
    @admin_required
    def admin_season():
        if request.method == "POST":
            season = (request.form.get("season") or "").strip().lower()

            if season not in VALID_SEASONS:
                flash("Invalid season value", "error")
                return redirect(url_for("admin_season"))

            current_row = db.execute('SELECT key FROM settings WHERE key = "season"')

            if current_row:
                db.execute('UPDATE settings SET value = ? WHERE key = "season"', season)
            else:
                db.execute(
                    'INSERT INTO settings (key, value) VALUES ("season", ?)', season
                )

            return redirect(url_for("admin_season"))

        row = db.execute('SELECT value FROM settings WHERE key = "season"')
        current_season = row[0]["value"] if row else "summer"
        if current_season not in VALID_SEASONS:
            current_season = "summer"

        return render_template("admin/season.html", current_season=current_season)
