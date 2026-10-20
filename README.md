# APNASTORE — Your Neighbourhood Store, Online

> **Prodigy Infotech Internship — Task 03: Full-Stack E-commerce Platform**  
> *A refined, production-grade local-store retail experience built with Python Flask, SQLAlchemy, Vanilla CSS design tokens, and Jinja2.*

---

## 1. Project Overview

**APNASTORE** ("Your Neighbourhood Store, Online") is a contemporary e-commerce platform designed for an Indian retail shop. It bridges the familiarity and warmth of a neighbourhood store with the convenience of an editorial digital shopping experience. 

Unlike generic e-commerce templates or mockups, APNASTORE is a complete, fully functional platform featuring:
- Server-authoritative shopping cart with real-time stock verification
- Decimal-accurate currency handling (Indian Rupee, `₹`)
- Atomic, transactional order placement with automated inventory reduction
- Historical order snapshot preservation
- Protected administrator dashboard with inventory metrics, product CRUD, and order status transitions
- Comprehensive automated test suite with 34 tests passing

---

## 2. Problem Statement & Objectives

### Problem
Independent local stores offer curated, high-quality artisanal goods, pantry staples, and textiles, but lack polished online storefronts. Most small retailers either rely on disjointed social media messaging or bloated marketplace platforms with high commission fees and fake discount gimmicks.

### Objectives
1. **Premium Brand Identity**: Deliver an art-directed editorial shopping aesthetic inspired by high-end retail (warm cream background, terracotta accents, typography blending `Playfair Display` and `Plus Jakarta Sans`).
2. **Transactional Integrity**: Ensure stock cannot be oversold, prices are never trusted from the client, and database transactions roll back atomically on any error.
3. **Frictionless Shopping**: Implement guest checkout with strict validation for Indian phone numbers (10 digits) and Postal PIN codes (6 digits).
4. **Comprehensive Store Operations**: Provide store staff with a secured administrative portal to monitor orders, restock low-inventory items, and manage fulfilment.

---

## 3. Technology Stack

| Layer | Technologies Used |
|---|---|
| **Backend Framework** | Python 3.14+, Flask 3.1.3 |
| **Database & ORM** | SQLite, Flask-SQLAlchemy 3.1.1 (SQLAlchemy 2.x) |
| **Authentication** | Flask-Login 0.6.3, Werkzeug Security (Scrypt password hashing) |
| **Form & CSRF** | Flask-WTF 1.3.0, WTForms 3.2.2, email-validator |
| **Frontend Styling** | Vanilla CSS3 Design System with CSS Custom Properties / Tokens |
| **Typography & Icons** | Playfair Display (Serif), Plus Jakarta Sans (Sans-serif), Lucide Icons |
| **Client Scripting** | Vanilla JavaScript (ES6+, Fetch API, Toast notifications, Quantity steppers) |
| **Automated Testing** | Pytest 9.1.1, Flask Test Client |

---

## 4. Key Features

### Storefront & Discovery
- **Editorial Hero Section**: Striking visual composition with curated product highlights and direct CTAs.
- **Department Navigation**: 6 initial product categories:
  1. *Electronics*
  2. *Fashion*
  3. *Home and Living*
  4. *Books and Stationery*
  5. *Accessories*
  6. *Daily Essentials*
- **Dedicated Shop Catalog**: Full-text case-insensitive product search, category filtering, numeric price range bounds (Min/Max ₹), deterministic sorting (Recommended, Price: Low-to-High, Price: High-to-Low, Name: A-Z, Newest), and server-side pagination.
- **Individual Product Pages**: High-resolution imagery, stock status badges (*In Stock*, *Low Stock: N left*, or *Out of Stock*), compare-at MRP discount calculator, quantity selector, and complementary product recommendations.

### Cart & Checkout
- **Session-Managed Cart**: Persists across browser visits without requiring prior registration.
- **Server Price Lookup**: Prices and totals are recalculated strictly on the server against the database.
- **Dynamic Shipping Threshold**: Clear rule: Flat ₹60.00 neighbourhood shipping fee, or **FREE** on orders ₹999.00 and above.
- **Indian Postal & Contact Validation**: Enforces valid 10-digit Indian mobile numbers and 6-digit PIN codes.
- **Atomic Order Placement**: Database transaction decrements inventory and persists immutable snapshots of item names and prices at the time of purchase.
- **Order Confirmation Receipt**: Clean receipt with unique order reference (`APNA-YYYYMMDD-XXXXXX`), customer information, ordered items, and print button.
- **Private Order Protection**: Confirmation view is session-isolated to prevent URL enumeration of other customers' orders.

