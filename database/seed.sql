-- settings:
INSERT INTO settings (key, value)
VALUES ('season', 'summer');

-- products:
INSERT INTO products (name, fit, price, season) VALUES
('t_shirt', 'boxy', 200, 'summer'),     -- 1
('t_shirt', 'relaxed', 250, 'summer');  -- 2


/*
=========================================================
==================== INSERT variants ====================
=========================================================
*/

INSERT INTO variants (product_id, name, description, color, style, design) VALUES
(1, 'تيشيرت صيفيي بوكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'white', 'plain', ''),   -- 1
(1, 'تيشيرت صيفيي بوكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'white', 'plain', ''),   -- 2
(1, 'تيشيرت صيفيي بوكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'white', 'plain', ''),   -- 3
(1, 'تيشيرت صيفيي بوكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'white', 'plain', ''),   -- 4
(2, 'تيشيرت صيفيي ريلاكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'beige', 'plain', ''),  -- 5
(2, 'تيشيرت صيفيي ريلاكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'beige', 'plain', ''),  -- 6
(2, 'تيشيرت صيفيي ريلاكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'beige', 'plain', ''),  -- 7
(2, 'تيشيرت صيفيي ريلاكس فيت', 'قماشة ضد الوبرة والانكماش، خامة عالية الجودة', 'beige', 'plain', '');  -- 8


INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(1, 'assets/products/t_shirt_boxy/plain/white/1.webp', 1),
(1, 'assets/products/t_shirt_boxy/plain/green/1.webp', 0),
(1, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 0),
(1, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 0);

INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(2, 'assets/products/t_shirt_boxy/plain/white/1.webp', 1),
(2, 'assets/products/t_shirt_boxy/plain/green/1.webp', 0),
(2, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 0),
(2, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 0);


INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(3, 'assets/products/t_shirt_boxy/plain/white/1.webp', 0),
(3, 'assets/products/t_shirt_boxy/plain/green/1.webp', 1),
(3, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 0),
(3, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 0);

INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(4, 'assets/products/t_shirt_boxy/plain/white/1.webp', 0),
(4, 'assets/products/t_shirt_boxy/plain/green/1.webp', 1),
(4, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 0),
(4, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 0);


INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(5, 'assets/products/t_shirt_boxy/plain/white/1.webp', 0),
(5, 'assets/products/t_shirt_boxy/plain/green/1.webp', 0),
(5, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 1),
(5, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 0);

INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(6, 'assets/products/t_shirt_boxy/plain/white/1.webp', 0),
(6, 'assets/products/t_shirt_boxy/plain/green/1.webp', 0),
(6, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 1),
(6, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 0);


INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(7, 'assets/products/t_shirt_boxy/plain/white/1.webp', 0),
(7, 'assets/products/t_shirt_boxy/plain/green/1.webp', 0),
(7, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 0),
(7, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 1);

INSERT INTO variant_images (variant_id, image, is_primary) VALUES
(8, 'assets/products/t_shirt_boxy/plain/white/1.webp', 0),
(8, 'assets/products/t_shirt_boxy/plain/green/1.webp', 0),
(8, 'assets/products/t_shirt_relaxed/plain/beige/1.webp', 0),
(8, 'assets/products/t_shirt_relaxed/plain/mint_green/1.webp', 1);


INSERT INTO variant_stock (variant_id, size, stock) VALUES
(1, 'L', 10), (1, 'XL', 8), (1, 'XXL', 5), (1, 'XXXL', 2),
(2, 'L', 10), (2, 'XL', 8), (2, 'XXL', 5), (2, 'XXXL', 2),
(3, 'L', 10), (3, 'XL', 8), (3, 'XXL', 5), (3, 'XXXL', 2),
(4, 'L', 10), (4, 'XL', 8), (4, 'XXL', 5), (4, 'XXXL', 2),
(5, 'L', 10), (5, 'XL', 8), (5, 'XXL', 5), (5, 'XXXL', 2),
(6, 'L', 10), (6, 'XL', 8), (6, 'XXL', 5), (6, 'XXXL', 2),
(7, 'L', 10), (7, 'XL', 8), (7, 'XXL', 5), (7, 'XXXL', 2),
(8, 'L', 10), (8, 'XL', 8), (8, 'XXL', 5), (8, 'XXXL', 2);