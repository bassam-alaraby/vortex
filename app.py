from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from math import ceil

# Configure application
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database/app.db")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/collection")
def collection():
    page = request.args.get("page")
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    if page < 1:
        page = 1

    per_page = 8

    row = db.execute("SELECT COUNT(*) AS count FROM variants")
    total_products = row[0]["count"]
    total_pages = ceil(total_products / per_page)

    if total_pages == 0:
        total_pages = 1

    if page > total_pages:
        page = total_pages
    
    offset = (page - 1) * per_page

    products = db.execute(
        '''SELECT products.id, variants.image, products.price
        FROM variants
        JOIN products
        ON products.id = variants.product_id
        LIMIT ? OFFSET ?
        ''', per_page, offset
    )

    return render_template(
    "collection.html",
    products=products,
    page=page,
    total_pages=total_pages
    )
