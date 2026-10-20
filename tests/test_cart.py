from decimal import Decimal
from app.models import Product


def test_empty_cart_view(client):
    """Test viewing an empty cart displays appropriate empty state."""
    response = client.get("/cart/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Your shopping bag is empty" in html


def test_add_product_to_cart(client, app):
    """Test adding an available product to the cart."""
    with app.app_context():
        product = Product.query.filter_by(slug="aura-wireless-earbuds").first()
        pid = product.id

    response = client.post(
        "/cart/add",
        data={"product_id": pid, "quantity": 2},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Aura Wireless Earbuds" in html
    assert "Qty" in html or "qty-input" in html


def test_add_to_cart_ajax(client, app):
    """Test JSON/AJAX add-to-cart endpoint."""
    with app.app_context():
        product = Product.query.filter_by(slug="hexagonal-brass-ballpoint-pen").first()
        pid = product.id

    response = client.post(
        "/cart/add",
        json={"product_id": pid, "quantity": 1},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["cart_count"] == 1


def test_reject_adding_out_of_stock_item(client, app):
    """Test that out-of-stock items cannot be added."""
    with app.app_context():
        product = Product.query.filter_by(slug="sold-out-item").first()
        pid = product.id

    response = client.post(
        "/cart/add",
        data={"product_id": pid, "quantity": 1},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "currently out of stock" in html


def test_reject_quantity_exceeding_stock(client, app):
    """Test that adding more items than available stock is rejected."""
    with app.app_context():
        product = Product.query.filter_by(slug="hexagonal-brass-ballpoint-pen").first()
        pid = product.id
        stock = product.stock_quantity  # 5 units

    response = client.post(
        "/cart/add",
        data={"product_id": pid, "quantity": stock + 5},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Only 5 units available in stock" in html


def test_update_cart_quantity_and_remove(client, app):
    """Test updating item quantity and removing item."""
    with app.app_context():
        product = Product.query.filter_by(slug="aura-wireless-earbuds").first()
        pid = product.id

    # 1. Add item
    client.post("/cart/add", data={"product_id": pid, "quantity": 1})

    # 2. Update quantity to 3
    res_update = client.post(
        "/cart/update",
        data={"product_id": pid, "quantity": 3},
        follow_redirects=True,
    )
    assert res_update.status_code == 200
    html_update = res_update.data.decode("utf-8")
    assert "Cart updated successfully." in html_update

    # 3. Remove item
    res_remove = client.post(
        "/cart/remove",
        data={"product_id": pid},
        follow_redirects=True,
    )
    assert res_remove.status_code == 200
    html_remove = res_remove.data.decode("utf-8")
    assert "Item removed from cart." in html_remove
    assert "Your shopping bag is empty" in html_remove


def test_cart_shipping_calculation(client, app):
    """Test shipping calculation: under ₹999 adds flat fee, ₹999+ qualifies for free shipping."""
    with app.app_context():
        pen = Product.query.filter_by(slug="hexagonal-brass-ballpoint-pen").first()  # ₹499
        earbuds = Product.query.filter_by(slug="aura-wireless-earbuds").first()      # ₹1999

    # Case A: Subtotal ₹499 (< ₹999) -> shipping is ₹60.00
    client.post("/cart/add", data={"product_id": pen.id, "quantity": 1})
    res_a = client.get("/cart/")
    html_a = res_a.data.decode("utf-8")
    assert "60.00" in html_a
    assert "559.00" in html_a  # 499 + 60

    # Case B: Add earbuds (total > ₹999) -> shipping is FREE
    client.post("/cart/add", data={"product_id": earbuds.id, "quantity": 1})
    res_b = client.get("/cart/")
    html_b = res_b.data.decode("utf-8")
    assert "FREE" in html_b
    assert "2,498.00" in html_b  # 499 + 1999 = 2498
