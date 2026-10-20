from app.models import Product, NewsletterSubscriber


def test_home_page_loads(client):
    """Test that homepage loads successfully with branding and featured items."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "APNASTORE" in html
    assert "Good things, closer to home." in html
    assert "Aura Wireless Earbuds" in html


def test_catalog_loads(client):
    """Test that the shop catalog loads with products."""
    response = client.get("/shop")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Discover the collection" in html
    assert "Aura Wireless Earbuds" in html
    assert "Hexagonal Brass Ballpoint Pen" in html


def test_product_detail_page(client):
    """Test viewing an individual product detail page."""
    response = client.get("/product/aura-wireless-earbuds")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Aura Wireless Earbuds" in html
    assert "1,999.00" in html
    assert "Add to Cart" in html


def test_missing_product_returns_404(client):
    """Test that a non-existent product slug returns 404."""
    response = client.get("/product/non-existent-product-slug")
    assert response.status_code == 404
    assert "Looking for something?" in response.data.decode("utf-8")


def test_search_filtering(client):
    """Test product search query filters accurately."""
    # Search for earbuds
    response = client.get("/shop?q=earbuds")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Aura Wireless Earbuds" in html
    assert "Hexagonal Brass Ballpoint Pen" not in html

    # Search for pen
    response2 = client.get("/shop?q=brass")
    assert response2.status_code == 200
    html2 = response2.data.decode("utf-8")
    assert "Hexagonal Brass Ballpoint Pen" in html2
    assert "Aura Wireless Earbuds" not in html2


def test_category_filtering(client):
    """Test category slug filter."""
    response = client.get("/shop?category=electronics")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Aura Wireless Earbuds" in html
    assert "Hexagonal Brass Ballpoint Pen" not in html


def test_price_range_filtering(client):
    """Test price filtering with min and max bounds."""
    # Only items between 300 and 600
    response = client.get("/shop?min_price=300&max_price=600")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Hexagonal Brass Ballpoint Pen" in html
    assert "Aura Wireless Earbuds" not in html


def test_sorting_functionality(client):
    """Test price low-to-high and high-to-low sorting."""
    res_asc = client.get("/shop?sort=price_asc")
    assert res_asc.status_code == 200
    html_asc = res_asc.data.decode("utf-8")
    pen_pos = html_asc.find("Hexagonal Brass Ballpoint Pen")
    earbuds_pos = html_asc.find("Aura Wireless Earbuds")
    # Pen (499) must appear before Earbuds (1999)
    assert pen_pos < earbuds_pos

    res_desc = client.get("/shop?sort=price_desc")
    assert res_desc.status_code == 200
    html_desc = res_desc.data.decode("utf-8")
    pen_pos_desc = html_desc.find("Hexagonal Brass Ballpoint Pen")
    earbuds_pos_desc = html_desc.find("Aura Wireless Earbuds")
    # Earbuds (1999) must appear before Pen (499)
    assert earbuds_pos_desc < pen_pos_desc


def test_newsletter_subscription(client, app):
    """Test newsletter subscription storage."""
    response = client.post(
        "/newsletter/subscribe",
        data={"email": "shopper@neighbourhood.in"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        sub = NewsletterSubscriber.query.filter_by(email="shopper@neighbourhood.in").first()
        assert sub is not None
