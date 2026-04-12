from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from math import ceil

# Configure application
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure CS50 Library to use SQLite database
db = SQL('sqlite:///database/app.db')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/collection')
def collection():

    # get the current season
    row = db.execute("SELECT value FROM settings WHERE key = 'season'")
    current_season = row[0]["value"]

    valid_seasons = ['summer', 'winter', 'all']

    if current_season not in valid_seasons:
        current_season = 'summer'

    fit = request.args.get('fit')

    rows = db.execute("SELECT DISTINCT fit FROM products")
    valid_fits = [row['fit'] for row in rows]

    if fit not in valid_fits:
        fit = None

    page = request.args.get('page')

    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    if page < 1:
        page = 1

    per_page = 12

    count_query = '''
    SELECT COUNT(*) AS count
    FROM variants
    JOIN products
        ON products.id = variants.product_id
    WHERE 1=1
    '''

    params = []

    if current_season != 'all':
        count_query += ' AND products.season = ?'
        params.append(current_season)

    if fit:
        count_query += ' AND products.fit = ?'
        params.append(fit)

    row = db.execute(count_query, *params)
    total_products = row[0]['count']
    total_pages = ceil(total_products / per_page)

    if total_pages == 0:
        total_pages = 1

    if page > total_pages:
        page = total_pages
    
    offset = (page - 1) * per_page

    query = '''
    SELECT 
        variants.id,
        variants.name,
        products.price,
        product_images.image
    FROM variants
    JOIN products
        ON products.id = variants.product_id
    JOIN product_images 
        ON product_images.product_id = products.id
    WHERE product_images.is_primary = 1
    '''

    params = []

    # season filter
    if current_season != 'all':
        query += ' AND products.season = ?'
        params.append(current_season)

    # fit filter
    if fit:
        query += ' AND products.fit = ?'
        params.append(fit)

    # pagination
    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, offset])

    products = db.execute(query, *params)

    return render_template(
        'collection.html',
        products=products,
        page=page,
        fit=fit,
        total_pages=total_pages
    )


@app.route('/variant/<int:id>')
def variant(id):

    row = db.execute(
        """
        SELECT 
            variants.id,
            variants.name,
            variants.description,
            variants.product_id,
            products.price,
            product_images.image
        FROM variants
        JOIN products 
            ON products.id = variants.product_id
        JOIN product_images
            ON product_images.product_id = products.id
        WHERE variants.id = ?
        AND product_images.is_primary = 1
        """, id)
    variant_details = row[0] if row else None

    product_id = variant_details['product_id']

    row = db.execute(
        '''
        SELECT image
        FROM product_images
        WHERE product_id = ?
        AND is_primary = 0
        ''', product_id)
    images = [r['image'] for r in row]

    return render_template(
        'variant.html'
        # variant_details=variant_details,
        # images=images
    )


@app.route('/about')
def about():
    return render_template('about.html')
