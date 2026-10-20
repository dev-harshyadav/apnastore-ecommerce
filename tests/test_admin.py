from decimal import Decimal
from app.extensions import db
from app.models import Administrator, Product, Category, Order, OrderItem


def test_admin_login_success(client):
    """Test administrator sign in with valid credentials."""
    response = client.post(
        "/auth/login",
        data={"email": "admin@test.com", "password": "AdminSecurePassword123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Dashboard Overview" in html
    assert "Welcome back" in html


def test_admin_login_failure(client, app):
    """Test administrator sign in with invalid password."""
    response = client.post(
        "/auth/login",
        data={"email": "admin@test.com", "password": "WrongPassword!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Invalid email or password" in html

    with app.app_context():
        admin = Administrator.query.filter_by(email="admin@test.com").first()
        assert admin.failed_login_attempts == 1


def test_unauthorized_admin_access_redirects(client):
    """Test that unauthorized visitors cannot access admin routes."""
    res_dash = client.get("/admin/")
    assert res_dash.status_code == 302
    assert "/auth/login" in res_dash.location

    res_prod = client.get("/admin/products")
    assert res_prod.status_code == 302
    assert "/auth/login" in res_prod.location


def test_admin_product_creation(admin_client, app):
    """Test creating a new product from the admin interface."""
    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    response = admin_client.post(
        "/admin/products/new",
        data={
            "name": "Kashmir Wildflower Honey",
            "slug": "kashmir-wildflower-honey",
            "category_id": cat_id,
            "price": "450.00",
            "compare_at_price": "550.00",
            "stock_quantity": 25,
            "image_url": "https://images.unsplash.com/photo-honey",
            "description": "Pure single origin mountain raw honey.",
            "is_featured": "y",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Kashmir Wildflower Honey" in html

    with app.app_context():
        prod = Product.query.filter_by(slug="kashmir-wildflower-honey").first()
        assert prod is not None
        assert prod.price == Decimal("450.00")
        assert prod.stock_quantity == 25


def test_admin_product_edit(admin_client, app):
    """Test editing an existing product's stock and price."""
    with app.app_context():
        p = Product.query.filter_by(slug="aura-wireless-earbuds").first()
        pid = p.id
        cat_id = p.category_id

    response = admin_client.post(
        f"/admin/products/{pid}/edit",
        data={
            "name": "Aura Wireless Earbuds Pro",
            "slug": "aura-wireless-earbuds",
            "category_id": cat_id,
            "price": "2299.00",
            "compare_at_price": "2699.00",
            "stock_quantity": 50,
            "image_url": "https://images.unsplash.com/photo-earbuds-pro",
            "description": "Updated active noise cancelling earbuds with spatial audio.",
            "is_featured": "y",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Aura Wireless Earbuds Pro" in html

    with app.app_context():
        updated = db.session.get(Product, pid)
        assert updated.name == "Aura Wireless Earbuds Pro"
        assert updated.price == Decimal("2299.00")
        assert updated.stock_quantity == 50


def test_admin_order_status_update_and_cancellation(admin_client, app):
    """Test order status updates and automatic stock restoration upon cancellation."""
    with app.app_context():
        prod = Product.query.filter_by(slug="hexagonal-brass-ballpoint-pen").first()
        prod_id = prod.id
        initial_stock = prod.stock_quantity  # 5

        # Create an order with 2 pens
        order = Order(
            order_number="APNA-TEST-CANCEL",
            customer_name="Test Customer",
            customer_email="test.customer@example.com",
            customer_phone="9876543210",
            address_line="Main Street",
            city="Delhi",
            state="Delhi",
            postal_code="110001",
            status="Confirmed",
            subtotal=Decimal("998.00"),
            shipping_amount=Decimal("0.00"),
            total_amount=Decimal("998.00"),
            stock_restored=False,
        )
        item = OrderItem(
            product_id=prod.id,
            product_name_snapshot=prod.name,
            unit_price_snapshot=prod.price,
            quantity=2,
            line_total=Decimal("998.00"),
        )
        order.items.append(item)
        prod.stock_quantity -= 2  # Simulating stock reduced on order
        db.session.add(order)
        db.session.commit()
        order_id = order.id

    # 1. Update status to Shipped
    res_ship = admin_client.post(
        f"/admin/orders/{order_id}",
        data={"status": "Shipped"},
        follow_redirects=True,
    )
    assert res_ship.status_code == 200
    with app.app_context():
        ord_db = db.session.get(Order, order_id)
        assert ord_db.status == "Shipped"
        assert ord_db.stock_restored is False

    # 2. Cancel order -> verify stock restored
    res_cancel = admin_client.post(
        f"/admin/orders/{order_id}",
        data={"status": "Cancelled"},
        follow_redirects=True,
    )
    assert res_cancel.status_code == 200
    with app.app_context():
        ord_db = db.session.get(Order, order_id)
        assert ord_db.status == "Cancelled"
        assert ord_db.stock_restored is True

        prod_db = db.session.get(Product, prod_id)
        # Stock should be back to initial_stock (3 + 2 = 5)
        assert prod_db.stock_quantity == initial_stock
