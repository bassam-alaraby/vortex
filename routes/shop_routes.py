import uuid

from flask import render_template, request, abort, redirect, flash, url_for, session

from cloudinary_utils import cloudinary_image_url
from cloudinary_utils import upload_image
from math import ceil

from helpers import get_cart, get_custom_fee, normalize_size, validate_image_upload, _safe_redirect


def _handle_custom_upload(file_obj):
    _, validation_error = validate_image_upload(file_obj)
    if validation_error:
        raise ValueError(validation_error)

    try:
        return upload_image(file_obj, folder="custom_designs")
    except Exception as upload_error:
        raise RuntimeError("Image upload failed.") from upload_error


def _handle_custom_uploads(file_objects):
    valid_files = [file_obj for file_obj in file_objects if file_obj and file_obj.filename]
    if not valid_files:
        raise ValueError("Image file is required.")

    public_ids = []

    for file_obj in valid_files:
        public_id = _handle_custom_upload(file_obj)
        if public_id:
            public_ids.append(public_id)

    if not public_ids:
        raise RuntimeError("Image upload failed.")

    return public_ids

def register_shop_routes(app, db):
    @app.route('/collection')
    def collection():
        # get the current season
        row = db.execute("SELECT value FROM settings WHERE key = 'season'")
        current_season = row[0]['value'] if row else 'summer'

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
            variant_images.image
        FROM variants
        JOIN products
            ON products.id = variants.product_id
        JOIN variant_images 
            ON variant_images.variant_id = variants.id
        WHERE variant_images.is_primary = 1
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
            total_pages=total_pages,
            cloudinary_image_url=cloudinary_image_url,
        )

    @app.route('/custom')
    def custom_collection():
        row = db.execute("SELECT value FROM settings WHERE key = 'season'")
        current_season = row[0]['value'] if row else 'summer'

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

        per_page = 12

        count_query = '''
        SELECT COUNT(*) AS count
        FROM variants
        JOIN products
            ON products.id = variants.product_id
        WHERE variants.style = 'plain'
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
            variant_images.image
        FROM variants
        JOIN products
            ON products.id = variants.product_id
        JOIN variant_images
            ON variant_images.variant_id = variants.id
        WHERE variant_images.is_primary = 1
        AND variants.style = 'plain'
        '''

        params = []

        if current_season != 'all':
            query += ' AND products.season = ?'
            params.append(current_season)

        if fit:
            query += ' AND products.fit = ?'
            params.append(fit)

        query += ' LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        products = db.execute(query, *params)

        return render_template(
            'custom_collection.html',
            products=products,
            page=page,
            fit=fit,
            total_pages=total_pages,
            cloudinary_image_url=cloudinary_image_url,
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
                variants.style,
                products.price,
                variant_images.image
            FROM variants
            JOIN products 
                ON products.id = variants.product_id
            JOIN variant_images
                ON variant_images.variant_id = variants.id
            WHERE variants.id = ?
            AND variant_images.is_primary = 1
            ''', id)
        if not row:
            abort(404)

        variant_details = row[0]

        variant_id = variant_details['id']

        row = db.execute(
            '''
            SELECT image
            FROM variant_images
            WHERE variant_id = ?
            AND is_primary = 0
            ''', variant_id)
        images = [r['image'] for r in row]

        return render_template(
            'variant.html',
            variant_details=variant_details,
            images=images,
            cloudinary_image_url=cloudinary_image_url,
        )

    @app.route('/custom/<int:variant_id>', methods=['GET', 'POST'])
    def custom_design(variant_id):
        row = db.execute(
            '''
            SELECT
                variants.id,
                variants.name,
                variants.description,
                variants.style,
                products.price,
                variant_images.image
            FROM variants
            JOIN products
                ON products.id = variants.product_id
            JOIN variant_images
                ON variant_images.variant_id = variants.id
            WHERE variants.id = ?
            AND variant_images.is_primary = 1
            ''',
            variant_id,
        )

        if not row:
            abort(404)

        variant_details = row[0]

        if variant_details['style'] != 'plain':
            abort(404)

        base_price = float(variant_details['price'])
        custom_fee = get_custom_fee(db)
        total_price = base_price + custom_fee

        if request.method == 'POST':
            size = normalize_size(request.form.get('size'))

            try:
                quantity = int(request.form.get('quantity'))
            except (TypeError, ValueError):
                quantity = 0

            action = request.form.get('action')
            custom_image_files = request.files.getlist('custom_images')
            if not custom_image_files:
                custom_image_files = [request.files.get('custom_image')]

            if not size or quantity <= 0:
                flash('يرجى اختيار المقاس والكمية بشكل صحيح.', 'error')
                return render_template(
                    'custom_design.html',
                    variant_details=variant_details,
                    base_price=base_price,
                    custom_fee=custom_fee,
                    total_price=total_price,
                    cloudinary_image_url=cloudinary_image_url,
                )

            try:
                custom_image_public_ids = _handle_custom_uploads(custom_image_files)
            except ValueError:
                flash('يرجى رفع صورة JPG أو PNG صالحة.', 'error')
                return render_template(
                    'custom_design.html',
                    variant_details=variant_details,
                    base_price=base_price,
                    custom_fee=custom_fee,
                    total_price=total_price,
                    cloudinary_image_url=cloudinary_image_url,
                )
            except RuntimeError:
                flash('تعذر رفع التصميم، حاول مرة أخرى.', 'error')
                return render_template(
                    'custom_design.html',
                    variant_details=variant_details,
                    base_price=base_price,
                    custom_fee=custom_fee,
                    total_price=total_price,
                    cloudinary_image_url=cloudinary_image_url,
                )

            custom_image_count = len(custom_image_public_ids)
            applied_custom_fee = custom_fee * (2 if custom_image_count > 1 else 1)
            unit_price = base_price + applied_custom_fee

            cart = get_cart()
            cart.append({
                'variant_id': variant_id,
                'size': size,
                'quantity': quantity,
                'is_custom': 1,
                'custom_image': custom_image_public_ids[0],
                'custom_images': custom_image_public_ids,
                'custom_image_count': custom_image_count,
                'custom_fee_applied': applied_custom_fee,
                'base_price': base_price,
                'unit_price': unit_price,
                'cart_item_id': uuid.uuid4().hex,
            })
            session['cart'] = cart

            if action == 'buy_now':
                return redirect(url_for('checkout'))

            flash('Added to cart successfully', 'success')
            fallback_url = url_for('custom_design', variant_id=variant_id)
            return _safe_redirect(fallback_url)

        return render_template(
            'custom_design.html',
            variant_details=variant_details,
            base_price=base_price,
            custom_fee=custom_fee,
            total_price=total_price,
            cloudinary_image_url=cloudinary_image_url,
        )
