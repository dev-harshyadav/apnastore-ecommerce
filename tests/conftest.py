import os
import pytest
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import Administrator, Category, Product, Order, OrderItem


@pytest.fixture
def app():
    """Create application configured for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()

        # Seed sample category and products for tests
        cat1 = Category(name="Electronics", slug="electronics", description="Tech essentials", is_active=True)
        cat2 = Category(name="Books and Stationery", slug="books-and-stationery", description="Stationery", is_active=True)
        db.session.add_all([cat1, cat2])
        db.session.commit()

        p1 = Product(
            name="Aura Wireless Earbuds",
            slug="aura-wireless-earbuds",
            category_id=cat1.id,
            price=Decimal("1999.00"),
            compare_at_price=Decimal("2499.00"),
            stock_quantity=10,
            image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df",
            description="Active noise cancelling wireless earbuds with high-fidelity drivers.",
            is_featured=True,
            is_active=True,
        )

        p2 = Product(
            name="Hexagonal Brass Ballpoint Pen",
            slug="hexagonal-brass-ballpoint-pen",
            category_id=cat2.id,
            price=Decimal("499.00"),
            compare_at_price=None,
            stock_quantity=5,
            image_url="https://images.unsplash.com/photo-1583485088034-697b5bc54ccd",
            description="Machined solid brass ballpoint pen with smooth balanced balance.",
            is_featured=False,
            is_active=True,
        )

        p3 = Product(
            name="Sold Out Item",
            slug="sold-out-item",
            category_id=cat1.id,
            price=Decimal("799.00"),
            compare_at_price=None,
            stock_quantity=0,
            image_url="https://images.unsplash.com/photo-1583863788434",
            description="Item that has no stock.",
            is_featured=False,
            is_active=True,
        )

        # Seed demo admin
        admin = Administrator(name="Test Admin", email="admin@test.com")
        admin.set_password("AdminSecurePassword123!")
        db.session.add_all([p1, p2, p3, admin])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def admin_client(app, client):
    """A test client authenticated as the administrator."""
    with client.session_transaction() as sess:
        admin = Administrator.query.filter_by(email="admin@test.com").first()
        sess["_user_id"] = str(admin.id)
        sess["_fresh"] = True
    return client