### Administration Portal
- **Secure Authentication**: Flask-Login session management with brute-force counter tracking.
- **Dashboard Metrics**: Real-time counts of active products, total orders, pending fulfilment, low-stock items, and confirmed revenue.
- **Low Stock Radar**: Surfaces all products with $\le 5$ units remaining with quick restock actions.
- **Product CRUD**: Create, edit, and archive products with live image preview URLs and unique slug generation.
- **Order Fulfilment Workflow**: Status transitions (*Pending* $\rightarrow$ *Confirmed* $\rightarrow$ *Processing* $\rightarrow$ *Shipped* $\rightarrow$ *Delivered* $\rightarrow$ *Cancelled*).
- **Automated Stock Restoration**: Cancelling an order automatically restores inventory quantities back to the database.

---

## 5. Architecture & Database Design

```
+-------------------------------------------------------------+
|                     APNASTORE Architecture                  |
+-------------------------------------------------------------+
|                                                             |
|  [Storefront / Shop / Detail]  <--->  [Session Cart]        |
|             |                                |              |
|             v                                v              |
|    [Flask Blueprints]  ------>  [Checkout Validation]       |
|    (storefront, cart,                 |                     |
|     checkout, auth,                   v                     |
|     admin)                  [Database Transaction]          |
|                                |   - Lock Product Rows      |
|                                |   - Re-verify Stock        |
|                                |   - Recompute Unit Prices  |
|                                |   - Deduct Stock Quantity  |
|                                |   - Create Order & Items   |
|                                v                            |
|                     [SQLite Database (ORM)]                 |
|                     - Administrator                         |
|                     - Category                              |
|                     - Product                               |
|                     - Order                                 |
|                     - OrderItem (Snapshots)                 |
|                     - NewsletterSubscriber                  |
+-------------------------------------------------------------+
```

### Database Schema Highlights
- **`Administrator`**: `id`, `name`, `email` (unique index), `password_hash` (scrypt), `failed_login_attempts`, `last_login_at`, `created_at`.
- **`Category`**: `id`, `name` (unique), `slug` (unique index), `description`, `image_url`, `is_active`, `created_at`.
- **`Product`**: `id`, `name`, `slug` (unique index), `description`, `category_id` (foreign key), `price` (`Numeric(10, 2)`), `compare_at_price`, `stock_quantity`, `image_url`, `is_featured`, `is_active`, `created_at`, `updated_at`.
- **`Order`**: `id`, `order_number` (unique index), `customer_name`, `customer_email`, `customer_phone`, `address_line`, `city`, `state`, `postal_code`, `status`, `subtotal`, `shipping_amount`, `total_amount`, `stock_restored` (bool), `created_at`.
- **`OrderItem`**: `id`, `order_id` (foreign key cascade), `product_id` (foreign key nullable), `product_name_snapshot`, `unit_price_snapshot` (`Numeric(10, 2)`), `quantity`, `line_total`.
- **`NewsletterSubscriber`**: `id`, `email` (unique index), `created_at`.

---

## 6. Directory Structure

