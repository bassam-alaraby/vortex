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