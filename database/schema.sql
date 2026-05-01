-- settings table
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    fit TEXT NOT NULL,
    price REAL NOT NULL,
    season TEXT NOT NULL
);

-- variants table
CREATE TABLE variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    color TEXT NOT NULL,
    style TEXT NOT NULL,              -- 'plain' or 'printed'
    design TEXT NOT NULL DEFAULT '',  -- '' for plain, ex: 'Fire' for printed
    FOREIGN KEY (product_id) REFERENCES products(id)
    UNIQUE(product_id, color, style, design)
); 

-- variant_images table
CREATE TABLE variant_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER,
    image TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (variant_id) REFERENCES variants(id)
);

-- orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    notes TEXT,
    total_price REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- order_items table
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    size TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    custom_image TEXT,
    is_custom INTEGER DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (variant_id) REFERENCES variants(id)
);
