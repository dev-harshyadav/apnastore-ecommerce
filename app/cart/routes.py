from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.cart.utils import (
    get_cart_details,
    add_product_to_cart,
    set_product_quantity,
    remove_product_from_cart,
    clear_session_cart,
    get_cart_count,
)

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


@cart_bp.route("/")
def view_cart():
    """Display the customer's current shopping cart."""
    cart_summary = get_cart_details()
    return render_template("cart/index.html", cart=cart_summary)


@cart_bp.route("/add", methods=["POST"])
def add_item():
    """Add an item to the shopping cart."""
    is_json = request.is_json
    data = request.get_json() if is_json else request.form

    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        if is_json:
            return jsonify({"success": False, "message": "Invalid product or quantity specified."}), 400
        flash("Invalid product or quantity specified.", "danger")
        return redirect(request.referrer or url_for("cart.view_cart"))

    success, message = add_product_to_cart(product_id, quantity)
    cart_count = get_cart_count()

    if is_json:
        status_code = 200 if success else 400
        return jsonify({
            "success": success,
            "message": message,
            "cart_count": cart_count,
        }), status_code

    flash(message, "success" if success else "warning")
    return redirect(request.referrer or url_for("cart.view_cart"))


@cart_bp.route("/update", methods=["POST"])
def update_item():
    """Update the quantity of an item in the cart."""
    is_json = request.is_json
    data = request.get_json() if is_json else request.form

    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity"))
    except (ValueError, TypeError):
        if is_json:
            return jsonify({"success": False, "message": "Invalid quantity provided."}), 400
        flash("Invalid quantity provided.", "danger")
        return redirect(url_for("cart.view_cart"))

    success, message = set_product_quantity(product_id, quantity)
    cart_summary = get_cart_details()

    if is_json:
        return jsonify({
            "success": success,
            "message": message,
            "cart_count": cart_summary["total_items"],
            "subtotal": str(cart_summary["subtotal"]),
            "shipping": str(cart_summary["shipping"]),
            "grand_total": str(cart_summary["grand_total"]),
        })

    flash(message, "success" if success else "warning")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove", methods=["POST"])
def remove_item():
    """Remove an item completely from the cart."""
    is_json = request.is_json
    data = request.get_json() if is_json else request.form

    try:
        product_id = int(data.get("product_id"))
    except (ValueError, TypeError):
        if is_json:
            return jsonify({"success": False, "message": "Invalid product ID."}), 400
        flash("Invalid product ID.", "danger")
        return redirect(url_for("cart.view_cart"))

    success, message = remove_product_from_cart(product_id)
    cart_summary = get_cart_details()

    if is_json:
        return jsonify({
            "success": success,
            "message": message,
            "cart_count": cart_summary["total_items"],
            "subtotal": str(cart_summary["subtotal"]),
            "shipping": str(cart_summary["shipping"]),
            "grand_total": str(cart_summary["grand_total"]),
        })

    flash(message, "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/clear", methods=["POST"])
def clear():
    """Empty the entire shopping cart."""
    clear_session_cart()
    flash("Your shopping cart has been cleared.", "info")
    return redirect(url_for("cart.view_cart"))
