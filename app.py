from flask import Flask, render_template
from cs50 import SQL
import os

# Import Configuration
from config import Config

# Import Routes
from routes.main_routes import register_main_routes
from routes.shop_routes import register_shop_routes
from routes.cart_routes import register_cart_routes

# Import Helpers
from helpers import get_cart, get_cart_count, render_error_response

# Configure application
app = Flask(__name__)
# Load config from object
app.config.from_object(Config)

# Configure CS50 Library to use SQLite database
db = SQL(app.config['DATABASE_PATH'])

# Register context processors
@app.context_processor
def inject_cart_count():
    cart = get_cart()
    return dict(cart_count=get_cart_count(cart))

# Register error handlers
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

# Register routes
register_main_routes(app)
register_shop_routes(app, db)
register_cart_routes(app, db)

if __name__ == '__main__':
    # Can run locally using standard python app.py
    app.run(debug=app.config.get('DEBUG', True))
