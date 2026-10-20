import click
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models import Administrator, Category, Product

SAMPLE_CATEGORIES = [
    {
        "name": "Electronics",
        "slug": "electronics",
        "description": "Smart devices, modern audio, and reliable everyday tech essentials.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Fashion",
        "slug": "fashion",
        "description": "Handcrafted Indian textiles, sustainable daily wear, and timeless silhouettes.",
        "image_url": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Home and Living",
        "slug": "home-and-living",
        "description": "Artisanal ceramics, warm ambient lighting, and cosy home touches.",
        "image_url": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Books and Stationery",
        "slug": "books-and-stationery",
        "description": "Hardbound journals, brass writing tools, and curated stationery.",
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Accessories",
        "slug": "accessories",
        "description": "Fine leather goods, handcrafted jewelry, and minimalist daily carries.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Daily Essentials",
        "slug": "daily-essentials",
        "description": "Cold-pressed oils, organic spices, raw mountain honey, and pantry staples.",
        "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=800&q=80",
    },
]

SAMPLE_PRODUCTS = [
    # Electronics
    {
        "name": "Aura Active Noise-Cancelling Earbuds",
        "slug": "aura-active-noise-cancelling-earbuds",
        "category_slug": "electronics",
        "description": "Immersive sound with 32-hour battery life, titanium drivers, and ambient pass-through mode for urban commutes.",
        "price": Decimal("2499.00"),
        "compare_at_price": Decimal("2999.00"),
        "stock_quantity": 18,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "VoltFlow 65W GaN Fast Wall Charger",
        "slug": "voltflow-65w-gan-fast-wall-charger",
        "category_slug": "electronics",
        "description": "Compact gallium nitride fast charger with twin USB-C Power Delivery ports and one USB-A quick-charge port.",
        "price": Decimal("1499.00"),
        "compare_at_price": Decimal("1799.00"),
        "stock_quantity": 25,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Sonus Acoustic Bluetooth Desk Speaker",
        "slug": "sonus-acoustic-bluetooth-desk-speaker",
        "category_slug": "electronics",
        "description": "Wrapped in natural tweed fabric with walnut wood accents, Bluetooth 5.3 connectivity, and deep tactile bass.",
        "price": Decimal("3299.00"),
        "compare_at_price": None,
        "stock_quantity": 8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "ErgoDock 7-in-1 Aluminum USB-C Hub",
        "slug": "ergodock-7-in-1-aluminum-usb-c-hub",
        "category_slug": "electronics",
        "description": "4K HDMI 60Hz, 100W PD pass-through charging, high-speed SD/TF card readers, and USB 3.2 data channels.",
        "price": Decimal("1899.00"),
        "compare_at_price": Decimal("2299.00"),
        "stock_quantity": 4,  # low stock demo
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1625842268584-8f3296236761?auto=format&fit=crop&w=800&q=80",
    },

    # Fashion
    {
        "name": "Handspun Khadi Cotton Kurta - Indigo",
        "slug": "handspun-khadi-cotton-kurta-indigo",
        "category_slug": "fashion",
        "description": "Woven by traditional artisans using organic breathable cotton yarn, dyed with natural fermented indigo.",
        "price": Decimal("1650.00"),
        "compare_at_price": Decimal("1950.00"),
        "stock_quantity": 14,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Classic Washed Linen Overshirt",
        "slug": "classic-washed-linen-overshirt",
        "category_slug": "fashion",
        "description": "A relaxed silhouette tailored from 100% European flax linen. Softened with natural pumice stones for daily ease.",
        "price": Decimal("2199.00"),
        "compare_at_price": None,
        "stock_quantity": 10,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Everyday Heavyweight Organic Cotton Tee",
        "slug": "everyday-heavyweight-organic-cotton-tee",
        "category_slug": "fashion",
        "description": "240 GSM combed organic cotton with reinforced collar ribbing and a clean relaxed drape. Pre-shrunk finish.",
        "price": Decimal("799.00"),
        "compare_at_price": Decimal("999.00"),
        "stock_quantity": 30,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
    },

    # Home and Living
    {
        "name": "Sandalwood & Cardamom Soy Wax Candle",
        "slug": "sandalwood-cardamom-soy-wax-candle",
        "category_slug": "home-and-living",
        "description": "Hand-poured into a reusable matte amber vessel with a crackling wooden wick. 50 hours of calming aroma.",
        "price": Decimal("649.00"),
        "compare_at_price": Decimal("799.00"),
        "stock_quantity": 20,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Artisanal Ceramic Pour-Over Dripper",
        "slug": "artisanal-ceramic-pour-over-dripper",
        "category_slug": "home-and-living",
        "description": "Wheel-thrown stoneware coffee dripper with interior spiral ridges engineered for balanced, aromatic extraction.",
        "price": Decimal("890.00"),
        "compare_at_price": None,
        "stock_quantity": 12,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Handwoven Cotton Waffle Throw Blanket",
        "slug": "handwoven-cotton-waffle-throw-blanket",
        "category_slug": "home-and-living",
        "description": "Ultra-soft breathable cotton in a textured waffle weave. Perfect for couches, armchairs, and light evening warmth.",
        "price": Decimal("1450.00"),
        "compare_at_price": Decimal("1750.00"),
        "stock_quantity": 9,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Khurja Terracotta Planter with Saucer",
        "slug": "khurja-terracotta-planter-with-saucer",
        "category_slug": "home-and-living",
        "description": "Porous unglazed terracotta that promotes root aeration and prevents overwatering. Includes matching drip saucer.",
        "price": Decimal("499.00"),
        "compare_at_price": None,
        "stock_quantity": 3,  # low stock demo
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80",
    },

    # Books and Stationery
    {
        "name": "The Daily Journal: Hardbound Dot-Grid",
        "slug": "the-daily-journal-hardbound-dot-grid",
        "category_slug": "books-and-stationery",
        "description": "160 pages of 120 GSM fountain-pen friendly bamboo paper. Lies completely flat with dual ribbon bookmarks.",
        "price": Decimal("599.00"),
        "compare_at_price": Decimal("750.00"),
        "stock_quantity": 22,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Solid Brass Hexagonal Ballpoint Pen",
        "slug": "solid-brass-hexagonal-ballpoint-pen",
        "category_slug": "books-and-stationery",
        "description": "Machined from raw untreated brass that develops a personal vintage patina over time. Takes standard Parker G2 refills.",
        "price": Decimal("1299.00"),
        "compare_at_price": Decimal("1499.00"),
        "stock_quantity": 11,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Handmade Cotton Rag Paper Sketchbook",
        "slug": "handmade-cotton-rag-paper-sketchbook",
        "category_slug": "books-and-stationery",
        "description": "Deckle-edged 250 GSM recycled cotton paper bound in earthy linen bookcloth. Wonderful for watercolor and sketching.",
        "price": Decimal("849.00"),
        "compare_at_price": None,
        "stock_quantity": 7,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?auto=format&fit=crop&w=800&q=80",
    },

    # Accessories
    {
        "name": "Full-Grain Vegetable Tanned Leather Cardholder",
        "slug": "full-grain-vegetable-tanned-leather-cardholder",
        "category_slug": "accessories",
        "description": "Hand-stitched with waxed linen thread. Holds up to 8 cards and folded currency with quick-access central pocket.",
        "price": Decimal("899.00"),
        "compare_at_price": Decimal("1199.00"),
        "stock_quantity": 16,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Classic Amber Acetate Sunglasses",
        "slug": "classic-amber-acetate-sunglasses",
        "category_slug": "accessories",
        "description": "UV400 polarized mineral glass lenses housed in hand-polished cellulose acetate frames with five-barrel hinges.",
        "price": Decimal("1950.00"),
        "compare_at_price": Decimal("2450.00"),
        "stock_quantity": 6,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Handcrafted Canvas & Leather Daily Tote",
        "slug": "handcrafted-canvas-leather-daily-tote",
        "category_slug": "accessories",
        "description": "Water-resistant 18oz duck canvas reinforced with full-grain leather straps, padded laptop compartment, and brass hardware.",
        "price": Decimal("2150.00"),
        "compare_at_price": None,
        "stock_quantity": 8,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Thermal Vacuum Insulated Water Flask (750ml)",
        "slug": "thermal-vacuum-insulated-water-flask-750ml",
        "category_slug": "accessories",
        "description": "Food-grade 18/8 stainless steel keeps cold for 24 hours or hot for 12 hours. Sweat-proof powder-coated finish.",
        "price": Decimal("749.00"),
        "compare_at_price": Decimal("899.00"),
        "stock_quantity": 25,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=800&q=80",
    },

    # Daily Essentials
    {
        "name": "Raw Wildflower Honey from Kashmir (500g)",
        "slug": "raw-wildflower-honey-from-kashmir-500g",
        "category_slug": "daily-essentials",
        "description": "Unpasteurized and single-origin raw honey harvested sustainably from high-altitude Himalayan wildflower apiaries.",
        "price": Decimal("480.00"),
        "compare_at_price": Decimal("550.00"),
        "stock_quantity": 24,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Cold-Pressed Wooden Kohl Mustard Oil (1L)",
        "slug": "cold-pressed-wooden-kohl-mustard-oil-1l",
        "category_slug": "daily-essentials",
        "description": "Traditional cold extraction preserving natural pungency, aroma, and omega-3 fatty acids. Unrefined & chemical-free.",
        "price": Decimal("295.00"),
        "compare_at_price": None,
        "stock_quantity": 30,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Royal Kashmiri Saffron & Cardamom Chai Masala (100g)",
        "slug": "royal-kashmiri-saffron-cardamom-chai-masala-100g",
        "category_slug": "daily-essentials",
        "description": "Stone-ground whole spices blended with hand-picked Mongra saffron, green cardamom, dry ginger, and cinnamon bark.",
        "price": Decimal("399.00"),
        "compare_at_price": Decimal("450.00"),
        "stock_quantity": 15,
        "is_featured": True,
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=800&q=80",
    },
    {
        "name": "Cold-Processed Neem & Tulsi Bath Bar",
        "slug": "cold-processed-neem-tulsi-bath-bar",
        "category_slug": "daily-essentials",
        "description": "Cured for 6 weeks with pure coconut oil, therapeutic neem leaf extracts, and steam-distilled tulsi essential oil.",
        "price": Decimal("180.00"),
        "compare_at_price": Decimal("220.00"),
        "stock_quantity": 40,
        "is_featured": False,
        "image_url": "https://images.unsplash.com/photo-1607006314605-feed460b1348?auto=format&fit=crop&w=800&q=80",
    },
]


