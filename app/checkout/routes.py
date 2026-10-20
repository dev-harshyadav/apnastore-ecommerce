from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask_login import current_user
from app.extensions import db
from app.models import Product, Order, OrderItem
from app.cart.utils import get_cart_details, clear_session_cart
from app.checkout.forms import CheckoutForm

checkout_bp = Blueprint("checkout", __name__, url_prefix="/checkout")


@checkout_bp.route("/", methods=["GET", "POST"])
def index():
    """Checkout flow: displays order summary and validates customer delivery details."""
    cart_summary = get_cart_details()

    # Prevent checking out with an empty cart
    if not cart_summary["items"] or cart_summary["total_items"] == 0:
        flash("Your shopping cart is empty. Please add items to your cart before proceeding to checkout.", "info")
        return redirect(url_for("cart.view_cart"))

    # Check if any cart item is out of stock or exceeded
    stock_errors = []
    for item in cart_summary["items"]:
        if item["is_out_of_stock"]:
            stock_errors.append(f"'{item['product'].name}' is out of stock. Please remove it from your cart.")
        elif item["is_stock_exceeded"]:
            stock_errors.append(
                f"Requested quantity for '{item['product'].name}' ({item['quantity']}) exceeds available stock ({item['available_stock']})."
            )

    if stock_errors:
        for err in stock_errors:
            flash(err, "danger")
        return redirect(url_for("cart.view_cart"))

    form = CheckoutForm()

    if form.validate_on_submit():
        # Begin transactional order placement
        try:
            # 1. Lock and verify products inside transaction
            product_ids = [item["product"].id for item in cart_summary["items"]]
            products = Product.query.filter(Product.id.in_(product_ids)).with_for_update().all()
            products_by_id = {p.id: p for p in products}

            # Re-verify availability and stock right before commit
            for item in cart_summary["items"]:
                prod = products_by_id.get(item["product"].id)
                if not prod or not prod.is_active:
                    db.session.rollback()
                    flash(f"'{item['product'].name}' is no longer available. Please update your cart.", "danger")
                    return redirect(url_for("cart.view_cart"))

                if prod.stock_quantity < item["quantity"]:
                    db.session.rollback()
                    flash(
                        f"Insufficient stock for '{prod.name}'. Only {prod.stock_quantity} remaining. Please adjust your cart.",
                        "danger",
                    )
                    return redirect(url_for("cart.view_cart"))

            # 2. Recompute monetary amounts on the server
            subtotal = Decimal("0.00")
            order_items_to_create = []

            for item in cart_summary["items"]:
                prod = products_by_id[item["product"].id]
                qty = item["quantity"]
                unit_price = prod.price  # Server-side authoritative price
                line_total = unit_price * Decimal(qty)
                subtotal += line_total

                # Prepare OrderItem snapshot
                order_item = OrderItem(
                    product_id=prod.id,
                    product_name_snapshot=prod.name,
                    unit_price_snapshot=unit_price,
                    quantity=qty,
                    line_total=line_total,
                )
                order_items_to_create.append(order_item)

                # Deduct inventory
                prod.stock_quantity -= qty

            # Determine shipping fee
            free_threshold = cart_summary["free_shipping_shortfall"]
            if cart_summary["qualifies_for_free_shipping"]:
                shipping_amount = Decimal("0.00")
            else:
                shipping_amount = cart_summary["shipping"]

            total_amount = subtotal + shipping_amount

            # 3. Create Order
            order = Order(
                order_number=Order.generate_order_number(),
                customer_name=form.customer_name.data.strip(),
                customer_email=form.customer_email.data.strip().lower(),
                customer_phone=form.customer_phone.data.strip(),
                address_line=form.address_line.data.strip(),
                city=form.city.data.strip(),
                state=form.state.data.strip(),
                postal_code=form.postal_code.data.strip(),
                status="Confirmed",
                subtotal=subtotal,
                shipping_amount=shipping_amount,
                total_amount=total_amount,
                stock_restored=False,
            )

            for oi in order_items_to_create:
                order.items.append(oi)

            db.session.add(order)
            db.session.commit()

            # 4. Clear session cart and bind confirmation authorization
            clear_session_cart()
            session["last_order_number"] = order.order_number
            session.modified = True

            flash(f"Order #{order.order_number} placed successfully! Thank you for supporting your local store.", "success")
            return redirect(url_for("checkout.confirmation", order_number=order.order_number))

        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred while processing your order: {str(e)}. No charges were made.", "danger")
            return render_template("checkout/index.html", form=form, cart=cart_summary)

    return render_template("checkout/index.html", form=form, cart=cart_summary)


@checkout_bp.route("/confirmation/<order_number>")
def confirmation(order_number):
    """
    Protected order confirmation page.
    Only allows access if the order matches the current session's recent order
    or if an administrator is logged in.
    """
    order = Order.query.filter_by(order_number=order_number).first_or_404()

    # Authorization verification
    is_session_owner = session.get("last_order_number") == order_number
    is_admin = current_user.is_authenticated

    if not is_session_owner and not is_admin:
        abort(403)

    return render_template("checkout/confirmation.html", order=order)
