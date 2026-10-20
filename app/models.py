from datetime import datetime, timezone
from decimal import Decimal
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


def utc_now():
    return datetime.now(timezone.utc)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Administrator, int(user_id))


class Administrator(UserMixin, db.Model):
    __tablename__ = "administrator"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Administrator {self.email}>"


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    products = db.relationship("Product", back_populates="category", lazy="dynamic")

    @property
    def active_products_count(self):
        return self.products.filter_by(is_active=True).count()

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    price = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)
    compare_at_price = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=True)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    category = db.relationship("Category", back_populates="products")

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0

    @property
    def is_low_stock(self) -> bool:
        return 0 < self.stock_quantity <= 5

    @property
    def stock_status(self) -> str:
        if self.stock_quantity <= 0:
            return "Out of Stock"
        elif self.stock_quantity <= 5:
            return f"Low Stock ({self.stock_quantity} remaining)"
        return "In Stock"

    @property
    def discount_percentage(self) -> int:
        if self.compare_at_price and self.compare_at_price > self.price:
            diff = self.compare_at_price - self.price
            return int(round((diff / self.compare_at_price) * Decimal(100)))
        return 0

    def __repr__(self):
        return f"<Product {self.name} (Stock: {self.stock_quantity})>"


class Order(db.Model):
    __tablename__ = "order"

    VALID_STATUSES = ["Pending", "Confirmed", "Processing", "Shipped", "Delivered", "Cancelled"]

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False, index=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default="Pending", nullable=False, index=True)
    subtotal = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)
    shipping_amount = db.Column(db.Numeric(10, 2, asdecimal=True), default=Decimal("0.00"), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)
    stock_restored = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)

    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined")

    @staticmethod
    def generate_order_number() -> str:
        date_str = utc_now().strftime("%Y%m%d")
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"APNA-{date_str}-{random_suffix}"

    @property
    def total_items_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def can_transition_to(self, new_status: str) -> bool:
        if new_status not in self.VALID_STATUSES:
            return False
        if self.status == "Delivered" and new_status != "Delivered":
            return False
        if self.status == "Cancelled" and new_status != "Cancelled":
            return False
        return True

    def __repr__(self):
        return f"<Order {self.order_number} ({self.status})>"


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete="SET NULL"), nullable=True)
    product_name_snapshot = db.Column(db.String(200), nullable=False)
    unit_price_snapshot = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    def __repr__(self):
        return f"<OrderItem {self.product_name_snapshot} x {self.quantity}>"


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscriber"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    def __repr__(self):
        return f"<NewsletterSubscriber {self.email}>"
