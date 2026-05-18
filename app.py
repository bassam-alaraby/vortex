from flask import Flask, request

from config import get_config
from cloudinary_utils import configure_cloudinary
from database.db import TursoDB
from extensions import csrf, limiter

from routes.main_routes import register_main_routes
from routes.shop_routes import register_shop_routes
from routes.cart_routes import register_cart_routes
from routes.admin_routes import register_admin_routes

from helpers import inject_cart_count, inject_sizes_ctx, render_error_response, egypt_time

app = Flask(__name__)
app.config.from_object(get_config())
csrf.init_app(app)
limiter.init_app(app)
configure_cloudinary()

db = TursoDB()

app.context_processor(inject_cart_count)
app.context_processor(inject_sizes_ctx)
app.jinja_env.filters["egypt_time"] = egypt_time

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
