from decimal import Decimal
from app.extensions import db
from app.models import Product, Order, OrderItem


def test_order_number_format(app):
    """Test order numbers follow expected APNA-YYYYMMDD-XXXX format."""
    with app.app_context():
        order_num = Order.generate_order_number()
        assert order_num.startswith("APNA-")
        parts = order_num.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # 6-char hex suffix


def test_order_item_snapshot_preservation(client, admin_client, app):
    """
    Test that updating or archiving a product later does not alter historical OrderItem snapshots.
    """
    with app.app_context():
        product = Product.query.filter_by(slug="aura-wireless-earbuds").first()
        pid = product.id
        original_price = product.price

    # Customer buys earbuds at original price (₹1999)
    client.post("/cart/add", data={"product_id": pid, "quantity": 1})
    client.post(
        "/checkout/",
        data={
            "customer_name": "Rohan Verma",
            "customer_email": "rohan.verma@example.com",
            "customer_phone": "9812345678",
            "address_line": "402 Royal Palms",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
        },
    )

    # Admin changes product price to ₹2999
    with app.app_context():
        prod_to_edit = db.session.get(Product, pid)
        prod_to_edit.price = Decimal("2999.00")
        db.session.commit()

    # Verify that the historical order item snapshot still preserves the original ₹1999 price
    with app.app_context():
        order = Order.query.filter_by(customer_email="rohan.verma@example.com").first()
        assert len(order.items) == 1
        assert order.items[0].unit_price_snapshot == original_price
        assert order.items[0].unit_price_snapshot == Decimal("1999.00")
