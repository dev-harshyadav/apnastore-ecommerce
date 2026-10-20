from decimal import Decimal
from app.extensions import db
from app.models import Product, Order, OrderItem


def test_empty_cart_cannot_checkout(client):
    """Test that visiting checkout with an empty cart redirects back to cart."""
    response = client.get("/checkout/", follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Your shopping cart is empty" in html


def test_checkout_form_validation(client, app):
    """Test frontend/backend validation on checkout form fields."""
    with app.app_context():
        product = Product.query.filter_by(slug="hexagonal-brass-ballpoint-pen").first()
        pid = product.id

    client.post("/cart/add", data={"product_id": pid, "quantity": 1})

    # Submit invalid phone and invalid PIN code
    response = client.post(
        "/checkout/",
        data={
            "customer_name": "A",
            "customer_email": "invalid-email",
            "customer_phone": "12345",  # invalid phone
            "address_line": "Apt",
            "city": "",
            "state": "",
            "postal_code": "999",       # invalid PIN
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Please enter a valid 10-digit Indian mobile number" in html or "Please enter a valid email address" in html


def test_successful_order_placement(client, app):
    """
    Test complete order lifecycle:
    1. Cart has items
    2. Submit valid checkout information
    3. Order record persisted in DB
    4. OrderItem snapshots created
    5. Inventory decreased
    6. Cart cleared
    7. Redirected to Confirmation
    """
    with app.app_context():
        product = Product.query.filter_by(slug="aura-wireless-earbuds").first()
        initial_stock = product.stock_quantity  # 10
        pid = product.id

    # Add 2 earbuds to cart
    client.post("/cart/add", data={"product_id": pid, "quantity": 2})

    # Submit checkout
    response = client.post(
        "/checkout/",
        data={
            "customer_name": "Priya Sharma",
            "customer_email": "priya.sharma@example.com",
            "customer_phone": "9876543210",
            "address_line": "12/A, Sunshine Apartments, Indiranagar",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560038",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Thank you for your order!" in html
    assert "Priya Sharma" in html
    assert "Bengaluru, Karnataka" in html
    assert "APNA-" in html

    # Verify Database state
    with app.app_context():
        order = Order.query.filter_by(customer_email="priya.sharma@example.com").first()
        assert order is not None
        assert order.status == "Confirmed"
        assert len(order.items) == 1
        
        item = order.items[0]
        assert item.product_name_snapshot == "Aura Wireless Earbuds"
        assert item.quantity == 2
        assert item.unit_price_snapshot == Decimal("1999.00")
        assert item.line_total == Decimal("3998.00")

        # Inventory check: 10 - 2 = 8
        updated_product = db.session.get(Product, pid)
        assert updated_product.stock_quantity == initial_stock - 2

    # Verify Cart is now cleared
    cart_res = client.get("/cart/")
    assert "Your shopping bag is empty" in cart_res.data.decode("utf-8")


def test_unauthorized_confirmation_access(client, app):
    """Test that unauthorized visitors cannot inspect private order confirmations."""
    with app.app_context():
        order = Order(
            order_number="APNA-20261020-SECRET",
            customer_name="Secret Customer",
            customer_email="secret@example.com",
            customer_phone="9876543210",
            address_line="Private Villa",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            status="Confirmed",
            subtotal=Decimal("1000.00"),
            shipping_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
        )
        db.session.add(order)
        db.session.commit()

    # Access without matching session order token or admin login
    response = client.get("/checkout/confirmation/APNA-20261020-SECRET")
    assert response.status_code == 403
    assert "Access Restricted" in response.data.decode("utf-8")