def register_cli_commands(app):
    @app.cli.command("init-db")
    def init_db():
        """Initialize the database tables."""
        db.create_all()
        click.echo(click.style("✓ Database tables initialized successfully.", fg="green"))

    @app.cli.command("seed-db")
    def seed_db():
        """Seed categories and realistic sample products into the database."""
        db.create_all()
        categories_map = {}

        # 1. Seed Categories
        added_categories = 0
        for cat_data in SAMPLE_CATEGORIES:
            existing = Category.query.filter_by(slug=cat_data["slug"]).first()
            if not existing:
                category = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    image_url=cat_data["image_url"],
                    is_active=True,
                )
                db.session.add(category)
                categories_map[cat_data["slug"]] = category
                added_categories += 1
            else:
                categories_map[cat_data["slug"]] = existing

        db.session.flush()

        # 2. Seed Products
        added_products = 0
        for prod_data in SAMPLE_PRODUCTS:
            category = categories_map.get(prod_data["category_slug"])
            if not category:
                category = Category.query.filter_by(slug=prod_data["category_slug"]).first()

            existing = Product.query.filter_by(slug=prod_data["slug"]).first()
            if not existing and category:
                product = Product(
                    name=prod_data["name"],
                    slug=prod_data["slug"],
                    description=prod_data["description"],
                    category_id=category.id,
                    price=prod_data["price"],
                    compare_at_price=prod_data.get("compare_at_price"),
                    stock_quantity=prod_data["stock_quantity"],
                    image_url=prod_data["image_url"],
                    is_featured=prod_data["is_featured"],
                    is_active=True,
                )
                db.session.add(product)
                added_products += 1

        db.session.commit()
        click.echo(
            click.style(
                f"✓ Seeding complete: {added_categories} categories and {added_products} products added.",
                fg="green",
            )
        )

    @app.cli.command("create-admin")
    @click.option("--name", prompt=True, default="Admin", help="Administrator full name")
    @click.option("--email", prompt=True, help="Administrator email address")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password")
    def create_admin(name, email, password):
        """Create or update an administrator account."""
        db.create_all()
        email = email.strip().lower()
        if not email or "@" not in email:
            click.echo(click.style("Error: A valid email address is required.", fg="red"))
            return

        admin = Administrator.query.filter_by(email=email).first()
        if admin:
            if click.confirm(f"Administrator {email} already exists. Do you want to update the password?"):
                admin.name = name
                admin.set_password(password)
                db.session.commit()
                click.echo(click.style(f"✓ Administrator {email} updated successfully.", fg="green"))
            else:
                click.echo("Cancelled.")
                return
        else:
            admin = Administrator(name=name, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            click.echo(click.style(f"✓ Administrator {email} created successfully.", fg="green"))
