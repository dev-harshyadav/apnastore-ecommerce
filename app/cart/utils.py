from decimal import Decimal
from flask import session, current_app
from app.extensions import db
from app.models import Product


def get_session_cart() -> dict:
    """Return the raw session cart dictionary mapping str(product_id) -> quantity."""
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]


def get_cart_count() -> int:
    """Return total number of items currently in the cart."""
    cart = get_session_cart()
    try:
        return sum(int(qty) for qty in cart.values() if int(qty) > 0)
    except (ValueError, TypeError):
        return 0


def get_cart_details():
    """
    Fetch active database products for all items in the session cart.
    Calculates subtotal, shipping fee, and grand total strictly on the server.
    Cleans up any invalid, deleted, or zero-quantity entries.
    """
    cart = get_session_cart()
    if not cart:
        return {
            "items": [],
            "subtotal": Decimal("0.00"),
            "shipping": Decimal("0.00"),
            "grand_total": Decimal("0.00"),
            "total_items": 0,
            "free_shipping_shortfall": current_app.config["FREE_SHIPPING_THRESHOLD"],
            "qualifies_for_free_shipping": False,
        }

    # Parse and filter product IDs
    valid_cart_map = {}
    for pid_str, qty in list(cart.items()):
        try:
            pid = int(pid_str)
            q = int(qty)
            if q > 0:
                valid_cart_map[pid] = q
        except (ValueError, TypeError):
            continue

    if not valid_cart_map:
        session["cart"] = {}
        session.modified = True
        return {
            "items": [],
            "subtotal": Decimal("0.00"),
            "shipping": Decimal("0.00"),
            "grand_total": Decimal("0.00"),
            "total_items": 0,
            "free_shipping_shortfall": current_app.config["FREE_SHIPPING_THRESHOLD"],
            "qualifies_for_free_shipping": False,
        }

    products = Product.query.filter(Product.id.in_(valid_cart_map.keys())).all()
    products_by_id = {p.id: p for p in products}

    items = []
    subtotal = Decimal("0.00")
    total_items = 0
    updated_cart = {}

    for pid, requested_qty in valid_cart_map.items():
        product = products_by_id.get(pid)
        if not product or not product.is_active:
            # Skip deleted or deactivated products
            continue

        # Adjust quantity if it exceeds available stock
        actual_qty = min(requested_qty, product.stock_quantity) if product.stock_quantity > 0 else 0
        
        # Even if out of stock, we show it with warning so customer knows to remove or reduce
        line_total = product.price * Decimal(actual_qty) if actual_qty > 0 else Decimal("0.00")
        
        items.append({
            "product": product,
            "quantity": requested_qty,
            "actual_quantity": actual_qty,
            "unit_price": product.price,
            "line_total": line_total,
            "is_out_of_stock": product.stock_quantity <= 0,
            "is_stock_exceeded": requested_qty > product.stock_quantity,
            "available_stock": product.stock_quantity,
        })

        if actual_qty > 0:
            subtotal += line_total
            total_items += actual_qty
            updated_cart[str(pid)] = requested_qty

    # Save cleaned cart back to session
    session["cart"] = updated_cart
    session.modified = True

    # Calculate shipping
    free_threshold = current_app.config["FREE_SHIPPING_THRESHOLD"]
    flat_shipping = current_app.config["SHIPPING_FLAT_RATE"]
    
    if subtotal == Decimal("0.00") or subtotal >= free_threshold:
        shipping = Decimal("0.00")
        qualifies_for_free_shipping = subtotal >= free_threshold
        free_shipping_shortfall = Decimal("0.00")
    else:
        shipping = flat_shipping
        qualifies_for_free_shipping = False
        free_shipping_shortfall = free_threshold - subtotal

    grand_total = subtotal + shipping

    return {
        "items": items,
        "cart_items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total,
        "total_items": total_items,
        "free_shipping_shortfall": free_shipping_shortfall,
        "qualifies_for_free_shipping": qualifies_for_free_shipping,
    }


def add_product_to_cart(product_id: int, quantity: int = 1) -> tuple[bool, str]:
    """
    Add a product to the cart with server-side stock verification.
    Returns (success, message).
    """
    if quantity <= 0:
        return False, "Quantity must be at least 1."

    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return False, "Product is not available."

    if product.stock_quantity <= 0:
        return False, f"Sorry, '{product.name}' is currently out of stock."

    cart = get_session_cart()
    key = str(product_id)
    current_qty = cart.get(key, 0)
    new_qty = current_qty + quantity

    if new_qty > product.stock_quantity:
        max_addable = max(0, product.stock_quantity - current_qty)
        if max_addable <= 0:
            return False, f"You already have all available units ({product.stock_quantity}) of '{product.name}' in your cart."
        return False, f"Only {product.stock_quantity} units available in stock. You can add at most {max_addable} more."

    cart[key] = new_qty
    session["cart"] = cart
    session.modified = True
    return True, f"Added {quantity} × '{product.name}' to your cart."


def set_product_quantity(product_id: int, quantity: int) -> tuple[bool, str]:
    """
    Set exact quantity for a product in the cart. If <= 0, item is removed.
    Returns (success, message).
    """
    cart = get_session_cart()
    key = str(product_id)

    if quantity <= 0:
        if key in cart:
            del cart[key]
            session["cart"] = cart
            session.modified = True
            return True, "Item removed from your cart."
        return True, "Item not in cart."

    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        if key in cart:
            del cart[key]
            session["cart"] = cart
            session.modified = True
        return False, "This product is no longer available."

    if quantity > product.stock_quantity:
        cart[key] = product.stock_quantity
        session["cart"] = cart
        session.modified = True
        return False, f"Quantity adjusted to maximum available stock ({product.stock_quantity})."

    cart[key] = quantity
    session["cart"] = cart
    session.modified = True
    return True, "Cart updated successfully."


def remove_product_from_cart(product_id: int) -> tuple[bool, str]:
    """Remove a product completely from the cart."""
    cart = get_session_cart()
    key = str(product_id)
    if key in cart:
        del cart[key]
        session["cart"] = cart
        session.modified = True
        return True, "Item removed from cart."
    return False, "Item was not found in your cart."


def clear_session_cart():
    """Empty the session cart completely."""
    session["cart"] = {}
    session.modified = True
