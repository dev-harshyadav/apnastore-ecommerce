from decimal import Decimal
import re
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    IntegerField,
    BooleanField,
    SelectField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from app.models import Category, Product, Order


class ProductForm(FlaskForm):
    name = StringField(
        "Product Name",
        validators=[
            DataRequired(message="Product name is required."),
            Length(min=2, max=200, message="Name must be between 2 and 200 characters."),
        ],
        render_kw={"placeholder": "e.g. Aura Active Noise-Cancelling Earbuds"},
    )
    slug = StringField(
        "URL Slug (optional, auto-generated if left blank)",
        validators=[Optional(), Length(max=200)],
        render_kw={"placeholder": "e.g. aura-active-noise-cancelling-earbuds"},
    )
    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[DataRequired(message="Please select a product category.")],
    )
    price = DecimalField(
        "Selling Price (₹)",
        places=2,
        validators=[
            DataRequired(message="Price is required."),
            NumberRange(min=Decimal("0.01"), message="Price must be greater than zero."),
        ],
        render_kw={"placeholder": "1499.00", "step": "0.50"},
    )
    compare_at_price = DecimalField(
        "Comparison Price / MRP (₹, optional)",
        places=2,
        validators=[
            Optional(),
            NumberRange(min=Decimal("0.01"), message="MRP must be greater than zero."),
        ],
        render_kw={"placeholder": "1799.00", "step": "0.50"},
    )
    stock_quantity = IntegerField(
        "Stock Quantity",
        validators=[
            DataRequired(message="Stock quantity is required."),
            NumberRange(min=0, message="Stock quantity cannot be negative."),
        ],
        default=10,
        render_kw={"placeholder": "25", "min": "0"},
    )
    image_url = StringField(
        "Image URL",
        validators=[
            DataRequired(message="Product image URL is required."),
            Length(max=500),
        ],
        render_kw={"placeholder": "https://images.unsplash.com/... or /static/images/..."},
    )
    description = TextAreaField(
        "Product Description",
        validators=[
            DataRequired(message="Description is required."),
            Length(min=10, max=3000, message="Description must be between 10 and 3000 characters."),
        ],
        render_kw={"rows": 5, "placeholder": "Describe the product materials, dimensions, and unique qualities..."},
    )
    is_featured = BooleanField("Feature on Homepage Showcase")
    is_active = BooleanField("Active in Storefront Catalog", default=True)
    submit = SubmitField("Save Product")

    def __init__(self, *args, original_product_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_product_id = original_product_id
        # Populate category choices dynamically
        categories = Category.query.order_by(Category.name.asc()).all()
        self.category_id.choices = [(c.id, c.name) for c in categories]

    def validate_compare_at_price(self, field):
        if field.data and self.price.data and field.data <= self.price.data:
            raise ValidationError("Comparison MRP price must be strictly greater than selling price.")

    def validate_slug(self, field):
        if field.data:
            slug_cleaned = re.sub(r"[^a-z0-9\-]", "", field.data.strip().lower())
            query = Product.query.filter_by(slug=slug_cleaned)
            if self.original_product_id:
                query = query.filter(Product.id != self.original_product_id)
            if query.first():
                raise ValidationError("This slug is already used by another product. Choose a distinct slug.")


class CategoryForm(FlaskForm):
    name = StringField(
        "Category Name",
        validators=[
            DataRequired(message="Category name is required."),
            Length(min=2, max=100),
        ],
        render_kw={"placeholder": "e.g. Daily Essentials"},
    )
    slug = StringField(
        "URL Slug (optional, auto-generated if left blank)",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g. daily-essentials"},
    )
    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 3, "placeholder": "Short summary of products in this category..."},
    )
    image_url = StringField(
        "Cover Image URL",
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "https://images.unsplash.com/..."},
    )
    is_active = BooleanField("Active in Store Navigation", default=True)
    submit = SubmitField("Save Category")

    def __init__(self, *args, original_category_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_category_id = original_category_id

    def validate_name(self, field):
        query = Category.query.filter(Category.name.ilike(field.data.strip()))
        if self.original_category_id:
            query = query.filter(Category.id != self.original_category_id)
        if query.first():
            raise ValidationError("A category with this name already exists.")


class OrderStatusForm(FlaskForm):
    status = SelectField(
        "Update Order Status",
        choices=[(s, s) for s in Order.VALID_STATUSES],
        validators=[DataRequired()],
    )
    submit = SubmitField("Update Status")
