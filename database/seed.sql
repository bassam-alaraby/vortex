-- categories:
INSERT INTO categories (name) VALUES 
('boxy_fit'),     -- 1
('relaxed_fit');  -- 2

-- products:
INSERT INTO products (name, category_id, price) VALUES
('boxy_fit_t_shirt', 1, 200),     -- 1
('relaxed_fit_t_shirt', 2, 150);  -- 2


/*
=========================================================
==================== INSERT variants ====================
=========================================================
*/

INSERT INTO variants (product_id, name, color, style, design, image) VALUES
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 1
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 2
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 3
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 4
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 5
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 6
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 7
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp');  -- 8

INSERT INTO variants (product_id, name, color, style, design, image) VALUES
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 9
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 10
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 11
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 12
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 13
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 14
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 15
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp');  -- 16

INSERT INTO variants (product_id, name, color, style, design, image) VALUES
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 17
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 18
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 19
(1, 'Boxy White', 'white', 'plain', '', 'images/products/boxy_fit_t_shirt_white.webp'),        -- 20
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 21
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 22
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp'),  -- 23
(2, 'Relaxed Beige', 'beige', 'plain', '', 'images/products/relaxed_fit_t_shirt_beige.webp');  -- 24