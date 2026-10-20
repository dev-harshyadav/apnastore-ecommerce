from app.models import Administrator


def test_password_is_properly_hashed():
    """Verify administrator passwords are encrypted with one-way salted hashes."""
    admin = Administrator(name="Security Officer", email="sec@apnastore.in")
    admin.set_password("PlainTextPasswordToProtect!")

    assert admin.password_hash != "PlainTextPasswordToProtect!"
    assert admin.password_hash.startswith("scrypt:") or admin.password_hash.startswith("pbkdf2:")
    assert admin.check_password("PlainTextPasswordToProtect!") is True
    assert admin.check_password("WrongPassword") is False


def test_safe_redirect_prevents_open_redirect(client):
    """Test that login redirect rejects external malicious URLs."""
    response = client.post(
        "/auth/login?next=https://evil-phishing-site.com",
        data={"email": "admin@test.com", "password": "AdminSecurePassword123!"},
    )
    # Should ignore external domain and redirect to internal admin dashboard
    assert response.status_code == 302
    assert "evil-phishing-site.com" not in response.location
    assert "/admin" in response.location


def test_search_handles_special_characters_safely(client):
    """Test SQL query parameter safety with quotes and symbols."""
    response = client.get("/shop?q=%27%20OR%201=1--%20%22%3B")
    assert response.status_code == 200
    assert "Discover the collection" in response.data.decode("utf-8")