```
APNASTORE/
├── app/
│   ├── __init__.py              # Application factory & context processors
│   ├── config.py                # Development, Testing, Production configurations
│   ├── extensions.py            # SQLAlchemy, Flask-Login, CSRFProtect
│   ├── models.py                # Database models with Decimal currency & methods
│   ├── cli.py                   # CLI commands (init-db, seed-db, create-admin)
│   ├── auth/                    # Staff authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── storefront/              # Public catalog blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── cart/                    # Shopping cart blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── utils.py             # Server cart calculations & session logic
│   ├── checkout/                # Checkout & transactional order creation
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py             # Indian phone & PIN validation form
│   ├── admin/                   # Operations & inventory portal
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Global shell with nav, cart badge, footer
│   │   ├── storefront/          # home.html, catalog.html, product_detail.html, etc.
│   │   ├── cart/                # index.html
│   │   ├── checkout/            # index.html, confirmation.html
│   │   ├── auth/                # login.html
│   │   ├── admin/               # base.html, dashboard.html, products.html, orders.html, etc.
│   │   └── errors/              # 403.html, 404.html, 429.html, 500.html
│   └── static/
│       ├── css/
│       │   ├── tokens.css       # Design tokens & color variables
│       │   ├── base.css         # Reset, typography, layout containers
│       │   ├── components.css   # Buttons, cards, badges, steppers, pagination
│       │   ├── storefront.css   # Hero, grids, catalog sidebar, detail page
│       │   ├── cart-checkout.css# Cart table, order summary, confirmation receipt
│       │   └── admin.css        # Admin sidebar, metric cards, data tables
│       ├── js/
│       │   ├── app.js           # Toast alerts, mobile menu, CSRF fetch helpers
│       │   ├── cart.js          # Cart steppers and AJAX add-to-cart
│       │   └── checkout.js      # Form auto-sanitization & double-submit protection
│       └── images/
│           └── placeholder.svg  # Designed fallback vector graphic
├── tests/                       # Pytest automated test suite (34 tests)
│   ├── conftest.py
│   ├── test_storefront.py
│   ├── test_products.py
│   ├── test_cart.py
│   ├── test_checkout.py
│   ├── test_orders.py
│   ├── test_admin.py
│   └── test_security.py
├── instance/                    # SQLite database directory (git-ignored)
├── .env.example                 # Example environment variables
├── .gitignore                   # Comprehensive exclusions for git cleanliness
├── pytest.ini                   # Pytest path configuration
├── requirements.txt             # Pinned project dependencies
└── run.py                       # Local application entrypoint
```

---

## 7. Installation & Setup Instructions

### Prerequisites
- Python 3.10 or higher (Tested on Python 3.14 on macOS)
- `pip` package manager
- Terminal access

### Step 1: Clone or Navigate to Project
```bash
cd /path/to/APNASTORE
```

### Step 2: Create and Activate Virtual Environment
On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 5: Initialize Database & Seed Realistic Sample Catalog
```bash
flask --app run.py init-db
flask --app run.py seed-db
```
*`seed-db` seeds 6 categories and 22 curated Indian retail products with authentic pricing in INR (₹) and high-quality photography. It is safe to re-run repeatedly without duplicate entries.*

### Step 6: Create an Administrator Account
Create the default demo administrator:
```bash
flask --app run.py create-admin --name "Store Manager" --email "admin@apnastore.in" --password "Admin1234!"
```
*(Or run `flask --app run.py create-admin` without flags to enter credentials interactively with masked password prompt.)*

### Step 7: Start the Local Development Server
```bash
python3 run.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5050`**

---

## 8. Default Credentials for Evaluation

| Role | Email | Password | Access Link |
|---|---|---|---|
| **Store Customer** | *Guest Checkout (No registration required)* | — | `http://127.0.0.1:5050/shop` |
| **Administrator** | `admin@apnastore.in` | `Admin1234!` | `http://127.0.0.1:5050/auth/login` |

---

## 9. Automated Testing

The project includes an automated test suite covering all critical customer flows, inventory edge cases, security validations, and admin management:

Run the test suite:
```bash
pytest -v
```

