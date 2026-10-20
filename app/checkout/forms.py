import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

INDIAN_STATES = [
    ("", "Select State / Union Territory"),
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("West Bengal", "West Bengal"),
    ("Delhi", "Delhi (NCT)"),
    ("Jammu and Kashmir", "Jammu and Kashmir"),
    ("Ladakh", "Ladakh"),
    ("Chandigarh", "Chandigarh"),
]


class CheckoutForm(FlaskForm):
    customer_name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Please provide your full name."),
            Length(min=2, max=120, message="Full name must be between 2 and 120 characters."),
        ],
        render_kw={"placeholder": "Aarav Sharma", "autocomplete": "name"},
    )
    customer_email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email address is required for order confirmation."),
            Email(message="Please enter a valid email address."),
            Length(max=120),
        ],
        render_kw={"placeholder": "aarav.sharma@example.com", "autocomplete": "email"},
    )
    customer_phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(message="Phone number is required for delivery coordination."),
            Length(min=10, max=15, message="Please enter a valid phone number."),
        ],
        render_kw={"placeholder": "9876543210", "autocomplete": "tel"},
    )
    address_line = StringField(
        "Street Address & Landmark",
        validators=[
            DataRequired(message="Please provide your street address or apartment."),
            Length(min=5, max=255, message="Street address must be at least 5 characters."),
        ],
        render_kw={"placeholder": "Flat 402, Greenfield Apts, 12th Cross Road", "autocomplete": "street-address"},
    )
    city = StringField(
        "City / District",
        validators=[
            DataRequired(message="City name is required."),
            Length(min=2, max=100),
        ],
        render_kw={"placeholder": "Bengaluru", "autocomplete": "address-level2"},
    )
    state = SelectField(
        "State / Region",
        choices=INDIAN_STATES,
        validators=[DataRequired(message="Please select your state.")],
    )
    postal_code = StringField(
        "PIN Code (6 Digits)",
        validators=[
            DataRequired(message="PIN code is required."),
            Length(min=6, max=6, message="PIN code must be exactly 6 digits."),
        ],
        render_kw={"placeholder": "560001", "maxlength": "6", "autocomplete": "postal-code"},
    )
    submit = SubmitField("Place Demonstration Order")

    def validate_customer_phone(self, field):
        cleaned = re.sub(r"[\s\-\(\)]", "", field.data or "")
        # Allow Indian 10-digit mobile number with optional +91 or 0
        if not re.match(r"^(?:\+91|0)?[6-9]\d{9}$", cleaned):
            raise ValidationError("Please enter a valid 10-digit Indian mobile number (e.g., 9876543210).")

    def validate_postal_code(self, field):
        cleaned = (field.data or "").strip()
        if not re.match(r"^[1-9][0-9]{5}$", cleaned):
            raise ValidationError("Please enter a valid 6-digit Indian Postal PIN code (e.g., 560001).")
