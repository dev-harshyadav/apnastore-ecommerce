from decimal import Decimal
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.models import Product, Category, Order, OrderItem
from app.admin.forms import ProductForm, CategoryForm, OrderStatusForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def generate_unique_slug(model, name, current_id=None):
    """Generate a clean URL slug and ensure uniqueness."""
    base_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not base_slug:
        base_slug = "item"

    slug = base_slug
    counter = 1
    while True:
        query = model.query.filter_by(slug=slug)
        if current_id:
            query = query.filter(model.id != current_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


@admin_bp.route("/")
@login_required
def dashboard():
    """Admin dashboard overview with metrics, recent orders, and inventory alerts."""
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter(Order.status.in_(["Pending", "Confirmed", "Processing"])).count()
    low_stock_products = Product.query.filter(Product.is_active == True, Product.stock_quantity <= 5).count()

    # Calculate real revenue from paid / active orders
    revenue_query = (
        db.session.query(func.sum(Order.total_amount))
        .filter(Order.status.in_(["Confirmed", "Processing", "Shipped", "Delivered"]))
        .scalar()
    )
    total_revenue = Decimal(str(revenue_query)) if revenue_query else Decimal("0.00")

    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    # Low stock items list
    low_stock_items = (
        Product.query.filter(Product.is_active == True, Product.stock_quantity <= 5)
        .order_by(Product.stock_quantity.asc())
        .limit(8)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        low_stock_products=low_stock_products,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        low_stock_items=low_stock_items,
    )


# -------------------------------------------------------------
# PRODUCT MANAGEMENT
# -------------------------------------------------------------

@admin_bp.route("/products")
@login_required
def products():
    """List all products with filtering, search, and pagination."""
    query = Product.query

    # Search filter
    search = request.args.get("q", "").strip()
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # Category filter
    category_id = request.args.get("category_id", type=int)
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Stock status filter
    stock_filter = request.args.get("stock", "").strip()
    if stock_filter == "low":
        query = query.filter(Product.stock_quantity <= 5, Product.stock_quantity > 0)
    elif stock_filter == "out":
        query = query.filter(Product.stock_quantity <= 0)

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=15, error_out=False)

    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        "admin/products.html",
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        selected_category_id=category_id,
        stock_filter=stock_filter,
    )


@admin_bp.route("/products/new", methods=["GET", "POST"])
@login_required
def product_new():
    """Create a new product."""
    form = ProductForm()
    if form.validate_on_submit():
        slug = form.slug.data.strip() if form.slug.data else ""
        if not slug:
            slug = generate_unique_slug(Product, form.name.data)

        product = Product(
            name=form.name.data.strip(),
            slug=slug,
            category_id=form.category_id.data,
            price=form.price.data,
            compare_at_price=form.compare_at_price.data,
            stock_quantity=form.stock_quantity.data,
            image_url=form.image_url.data.strip(),
            description=form.description.data.strip(),
            is_featured=form.is_featured.data,
            is_active=form.is_active.data,
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Product '{product.name}' created successfully.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", form=form, title="Add New Product")


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def product_edit(product_id):
    """Edit an existing product."""
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product, original_product_id=product.id)

    if form.validate_on_submit():
        slug = form.slug.data.strip() if form.slug.data else ""
        if not slug:
            slug = generate_unique_slug(Product, form.name.data, current_id=product.id)

        product.name = form.name.data.strip()
        product.slug = slug
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.compare_at_price = form.compare_at_price.data
        product.stock_quantity = form.stock_quantity.data
        product.image_url = form.image_url.data.strip()
        product.description = form.description.data.strip()
        product.is_featured = form.is_featured.data
        product.is_active = form.is_active.data

        db.session.commit()
        flash(f"Product '{product.name}' updated successfully.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", form=form, product=product, title=f"Edit {product.name}")


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def product_delete(product_id):
    """
    Delete or archive a product safely.
    Preserves historical order snapshots if product was purchased previously.
    """
    product = Product.query.get_or_404(product_id)
    # Check if this product has appeared in orders
    order_item_count = OrderItem.query.filter_by(product_id=product.id).count()

    if order_item_count > 0:
        # Archive product to preserve order history
        product.is_active = False
        db.session.commit()
        flash(
            f"Product '{product.name}' has appeared in {order_item_count} historical order items. It has been deactivated/archived to protect order records.",
            "info",
        )
    else:
        name = product.name
        db.session.delete(product)
        db.session.commit()
        flash(f"Product '{name}' has been permanently deleted.", "success")

    return redirect(url_for("admin.products"))


# -------------------------------------------------------------
# ORDER MANAGEMENT
# -------------------------------------------------------------

@admin_bp.route("/orders")
@login_required
def orders():
    """List orders with status filters and search."""
    query = Order.query

    status_filter = request.args.get("status", "").strip()
    if status_filter and status_filter in Order.VALID_STATUSES:
        query = query.filter(Order.status == status_filter)

    search = request.args.get("q", "").strip()
    if search:
        query = query.filter(
            (Order.order_number.ilike(f"%{search}%"))
            | (Order.customer_name.ilike(f"%{search}%"))
            | (Order.customer_email.ilike(f"%{search}%"))
        )

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=15, error_out=False)

    return render_template(
        "admin/orders.html",
        orders=pagination.items,
        pagination=pagination,
        status_filter=status_filter,
        search=search,
        valid_statuses=Order.VALID_STATUSES,
    )


@admin_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@login_required
def order_detail(order_id):
    """View full order details and update order status."""
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm(status=order.status)

    if form.validate_on_submit():
        new_status = form.status.data

        if not order.can_transition_to(new_status):
            flash(f"Invalid status transition from {order.status} to {new_status}.", "danger")
            return redirect(url_for("admin.order_detail", order_id=order.id))

        # Handle cancellation and inventory restoration
        if new_status == "Cancelled" and not order.stock_restored:
            for item in order.items:
                if item.product:
                    item.product.stock_quantity += item.quantity
            order.stock_restored = True
            flash("Order cancelled. Associated inventory quantities have been safely restored.", "warning")

        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.order_number} status updated to {new_status}.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    return render_template("admin/order_detail.html", order=order, form=form)


# -------------------------------------------------------------
# CATEGORY MANAGEMENT
# -------------------------------------------------------------

@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    """List and create categories."""
    form = CategoryForm()
    if form.validate_on_submit():
        slug = form.slug.data.strip() if form.slug.data else ""
        if not slug:
            slug = generate_unique_slug(Category, form.name.data)

        category = Category(
            name=form.name.data.strip(),
            slug=slug,
            description=form.description.data.strip() if form.description.data else None,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            is_active=form.is_active.data,
        )
        db.session.add(category)
        db.session.commit()
        flash(f"Category '{category.name}' created successfully.", "success")
        return redirect(url_for("admin.categories"))

    all_categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/categories.html", categories=all_categories, form=form)
