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

CREATE TABLE product_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    image TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id)
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
    stock INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (product_id) REFERENCES products(id)
    -- UNIQUE(product_id, color, style, design)
);

-- -- variant_sizes table
-- CREATE TABLE variant_sizes (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     variant_id INTEGER,
--     size TEXT NOT NULL,
--     stock INTEGER NOT NULL,
--     FOREIGN KEY (variant_id) REFERENCES variants(id),
--     UNIQUE(variant_id, size)
-- );

-- -- variant_images table
-- CREATE TABLE variant_images (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     variant_id INTEGER,
--     image TEXT NOT NULL,
--     is_primary INTEGER NOT NULL DEFAULT 0,
--     FOREIGN KEY (variant_id) REFERENCES variants(id)
-- );

-- cart table
CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER,
    quantity INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    FOREIGN KEY (variant_id) REFERENCES variants(id),
    UNIQUE(variant_id, session_id)
);

-- orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    total_price REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- order_items table
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    variant_id INTEGER,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (variant_id) REFERENCES variants(id)
);