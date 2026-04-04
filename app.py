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


@app.route("/collection")
def collection():
    return render_template("collection.html")