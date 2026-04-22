from flask import render_template, request, abort
from math import ceil

def register_shop_routes(app, db):
    @app.route('/collection')
    def collection():
        # get the current season
        row = db.execute('SELECT value FROM settings WHERE key = "season"')
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

        per_page = 2

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
            images=images
        )
