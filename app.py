from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from math import ceil

# Configure application
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database/database.db")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/products")
def products():
    page = request.args.get("page")
    try:
        page = int(page)
    except:
        page = 1

    if page < 1:
        page = 1

    per_page = 8
    offset = (page - 1) * per_page

    products = db.execute(
        "SELECT * FROM products LIMIT ? OFFSET ?",
        per_page, offset
    )

    row = db.execute("SELECT COUNT(*) AS count FROM products")
    total_products = row[0]["count"]
    total_pages = ceil(total_products / per_page)

    return render_template(
    "products.html",
    products=products,
    page=page,
    total_pages=total_pages
    )