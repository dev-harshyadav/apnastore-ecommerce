from decimal import Decimal, InvalidOperation
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from sqlalchemy import or_
from app.extensions import db
from app.models import Product, Category, NewsletterSubscriber

storefront_bp = Blueprint("storefront", __name__)


@storefront_bp.route("/")
def home():
    """Editorial Homepage showcasing categories, curated products, and brand story."""
    categories = Category.query.filter_by(is_active=True).all()
    featured_products = (
        Product.query.filter_by(is_featured=True, is_active=True)
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )
    popular_products = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.stock_quantity.asc())  # Shows in-demand items
        .limit(4)
        .all()
    )
    return render_template(
        "storefront/home.html",
        categories=categories,
        featured_products=featured_products,
        popular_products=popular_products,
    )


@storefront_bp.route("/shop")
def catalog():
    """
    Dedicated Shop / Catalog page supporting:
    - Case-insensitive search
    - Category filtering
    - Server-side validated price ranges
    - Deterministic sorting
    - Server-side pagination with query param preservation
    """
    query = Product.query.filter_by(is_active=True)

    # 1. Search Query
    search_query = request.args.get("q", "").strip()
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
            )
        )

    # 2. Category Filter
    selected_category_slug = request.args.get("category", "").strip()
    selected_category = None
    if selected_category_slug:
        selected_category = Category.query.filter_by(slug=selected_category_slug, is_active=True).first()
        if selected_category:
            query = query.filter(Product.category_id == selected_category.id)

    # 3. Price Filter
    min_price_str = request.args.get("min_price", "").strip()
    max_price_str = request.args.get("max_price", "").strip()
    min_price = None
    max_price = None

    if min_price_str:
        try:
            min_val = Decimal(min_price_str)
            if min_val >= 0:
                min_price = min_val
                query = query.filter(Product.price >= min_price)
        except InvalidOperation:
            pass

    if max_price_str:
        try:
            max_val = Decimal(max_price_str)
            if max_val >= 0:
                max_price = max_val
                query = query.filter(Product.price <= max_price)
        except InvalidOperation:
            pass

    # 4. Sorting
    sort_by = request.args.get("sort", "recommended").strip()
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    else:
        # Recommended: Featured first, then newest
        query = query.order_by(Product.is_featured.desc(), Product.created_at.desc())

    # 5. Pagination
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    per_page = 12

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    categories = Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()

    return render_template(
        "storefront/catalog.html",
        products=products,
        pagination=pagination,
        categories=categories,
        search_query=search_query,
        selected_category=selected_category,
        selected_category_slug=selected_category_slug,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
    )


@storefront_bp.route("/category/<slug>")
def category_detail(slug):
    """Direct route to filter catalog by category slug."""
    return redirect(url_for("storefront.catalog", category=slug))


@storefront_bp.route("/product/<slug>")
def product_detail(slug):
    """Detailed view for an individual product."""
    # Look up by slug, fallback by id if numeric
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product and slug.isdigit():
        product = Product.query.filter_by(id=int(slug), is_active=True).first()

    if not product:
        abort(404)

    related_products = (
        Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_active == True,
        )
        .limit(4)
        .all()
    )

    return render_template(
        "storefront/product_detail.html",
        product=product,
        related_products=related_products,
    )


@storefront_bp.route("/categories")
def all_categories():
    """Directory of all active categories."""
    categories = Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()
    return render_template("storefront/categories.html", categories=categories)


@storefront_bp.route("/newsletter/subscribe", methods=["POST"])
def newsletter_subscribe():
    """Handles newsletter subscription with validation and database storage."""
    email = request.form.get("email", "").strip().lower()
    if not email or "@" not in email or "." not in email:
        flash("Please provide a valid email address.", "danger")
        return redirect(request.referrer or url_for("storefront.home"))

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        flash("You are already subscribed to the APNASTORE newsletter.", "info")
    else:
        subscriber = NewsletterSubscriber(email=email)
        db.session.add(subscriber)
        db.session.commit()
        flash("Thank you for subscribing! You will receive our seasonal neighbourhood edits.", "success")

    return redirect(request.referrer or url_for("storefront.home"))


@storefront_bp.route("/about")
def about():
    return render_template("storefront/about.html")


@storefront_bp.route("/terms")
def terms():
    return render_template("storefront/terms.html")


@storefront_bp.route("/privacy")
def privacy():
    return render_template("storefront/privacy.html")