### Actual Test Results
```text
============================= test session starts ==============================
platform darwin -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/harshyadav/Downloads/APNASTORE
configfile: pytest.ini
testpaths: tests
collected 34 items

tests/test_admin.py::test_admin_login_success PASSED                     [  2%]
tests/test_admin.py::test_admin_login_failure PASSED                     [  5%]
tests/test_admin.py::test_unauthorized_admin_access_redirects PASSED     [  8%]
tests/test_admin.py::test_admin_product_creation PASSED                  [ 11%]
tests/test_admin.py::test_admin_product_edit PASSED                      [ 14%]
tests/test_admin.py::test_admin_order_status_update_and_cancellation PASSED [ 17%]
tests/test_cart.py::test_empty_cart_view PASSED                          [ 20%]
tests/test_cart.py::test_add_product_to_cart PASSED                      [ 23%]
tests/test_cart.py::test_add_to_cart_ajax PASSED                         [ 26%]
tests/test_cart.py::test_reject_adding_out_of_stock_item PASSED          [ 29%]
tests/test_cart.py::test_reject_quantity_exceeding_stock PASSED          [ 32%]
tests/test_cart.py::test_update_cart_quantity_and_remove PASSED          [ 35%]
tests/test_cart.py::test_cart_shipping_calculation PASSED                [ 38%]
tests/test_checkout.py::test_empty_cart_cannot_checkout PASSED           [ 41%]
tests/test_checkout.py::test_checkout_form_validation PASSED             [ 44%]
tests/test_checkout.py::test_successful_order_placement PASSED           [ 47%]
tests/test_checkout.py::test_unauthorized_confirmation_access PASSED     [ 50%]
tests/test_orders.py::test_order_number_format PASSED                    [ 52%]
tests/test_orders.py::test_order_item_snapshot_preservation PASSED       [ 55%]
tests/test_products.py::test_inactive_product_hidden_from_storefront PASSED [ 58%]
tests/test_products.py::test_category_direct_route PASSED                [ 61%]
tests/test_products.py::test_categories_index_page PASSED                [ 64%]
tests/test_security.py::test_password_is_properly_hashed PASSED          [ 67%]
tests/test_security.py::test_safe_redirect_prevents_open_redirect PASSED [ 70%]
tests/test_security.py::test_search_handles_special_characters_safely PASSED [ 73%]
tests/test_storefront.py::test_home_page_loads PASSED                    [ 76%]
tests/test_storefront.py::test_catalog_loads PASSED                      [ 79%]
tests/test_storefront.py::test_product_detail_page PASSED                [ 82%]
tests/test_storefront.py::test_missing_product_returns_404 PASSED        [ 85%]
tests/test_storefront.py::test_search_filtering PASSED                   [ 88%]
tests/test_storefront.py::test_category_filtering PASSED                 [ 91%]
tests/test_storefront.py::test_price_range_filtering PASSED              [ 94%]
tests/test_storefront.py::test_sorting_functionality PASSED              [ 97%]
tests/test_storefront.py::test_newsletter_subscription PASSED            [100%]

======================== 34 passed in 3.10s ========================
```

---

## 10. Security & Hardening Features

- **CSRF Protection**: All state-altering POST requests (cart updates, order placement, logins, product modifications, and order status changes) require validated CSRF tokens.
- **Server-Side Price Recalculation**: Prices submitted by client browsers are never trusted. All totals, taxes, and shipping calculations occur strictly via server-side database lookups.
- **Atomic Stock Checks**: Product rows are checked within a database transaction during checkout. If stock is insufficient, the transaction rolls back cleanly without saving any partial records.
- **One-Way Password Hashing**: Passwords use Scrypt/PBKDF2 salted hashes through Werkzeug security primitives. Plaintext passwords are never stored or logged.
- **Session-Protected Order Receipts**: Order confirmation receipts verify that the visitor owns the session order token or is an authenticated administrator, preventing direct ID enumeration.
- **Anti-Brute Force Protection**: Failed administrator login attempts are tracked and rate-limited.
- **Open-Redirect Protection**: Login redirection validates the target host against the current local server before issuing redirects.

---

## 11. Known Limitations & Future Roadmap

### Known Limitations
- Payment processing is implemented in demonstration mode: orders are recorded in the database with inventory deductions, but real credit card / UPI payment gateways (e.g. Razorpay, Stripe) are simulated without real money charges.
- Local development uses SQLite for lightweight, zero-dependency installation; production environments would deploy PostgreSQL with migration tracking via Flask-Migrate.

### Future Roadmap
- Customer accounts with saved addresses and past order history.
- UPI QR code dynamic generation for Indian payments.
- Webhook integration for shipping carriers (Delhivery, Shiprocket).
- Automated email order receipts via SendGrid or AWS SES.

---

## 12. License & Acknowledgements

Created for the **Prodigy Infotech Internship — Task 03**  
Designed and built with passion as a demonstration of high-quality, full-stack product engineering.
