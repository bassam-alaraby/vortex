-- INSERT test data to products table.
INSERT INTO products (name, price, sizes, image) VALUES
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg'),
('Black Hoodie', 200, 'XL, L, M, S', 'images/black-hoodie-mockup.jpg');

-- UPDATE images link.
UPDATE products
SET image = REPLACE(image, '.jpg', '.png')
WHERE image LIKE '%.jpg';