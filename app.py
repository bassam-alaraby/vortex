import os
import sqlite3

from flask import Flask, request
from cs50 import SQL

from config import get_config
from cloudinary_utils import configure_cloudinary

from routes.main_routes import register_main_routes
from routes.shop_routes import register_shop_routes
from routes.cart_routes import register_cart_routes
from routes.admin_routes import register_admin_routes

from helpers import get_cart, get_cart_count, render_error_response, get_sizes

app = Flask(__name__)
app.config.from_object(get_config())
configure_cloudinary()

def _ensure_db(db_path, schema_path):
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        print(f"DB initialized at {db_path}")

_BASE = os.path.abspath(os.path.dirname(__file__))
_ensure_db(
    os.path.join(_BASE, 'data', 'app.db'),
    os.path.join(_BASE, 'database', 'schema.sql')
)

db = SQL(app.config['DATABASE_PATH'])
db.execute("PRAGMA foreign_keys = ON")

@app.context_processor
def inject_cart_count():
    cart = get_cart()
    return dict(cart_count=get_cart_count(cart))


@app.context_processor
def inject_sizes():
    return dict(sizes=get_sizes())

@app.errorhandler(404)
def not_found(error):
    return render_error_response(
        404,
        "404.html",
        "404",
        "The page you are looking for does not exist."
    )

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.exception("Unhandled server error")
    return render_error_response(
        500,
        "500.html",
        "500",
        "An unexpected error occurred. Please try again later."
    )
    
@app.after_request
def add_no_cache_headers(response):
    if request.path.startswith("/admin"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

register_main_routes(app)
register_shop_routes(app, db)
register_cart_routes(app, db)
register_admin_routes(app, db)

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', True))
