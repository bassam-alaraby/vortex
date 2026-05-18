import logging
import os
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import requests
from flask import current_app, has_app_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)

TELEGRAM_CHAT_ID_ENV_KEYS = ("TELEGRAM_CHAT_ID_1", "TELEGRAM_CHAT_ID_2")
TELEGRAM_REQUEST_TIMEOUT = 10
TELEGRAM_PARSE_MODE = "HTML"
UTC_ZONE = "UTC"
CAIRO_ZONE = "Africa/Cairo"
logger = logging.getLogger(__name__)


def _get_logger():
    if has_app_context():
        return current_app.logger
    return logger


def send_order_telegram_notification(db, order_id):
    app_logger = _get_logger()

    try:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_ids = [os.environ.get(env_key) for env_key in TELEGRAM_CHAT_ID_ENV_KEYS]
        chat_ids = [chat_id for chat_id in chat_ids if chat_id]

        if not bot_token or not chat_ids:
            return

        order_rows = db.execute(
            """
            SELECT id, name, phone, address, total_price, created_at
            FROM orders
            WHERE id = ?
            """,
            order_id,
        )
        if not order_rows:
            return

        item_rows = db.execute(
            """
            SELECT variant_name, size, quantity, price
            FROM order_items
            WHERE order_id = ?
            """,
            order_id,
        )

        order = order_rows[0]
        created_at = order.get("created_at")
        time_text = ""
        date_text = ""

        if created_at:
            try:
                dt = datetime.fromisoformat(str(created_at).replace(" ", "T"))
                dt = dt.replace(tzinfo=ZoneInfo(UTC_ZONE)).astimezone(ZoneInfo(CAIRO_ZONE))
                time_text = dt.strftime("%H:%M")
                date_text = dt.strftime("%Y-%m-%d")
            except Exception:
                date_text = str(created_at)

        name_text = escape(str(order.get("name", "")))
        phone_text = escape(str(order.get("phone", "")))
        address_text = escape(str(order.get("address", "")))
        time_text = escape(time_text)
        date_text = escape(date_text)

        product_lines = []
        for item in item_rows:
            product_name = escape(str(item.get("variant_name") or "منتج"))
            size = escape(str(item.get("size") or "-"))
            qty = int(item.get("quantity") or 0)
            price = float(item.get("price") or 0)
            product_lines.append(f"  • {product_name} ({size}) x{qty} — {price:.2f} EGP")

        products_text = "\n".join(product_lines) if product_lines else "  • لا توجد منتجات"

        message = (
            "🛍️ <b>أوردر جديد على VORTEX!</b>\n"
            "━━━━━━━━━━━━━━\n\n"
            f"🔢 رقم الأوردر: <code>#{order['id']}</code>\n"
            f"🕐 الوقت: {time_text} — {date_text}\n"
            f"👤 الاسم: {name_text}\n"
            f"📞 التليفون: {phone_text}\n\n"
            "📦 <b>المنتجات:</b>\n"
            f"{products_text}\n\n"
            "━━━━━━━━━━━━━━\n"
            f"💰 الإجمالي: <b>{float(order.get('total_price') or 0):.2f} EGP</b>\n"
            f"📍 العنوان: {address_text}"
        )

        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        for chat_id in chat_ids:
            try:
                response = requests.post(
                    telegram_url,
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": TELEGRAM_PARSE_MODE,
                    },
                    timeout=TELEGRAM_REQUEST_TIMEOUT,
                )
                if response.status_code != 200:
                    app_logger.warning(
                        "Telegram API error: status=%s chat_id=%s",
                        response.status_code,
                        chat_id,
                    )
            except Exception as inner_error:
                app_logger.warning(
                    "Telegram send error: chat_id=%s error=%s",
                    chat_id,
                    inner_error,
                )

    except Exception as error:
        app_logger.warning("Telegram notification error: %s", error)
