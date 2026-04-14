from cs50 import SQL
from flask import Flask, session, flash, jsonify, redirect, url_for, render_template, request, abort
from math import ceil

# Configure application
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'vortexMO'

# Configure CS50 Library to use SQLite database
db = SQL('sqlite:///database/app.db')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/collection')
def collection():

    # get the current season
    row = db.execute('SELECT value FROM settings WHERE key = "season"')
    current_season = row[0]['value']

    valid_seasons = ['summer', 'winter', 'all']

    if current_season not in valid_seasons:
        current_season = 'summer'

    fit = request.args.get('fit')

    rows = db.execute('SELECT DISTINCT fit FROM products')
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

    per_page = 6

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
        '''
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
        ''', id)
    if not row:
        abort(404)

    variant_details = row[0]

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
        'variant.html',
        variant_details=variant_details,
        images=images
    )


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    try:
        variant_id = int(request.form.get('variant_id'))
        quantity = int(request.form.get('quantity'))
    except (TypeError, ValueError):
        return handle_cart_error('Invalid product data', 400)

    size = normalize_size(request.form.get('size'))
    action = request.form.get('action')
    source = request.form.get('source')

    if not size or quantity <= 0:
        return handle_cart_error('Invalid cart selection', 400)

    cart = get_cart()

    found = False

    for item in cart:
        if item['variant_id'] == variant_id and item['size'] == size:
            item['quantity'] += quantity
            found = True
            break

    if not found:
        cart.append({
            'variant_id': variant_id,
            'size': size,
            'quantity': quantity
        })

    session['cart'] = cart

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    is_collection_ajax = is_ajax and source == 'collection'

    if is_collection_ajax:
        return jsonify({
            "success": True,
            "cart_count": get_cart_count(cart)
        })

    if action == 'buy_now':
        return redirect('/checkout')
    else:
        flash('Added to cart successfully', "success")
        return redirect(request.referrer)


@app.route("/cart")
def cart():
    cart = get_cart()

    cart_items = []

    for item in cart:
        row = db.execute(
            '''
            SELECT 
                variants.id,
                variants.name,
                variants.description,
                products.price,
                product_images.image
            FROM variants
            JOIN products 
                ON products.id = variants.product_id
            JOIN product_images
                ON product_images.product_id = products.id
            WHERE variants.id = ?
            AND product_images.is_primary = 1
            ''', item['variant_id'])

        if not row:
            continue

        cart_items.append({
            'id': row[0]['id'],
            'name': row[0]['name'],
            'description': row[0]['description'],
            'price': row[0]['price'],
            'image': row[0]['image'],
            'size': item['size'],
            'quantity': item['quantity']
        })

    total = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


@app.route("/update_cart", methods=["POST"])
def update_cart():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request payload"
        }), 400

    try:
        variant_id = int(data.get("variant_id"))
        quantity = int(data.get("quantity"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid cart update"
        }), 400

    size = normalize_size(data.get("size"))
    new_size = normalize_size(data.get("new_size"))

    if not size:
        return jsonify({
            "success": False,
            "message": "Missing cart item size"
        }), 400

    cart = get_cart()
    current_item = None

    for item in cart:
        if item["variant_id"] == variant_id and item["size"] == size:
            current_item = item
            break

    if not current_item:
        return jsonify({
            "success": False,
            "message": "Cart item not found"
        }), 404

    if new_size:
        merge_target = None

        for item in cart:
            if item is current_item:
                continue
            if item["variant_id"] == variant_id and item["size"] == new_size:
                merge_target = item
                break

        if merge_target:
            merge_target["quantity"] += quantity
            cart.remove(current_item)
            response_item = merge_target
            merged = True
        else:
            current_item["size"] = new_size
            response_item = current_item
            merged = False
    else:
        if quantity <= 0:
            cart.remove(current_item)
            response_item = None
        else:
            current_item["quantity"] = quantity
            response_item = current_item
        merged = False

    session["cart"] = cart

    return jsonify({
        "success": True,
        "total": calculate_cart_total(cart),
        "cart_count": get_cart_count(cart),
        "item": {
            "variant_id": response_item["variant_id"],
            "size": response_item["size"],
            "quantity": response_item["quantity"]
        } if response_item else None,
        "removed": response_item is None,
        "merged": merged
    })


@app.context_processor
def inject_cart_count():
    cart = get_cart()
    return dict(cart_count=get_cart_count(cart))


def get_cart():
    return session.get('cart', [])


def normalize_size(size):
    if not size:
        return None
    return str(size).strip().upper()


def get_cart_count(cart):
    return sum(item["quantity"] for item in cart)


def calculate_cart_total(cart):
    total = 0

    for item in cart:
        row = db.execute("""
            SELECT products.price
            FROM variants
            JOIN products ON variants.product_id = products.id
            WHERE variants.id = ?
        """, item["variant_id"])

        if not row:
            continue

        total += row[0]["price"] * item["quantity"]

    return total


def handle_cart_error(message, status_code):
    if wants_json_response():
        return jsonify({
            "success": False,
            "message": message
        }), status_code

    flash(message, "error")
    return redirect(request.referrer or url_for('collection'))


def wants_json_response():
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.is_json
    )


def render_error_response(status_code, template_name, title, message):
    if wants_json_response():
        return jsonify({
            "success": False,
            "message": message,
            "status_code": status_code
        }), status_code

    return render_template(
        template_name,
        error_title=title,
        error_message=message
    ), status_code


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
