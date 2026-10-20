from decimal import Decimal
from app.extensions import db
from app.models import Product, Category


def test_inactive_product_hidden_from_storefront(client, app):
    """Test that deactivated or archived products do not appear in catalog or home."""
    with app.app_context():
        cat = Category.query.first()
        hidden_prod = Product(
            name="Archived Antique Watch",
            slug="archived-antique-watch",
            category_id=cat.id,
            price=Decimal("4999.00"),
            stock_quantity=1,
            image_url="https://images.unsplash.com/photo-watch",
            description="Rare discontinued antique timepiece.",
            is_active=False,
            is_featured=True,
        )
        db.session.add(hidden_prod)
        db.session.commit()

    # Should not appear in shop
    res_shop = client.get("/shop")
    assert "Archived Antique Watch" not in res_shop.data.decode("utf-8")

    # Accessing direct detail should return 404
    res_detail = client.get("/product/archived-antique-watch")
    assert res_detail.status_code == 404


def test_category_direct_route(client):
    """Test /category/<slug> redirects to filtered shop catalog."""
    response = client.get("/category/electronics")
    assert response.status_code == 302
    assert "/shop?category=electronics" in response.location


def test_categories_index_page(client):
    """Test /categories displays department directory."""
    response = client.get("/categories")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Shop by Category" in html
    assert "Electronics" in html
    assert "Books and Stationery" in html
