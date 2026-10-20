import os
from decimal import Decimal
from flask import Flask, render_template
from app.config import config_by_name
from app.extensions import db, login_manager, csrf
from app.cli import register_cli_commands
from app.cart.utils import get_cart_count
from app.models import Category


def format_inr(value):
    """Format decimal/float number into Indian Rupee representation (e.g., ₹1,499.00)."""
    if value is None:
        return "₹0.00"
    try:
        dec_val = Decimal(str(value))
        # Format with two decimal places
        s = f"{dec_val:,.2f}"
        return f"₹{s}"
    except Exception:
        return f"₹{value}"


def create_app(config_name=None):
    """Application factory for APNASTORE."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register custom template filters
    app.jinja_env.filters["format_inr"] = format_inr

    # Context processors for global layout data
    @app.context_processor
    def inject_global_data():
        try:
            active_categories = Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()
        except Exception:
            active_categories = []

        return {
            "cart_count": get_cart_count(),
            "nav_categories": active_categories,
            "store_name": app.config.get("STORE_NAME", "APNASTORE"),
            "store_tagline": app.config.get("STORE_TAGLINE", "Your Neighbourhood Store, Online."),
            "currency_symbol": app.config.get("CURRENCY_SYMBOL", "₹"),
            "free_shipping_threshold": app.config.get("FREE_SHIPPING_THRESHOLD", Decimal("999.00")),
            "shipping_flat_rate": app.config.get("SHIPPING_FLAT_RATE", Decimal("60.00")),
        }

    # Register Blueprints
    from app.storefront.routes import storefront_bp
    from app.cart.routes import cart_bp
    from app.checkout.routes import checkout_bp
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(storefront_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # Register CLI commands
    register_cli_commands(app)

    # Register Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
