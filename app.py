import json
import logging
import os
import re
import sqlite3
from datetime import datetime
from functools import wraps

# Load .env file BEFORE any os.environ.get() calls
from dotenv import load_dotenv
load_dotenv()

from flask import (Flask, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import email_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("ELORA_SECRET_KEY", "elora-dev-secret-change-in-prod-2026")

# ---------------------------------------------------------------------------
# Database helpers & initial schema
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "elora.db")


def get_db():
    """Return a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Initial product catalogue (source of truth & seed data)
DEFAULT_PRODUCTS = [
    {
        "id": "noir",
        "name": "ELORA NOIR",
        "price": 185.0,
        "image": "/static/images/elora-noir.png",
        "category": "Eau de Parfum",
        "scent_family": "Woody & Amber",
        "tagline": "Dark, smoky, and unforgettable — a fragrance that commands any room.",
        "description": "ELORA NOIR is an intimate study in shadow and depth. Opening with a burst of smoked black amber and pink peppercorn, it settles into an aristocratic heart of cedarwood before yielding to a warm, intoxicating trail of bourbon vanilla. Rich. Authoritative. Enduring.",
        "top_notes": "Smoked Black Amber, Pink Peppercorn, Cardamom",
        "heart_notes": "Atlas Cedarwood, Orris Root, Rare Clove",
        "base_notes": "Bourbon Vanilla, Smoky Tonka, Dark Indonesian Patchouli",
        "notes_list": "Black Amber · Cedar · Vanilla",
        "volume": "100 ml / 3.4 fl oz",
        "stock": 42,
        "featured": 1,
        "rating": 4.95,
        "reviews_count": 142
    },
    {
        "id": "eclat",
        "name": "ELORA ÉCLAT",
        "price": 165.0,
        "image": "/static/images/elora-eclat.png",
        "category": "Eau de Parfum",
        "scent_family": "Floral & Fresh",
        "tagline": "Radiant and luminous — the scent of golden afternoons in Grasse.",
        "description": "ELORA ÉCLAT radiates with the brilliance of sun-drenched Italian bergamot, crisp and effervescent. A heart of dewy Grasse jasmine adds sublime elegance before a base of white musk anchors the fragrance in silky intimacy. Light that lingers forever.",
        "top_notes": "Italian Bergamot, Mandarin Leaf, White Crisp Pear",
        "heart_notes": "Grasse Jasmine Absolute, Orange Blossom, Dewy Freesia",
        "base_notes": "Silky White Musk, Golden Cedar, Rare Ambergris",
        "notes_list": "Bergamot · Jasmine · Musk",
        "volume": "100 ml / 3.4 fl oz",
        "stock": 38,
        "featured": 1,
        "rating": 4.88,
        "reviews_count": 119
    },
    {
        "id": "velvet",
        "name": "ELORA VELVET",
        "price": 195.0,
        "image": "/static/images/elora-velvet.png",
        "category": "Eau de Parfum",
        "scent_family": "Oriental & Spiced",
        "tagline": "Opulent, warm, and deeply sensual — draped in the finest petals.",
        "description": "ELORA VELVET is pure olfactory opulence. An intoxicating saffron-rose accord blooms at the opening, spiced and lush, before melting into a velvet bed of creamy Mysore sandalwood. Deeply sensual. Timelessly romantic. An embrace you never want to leave.",
        "top_notes": "Persian Saffron, Pink Pepper, Blackcurrant Cassis",
        "heart_notes": "Bulgarian Rose Absolute, Red Peony, Royal Cinnamon Bark",
        "base_notes": "Creamy Mysore Sandalwood, Cashmeran, Golden Honey",
        "notes_list": "Rose · Saffron · Sandalwood",
        "volume": "100 ml / 3.4 fl oz",
        "stock": 29,
        "featured": 1,
        "rating": 4.92,
        "reviews_count": 156
    },
    {
        "id": "oud",
        "name": "ELORA OUD",
        "price": 245.0,
        "image": "/static/images/elora-oud.png",
        "category": "Eau de Parfum",
        "scent_family": "Deep Oud & Leather",
        "tagline": "Ancient, rare, and commanding — a fragrance reserved for the bold.",
        "description": "ELORA OUD is our most coveted creation. Wild Cambodian oud, hand-aged for over a decade, opens with a complexity that cannot be rushed. A leather accord of rare restraint follows, grounded in a resinous, golden amber. Unapologetic power distilled.",
        "top_notes": "Smoked Bergamot, Wild Incense, Elemi Resin",
        "heart_notes": "Wild Cambodian Oud, Florentine Leather, Black Rose",
        "base_notes": "Resinous Golden Amber, Royal Birch, Bourbon Vetiver",
        "notes_list": "Oud · Leather · Amber",
        "volume": "100 ml / 3.4 fl oz",
        "stock": 18,
        "featured": 1,
        "rating": 4.98,
        "reviews_count": 204
    },
    {
        "id": "solaris",
        "name": "ELORA SOLARIS ROYALE",
        "price": 225.0,
        "image": "/static/images/elora-solaris.png",
        "category": "Extrait de Parfum",
        "scent_family": "Solar & Amber",
        "tagline": "Golden heat on sun-warmed skin — liquid sunlight caught in heavy crystal.",
        "description": "ELORA SOLARIS ROYALE captures the intoxicating warmth of the Mediterranean sunset. Solar amber and neroli glow over rare royal tuberose, benzoin, and Tahitian coconut nectar.",
        "top_notes": "Solar Amber, Neroli, Calabrian Bergamot",
        "heart_notes": "Royal Tuberose, Jasmine Sambac, Ylang Ylang",
        "base_notes": "Warm Golden Amber, Benzoin Resin, Sun-bleached Driftwood",
        "notes_list": "Solar Amber · Neroli · Royal Tuberose",
        "volume": "100 ml / 3.4 fl oz",
        "stock": 35,
        "featured": 1,
        "rating": 4.95,
        "reviews_count": 88
    }
]

DEFAULT_REVIEWS = [
    {
        "product_id": "noir",
        "user_name": "Alexander Vance",
        "rating": 5,
        "comment": "Unbelievable depth. The transition from smoky amber to bourbon vanilla is sheer perfection. Lasts well over 14 hours on fabric.",
        "created_at": "2026-10-18 14:22:00"
    },
    {
        "product_id": "noir",
        "user_name": "Eleanor Sinclair",
        "rating": 5,
        "comment": "My signature evening scent. It draws compliments everywhere without ever being overpowering.",
        "created_at": "2026-10-29 09:40:00"
    },
    {
        "product_id": "eclat",
        "user_name": "Sophia Laurent",
        "rating": 5,
        "comment": "Crisp, radiant, and luminous. It feels like golden sunshine in an Italian orchard. Fresh yet wonderfully persistent.",
        "created_at": "2026-11-02 11:15:00"
    },
    {
        "product_id": "velvet",
        "user_name": "Camille Dupond",
        "rating": 5,
        "comment": "The Bulgarian rose and saffron accord is mesmerizing. Rich, velvety, and romantic beyond words.",
        "created_at": "2026-11-05 16:30:00"
    },
    {
        "product_id": "oud",
        "user_name": "Henri de Montmirail",
        "rating": 5,
        "comment": "Magnificent Cambodian oud with Florentine leather. Dark, regal, and exceptionally refined. Worth every single cent.",
        "created_at": "2026-11-08 18:05:00"
    }
]


def init_db():
    """Create all tables and perform safe schema migrations if upgrading."""
    with get_db() as conn:
        # 1. Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                is_admin      INTEGER DEFAULT 0,
                phone         TEXT    DEFAULT '',
                address       TEXT    DEFAULT '',
                city          TEXT    DEFAULT '',
                state         TEXT    DEFAULT '',
                pincode       TEXT    DEFAULT '',
                created_at    TEXT    DEFAULT ''
            )
        """)

        # Check existing columns in users
        user_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "is_admin" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        if "phone" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''")
        if "address" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN address TEXT DEFAULT ''")
        if "city" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN city TEXT DEFAULT ''")
        if "state" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN state TEXT DEFAULT ''")
        if "pincode" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN pincode TEXT DEFAULT ''")
        if "created_at" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT ''")

        # 2. Products table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id            TEXT PRIMARY KEY,
                name          TEXT NOT NULL,
                price         REAL NOT NULL,
                image         TEXT NOT NULL,
                category      TEXT NOT NULL,
                scent_family  TEXT NOT NULL,
                tagline       TEXT,
                description   TEXT,
                top_notes     TEXT,
                heart_notes   TEXT,
                base_notes    TEXT,
                notes_list    TEXT,
                volume        TEXT DEFAULT '100 ml / 3.4 fl oz',
                stock         INTEGER DEFAULT 50,
                featured      INTEGER DEFAULT 1,
                rating        REAL DEFAULT 4.9,
                reviews_count INTEGER DEFAULT 120
            )
        """)

        # 3. Orders table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                order_number   TEXT    NOT NULL UNIQUE,
                status         TEXT    NOT NULL DEFAULT 'confirmed',
                total          REAL    NOT NULL,
                full_name      TEXT    NOT NULL,
                email          TEXT    NOT NULL,
                phone          TEXT    NOT NULL,
                address        TEXT    NOT NULL,
                city           TEXT    NOT NULL,
                state          TEXT    NOT NULL,
                pincode        TEXT    NOT NULL,
                created_at     TEXT    NOT NULL,
                discount       REAL    DEFAULT 0.0,
                payment_method TEXT    DEFAULT 'Cash on Delivery',
                gift_wrap      INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        order_cols = [r[1] for r in conn.execute("PRAGMA table_info(orders)").fetchall()]
        if "discount" not in order_cols:
            conn.execute("ALTER TABLE orders ADD COLUMN discount REAL DEFAULT 0.0")
        if "payment_method" not in order_cols:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT 'Cash on Delivery'")
        if "gift_wrap" not in order_cols:
            conn.execute("ALTER TABLE orders ADD COLUMN gift_wrap INTEGER DEFAULT 0")

        # 4. Order items table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id     INTEGER NOT NULL,
                product_id   TEXT    NOT NULL,
                product_name TEXT    NOT NULL,
                unit_price   REAL    NOT NULL,
                quantity     INTEGER NOT NULL,
                subtotal     REAL    NOT NULL,
                image        TEXT    DEFAULT '',
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)
        order_item_cols = [r[1] for r in conn.execute("PRAGMA table_info(order_items)").fetchall()]
        if "image" not in order_item_cols:
            conn.execute("ALTER TABLE order_items ADD COLUMN image TEXT DEFAULT ''")

        # 5. Reviews table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT    NOT NULL,
                user_name  TEXT    NOT NULL,
                rating     INTEGER NOT NULL,
                comment    TEXT    NOT NULL,
                created_at TEXT    NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # 6. Seed products if empty
        prod_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if prod_count == 0:
            for p in DEFAULT_PRODUCTS:
                conn.execute("""
                    INSERT INTO products (
                        id, name, price, image, category, scent_family,
                        tagline, description, top_notes, heart_notes,
                        base_notes, notes_list, volume, stock, featured, rating, reviews_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p["id"], p["name"], p["price"], p["image"], p["category"], p["scent_family"],
                    p["tagline"], p["description"], p["top_notes"], p["heart_notes"],
                    p["base_notes"], p["notes_list"], p["volume"], p["stock"], p["featured"],
                    p["rating"], p["reviews_count"]
                ))
            logging.info("Seeded %d default products into database.", len(DEFAULT_PRODUCTS))

        # 7. Seed sample reviews if empty
        rev_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        if rev_count == 0:
            for r in DEFAULT_REVIEWS:
                conn.execute("""
                    INSERT INTO reviews (product_id, user_name, rating, comment, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (r["product_id"], r["user_name"], r["rating"], r["comment"], r["created_at"]))
            logging.info("Seeded %d sample reviews into database.", len(DEFAULT_REVIEWS))

        # 8. Ensure user 1 or admin email has admin privileges
        conn.execute("UPDATE users SET is_admin = 1 WHERE id = 1 OR email = 'admin@eloraparfum.com'")

        conn.commit()


# Initialise the database on startup
init_db()


# ---------------------------------------------------------------------------
# Dynamic Product Repository (Synchronized with SQLite)
# ---------------------------------------------------------------------------
def get_all_products(featured_only=False, category=None):
    """Retrieve products from the database as list of dicts."""
    with get_db() as conn:
        query = "SELECT * FROM products"
        params = []
        conditions = []
        if featured_only:
            conditions.append("featured = 1")
        if category and category.lower() != "all":
            conditions.append("LOWER(scent_family) = LOWER(?) OR LOWER(category) = LOWER(?)")
            params.extend([category, category])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY featured DESC, price DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_product(product_id: str):
    """Retrieve a single product by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row) if row else None


def get_products_dict():
    """Return dictionary of products keyed by ID (backwards compatibility)."""
    prods = get_all_products()
    return {p["id"]: p for p in prods}


# Static-compatible fallback reference
PRODUCTS = get_products_dict()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    digits = re.sub(r"\D", "", phone.strip())
    return 7 <= len(digits) <= 15


def is_valid_pincode(pincode: str) -> bool:
    if not pincode:
        return False
    clean = re.sub(r"\s", "", pincode.strip())
    return 3 <= len(clean) <= 12 and bool(re.match(r"^[A-Za-z0-9\-]+$", clean))

VALID_COUPONS = {
    "ELORA10": {"discount_percent": 10, "label": "10% VIP Atelier Discount"},
    "LUXURY20": {"discount_percent": 20, "label": "20% Exclusive Member Privilege"},
    "SIGNATURE": {"discount_fixed": 30, "label": "$30 Signature Gift Credit"},
}


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip())) if email else False


def generate_order_number() -> str:
    """Return a unique order number like ELORA-20261114-00042-1234."""
    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    micro_suffix = str(now.microsecond)[:4].zfill(4)
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    return f"ELORA-{date_part}-{count + 1:05d}-{micro_suffix}"


# ---------------------------------------------------------------------------
# Authentication & Authorization decorators
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            flash("Please log in to continue your luxury experience.", "error")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get("user")
        if not user:
            flash("Administrator authentication required.", "error")
            return redirect(url_for("login", next=request.path))
        if not user.get("is_admin"):
            flash("Access restricted to ELORA Atelier Administrators.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Context Processors
# ---------------------------------------------------------------------------
@app.context_processor
def inject_global_data():
    """Make current_user and basic catalog metadata available to all templates."""
    user = session.get("user")
    cart_items_count = 0
    return {
        "current_user": user,
        "is_admin": bool(user and user.get("is_admin")),
        "now_year": datetime.now().year
    }


# ---------------------------------------------------------------------------
# Routes — Main Landing & Products
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    products = get_all_products()
    products_json = json.dumps(
        {p["id"]: {
            "name": p["name"],
            "image": p["image"],
            "price": p["price"],
            "category": p["category"],
            "scent_family": p["scent_family"],
            "tagline": p["tagline"],
            "description": p["description"],
            "notes": [n.strip() for n in p["notes_list"].split("·")] if "·" in p["notes_list"] else [p["notes_list"]],
            "volume": p["volume"],
            "rating": p["rating"]
        } for p in products}
    )
    return render_template(
        "index.html",
        products=products,
        products_json=products_json,
        current_user=session.get("user")
    )


@app.route("/product/<product_id>")
def product_detail(product_id):
    """Dedicated luxury product detail page."""
    product = get_product(product_id)
    if not product:
        flash("The requested fragrance could not be found.", "error")
        return redirect(url_for("index") + "#collection")

    with get_db() as conn:
        reviews = conn.execute(
            "SELECT * FROM reviews WHERE product_id = ? ORDER BY created_at DESC",
            (product_id,)
        ).fetchall()

    related_products = [
        p for p in get_all_products() if p["id"] != product_id
    ][:3]

    return render_template(
        "product_detail.html",
        product=product,
        reviews=reviews,
        related_products=related_products,
        current_user=session.get("user")
    )


@app.route("/product/<product_id>/review", methods=["POST"])
def add_review(product_id):
    """Submit a customer review for a perfume."""
    product = get_product(product_id)
    if not product:
        flash("Fragrance not found.", "error")
        return redirect(url_for("index"))

    user_name = request.form.get("user_name", "").strip()
    comment = request.form.get("comment", "").strip()
    try:
        rating = int(request.form.get("rating", 5))
        rating = max(1, min(5, rating))
    except ValueError:
        rating = 5

    if not user_name or not comment:
        flash("Please provide both your name and review impressions.", "error")
        return redirect(url_for("product_detail", product_id=product_id))

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO reviews (product_id, user_name, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
            (product_id, user_name, rating, comment, created_at)
        )
        # Update product aggregate rating
        cur = conn.execute(
            "SELECT AVG(rating), COUNT(id) FROM reviews WHERE product_id = ?",
            (product_id,)
        )
        avg_r, count_r = cur.fetchone()
        new_rating = round(avg_r, 2) if avg_r else 5.0
        conn.execute(
            "UPDATE products SET rating = ?, reviews_count = ? WHERE id = ?",
            (new_rating, count_r, product_id)
        )
        conn.commit()

    flash("Thank you for sharing your olfactory impressions with the ELORA Atelier.", "success")
    return redirect(url_for("product_detail", product_id=product_id))


@app.route("/api/products")
def api_products():
    """JSON API for searching and filtering fragrances."""
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip().lower()
    products = get_all_products()

    filtered = []
    for p in products:
        match_q = (
            not query or
            query in p["name"].lower() or
            query in p["scent_family"].lower() or
            query in p["notes_list"].lower() or
            query in p["description"].lower()
        )
        match_cat = (
            not category or
            category == "all" or
            category == p["scent_family"].lower() or
            category in p["category"].lower()
        )
        if match_q and match_cat:
            filtered.append(p)

    return jsonify({"count": len(filtered), "products": filtered})


# ---------------------------------------------------------------------------
# Routes — Cart & Checkout
# ---------------------------------------------------------------------------
@app.route("/cart")
def cart():
    products = get_products_dict()
    products_json = json.dumps(
        {k: {"name": v["name"], "image": v["image"], "price": v["price"], "category": v["category"], "stock": v["stock"]}
         for k, v in products.items()}
    )
    return render_template(
        "cart.html",
        current_user=session.get("user"),
        products_json=products_json
    )


@app.route("/api/validate-coupon", methods=["POST"])
def validate_coupon():
    """Validate a VIP promo code and return calculated discount details."""
    data = request.get_json(silent=True) or {}
    code = data.get("coupon", "").strip().upper()
    subtotal = float(data.get("subtotal", 0))

    if not code:
        return jsonify({"valid": False, "message": "Please enter a coupon code."})

    coupon = VALID_COUPONS.get(code)
    if not coupon:
        return jsonify({"valid": False, "message": "Invalid privilege code. Try 'ELORA10' or 'LUXURY20'."})

    discount = 0.0
    if "discount_percent" in coupon:
        discount = round(subtotal * (coupon["discount_percent"] / 100.0), 2)
    elif "discount_fixed" in coupon:
        discount = min(float(coupon["discount_fixed"]), subtotal)

    return jsonify({
        "valid": True,
        "coupon": code,
        "label": coupon["label"],
        "discount": discount,
        "new_total": max(0.0, round(subtotal - discount, 2)),
        "message": f"Privilege applied: {coupon['label']}"
    })


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    user = session["user"]
    products_dict = get_products_dict()

    # Retrieve stored user profile for default checkout info
    with get_db() as conn:
        profile_row = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
        profile = dict(profile_row) if profile_row else {}

    if request.method == "POST":
        # Form field reading & sanitisation
        full_name = request.form.get("full_name", "").strip() or profile.get("name", "")
        email = request.form.get("email", "").strip().lower() or profile.get("email", "")
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        cart_json = request.form.get("cart_data", "")
        payment_method = request.form.get("payment_method", "Cash on Delivery").strip()
        coupon_code = request.form.get("coupon_code", "").strip().upper()
        gift_wrap = 1 if request.form.get("gift_wrap") in ["on", "1", "true"] else 0
        save_info = request.form.get("save_info") in ["on", "1", "true"]

        errors = []
        if not full_name:
            errors.append("Full name is required for delivery.")
        if not is_valid_email(email):
            errors.append("A valid contact email is required.")
        if not is_valid_phone(phone):
            errors.append("A valid contact telephone number is required (7–15 digits).")
        if not address:
            errors.append("Delivery street address is required.")
        if not city:
            errors.append("City is required.")
        if not state:
            errors.append("State / Province is required.")
        if not is_valid_pincode(pincode):
            errors.append("A valid postal / ZIP code is required.")

        # Parse cart data
        cart_items = []
        try:
            raw = json.loads(cart_json) if cart_json else []
            for item in raw:
                pid = item.get("id", "")
                qty = int(item.get("qty", 0))
                if pid in products_dict and qty > 0:
                    cart_items.append({"id": pid, "qty": qty})
        except (json.JSONDecodeError, ValueError):
            errors.append("Cart data could not be validated. Please return to your bag.")

        if not cart_items:
            errors.append("Your bag is currently empty. Please select a fragrance before completing checkout.")

        if errors:
            for e in errors:
                flash(e, "error")
            products_json = json.dumps(
                {k: {"name": v["name"], "image": v["image"], "price": v["price"], "category": v["category"]}
                 for k, v in products_dict.items()}
            )
            return render_template(
                "checkout.html",
                current_user=user,
                form=request.form,
                products_json=products_json,
                profile=profile
            )

        # Server-side subtotal & coupon discount calculation (never trust client total)
        subtotal = sum(products_dict[i["id"]]["price"] * i["qty"] for i in cart_items)
        discount = 0.0
        if coupon_code in VALID_COUPONS:
            c = VALID_COUPONS[coupon_code]
            if "discount_percent" in c:
                discount = round(subtotal * (c["discount_percent"] / 100.0), 2)
            elif "discount_fixed" in c:
                discount = min(float(c["discount_fixed"]), subtotal)

        total = max(0.0, round(subtotal - discount, 2))

        # Save address to profile if checked or profile fields empty
        if save_info or not profile.get("phone"):
            with get_db() as conn:
                conn.execute(
                    """UPDATE users SET phone = ?, address = ?, city = ?, state = ?, pincode = ?
                       WHERE id = ?""",
                    (phone, address, city, state, pincode, user["id"])
                )
                conn.commit()

        # Persist order
        order_number = generate_order_number()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with get_db() as conn:
            cur = conn.execute(
                """INSERT INTO orders
                   (user_id, order_number, status, total, full_name, email, phone,
                    address, city, state, pincode, created_at, discount, payment_method, gift_wrap)
                   VALUES (?, ?, 'confirmed', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user["id"], order_number, total, full_name, email, phone,
                 address, city, state, pincode, created_at, discount, payment_method, gift_wrap)
            )
            order_id = cur.lastrowid

            for item in cart_items:
                p = products_dict[item["id"]]
                unit_price = p["price"]
                item_subtotal = unit_price * item["qty"]
                conn.execute(
                    """INSERT INTO order_items
                       (order_id, product_id, product_name, unit_price, quantity, subtotal, image)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (order_id, item["id"], p["name"], unit_price, item["qty"], item_subtotal, p["image"])
                )
                # Decrement stock safely
                conn.execute(
                    "UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?",
                    (item["qty"], item["id"])
                )
            conn.commit()

        # Dispatch confirmation email (non-blocking)
        order_data = {
            "order_number": order_number,
            "created_at": created_at,
            "status": "confirmed",
            "total": total,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "payment_method": payment_method,
            "gift_wrap": gift_wrap
        }
        email_items = [
            {
                "product_name": products_dict[i["id"]]["name"],
                "unit_price": products_dict[i["id"]]["price"],
                "quantity": i["qty"],
                "subtotal": products_dict[i["id"]]["price"] * i["qty"],
            }
            for i in cart_items
        ]
        try:
            sent = email_service.send_order_confirmation(order_data, email_items)
            if sent:
                logging.info("Confirmation email dispatched for order %s", order_number)
        except Exception as exc:
            logging.error("Email dispatch failed for order %s: %s", order_number, exc)

        flash(f"Order {order_number} confirmed with distinction. Welcome to the ELORA family.", "success")
        return redirect(url_for("order_confirmation", order_number=order_number))

    # GET request
    form_defaults = {
        "full_name": profile.get("name", user.get("name", "")),
        "email": profile.get("email", user.get("email", "")),
        "phone": profile.get("phone", ""),
        "address": profile.get("address", ""),
        "city": profile.get("city", ""),
        "state": profile.get("state", ""),
        "pincode": profile.get("pincode", "")
    }
    products_json = json.dumps(
        {k: {"name": v["name"], "image": v["image"], "price": v["price"], "category": v["category"]}
         for k, v in products_dict.items()}
    )
    return render_template(
        "checkout.html",
        current_user=user,
        form=form_defaults,
        products_json=products_json,
        profile=profile
    )


@app.route("/order/<order_number>")
@login_required
def order_confirmation(order_number):
    user = session["user"]
    with get_db() as conn:
        order = conn.execute(
            "SELECT * FROM orders WHERE order_number = ? AND (user_id = ? OR ? = 1)",
            (order_number, user["id"], 1 if user.get("is_admin") else 0)
        ).fetchone()

        if not order:
            flash("Order not found or access restricted.", "error")
            return redirect(url_for("my_orders"))

        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?",
            (order["id"],)
        ).fetchall()

    return render_template(
        "order_confirmation.html",
        current_user=user,
        order=order,
        items=items,
    )


@app.route("/orders")
@login_required
def my_orders():
    user = session["user"]
    with get_db() as conn:
        orders = conn.execute(
            """SELECT o.*, COUNT(oi.id) as item_count
               FROM orders o
               LEFT JOIN order_items oi ON oi.order_id = o.id
               WHERE o.user_id = ?
               GROUP BY o.id
               ORDER BY o.created_at DESC""",
            (user["id"],)
        ).fetchall()
    return render_template("my_orders.html", current_user=user, orders=orders)


# ---------------------------------------------------------------------------
# Routes — User Profile & Account Settings
# ---------------------------------------------------------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = session["user"]

    if request.method == "POST":
        action = request.form.get("action", "update_info")

        if action == "update_info":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            city = request.form.get("city", "").strip()
            state = request.form.get("state", "").strip()
            pincode = request.form.get("pincode", "").strip()

            if not name:
                flash("Your name is required.", "error")
            else:
                with get_db() as conn:
                    conn.execute("""
                        UPDATE users
                        SET name = ?, phone = ?, address = ?, city = ?, state = ?, pincode = ?
                        WHERE id = ?
                    """, (name, phone, address, city, state, pincode, user["id"]))
                    conn.commit()
                # Update session name
                session["user"]["name"] = name
                session.modified = True
                flash("Your profile and delivery details have been updated.", "success")
                return redirect(url_for("profile"))

        elif action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            with get_db() as conn:
                user_row = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user["id"],)).fetchone()

            if not check_password_hash(user_row["password_hash"], current_pw):
                flash("Current password was incorrect.", "error")
            elif len(new_pw) < 8:
                flash("New password must be at least 8 characters long.", "error")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "error")
            else:
                new_hash = generate_password_hash(new_pw)
                with get_db() as conn:
                    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user["id"]))
                    conn.commit()
                flash("Your password has been securely updated.", "success")
                return redirect(url_for("profile"))

    with get_db() as conn:
        profile_row = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
        order_stats = conn.execute("""
            SELECT COUNT(id) as total_orders, COALESCE(SUM(total), 0) as total_spent
            FROM orders WHERE user_id = ?
        """, (user["id"],)).fetchone()

    return render_template(
        "profile.html",
        current_user=user,
        profile=profile_row,
        total_orders=order_stats["total_orders"],
        total_spent=round(order_stats["total_spent"], 2)
    )


# ---------------------------------------------------------------------------
# Routes — Admin Dashboard & Catalog Management
# ---------------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    with get_db() as conn:
        total_revenue = conn.execute("SELECT COALESCE(SUM(total), 0) FROM orders").fetchone()[0]
        total_orders = conn.execute("SELECT COUNT(id) FROM orders").fetchone()[0]
        total_products = conn.execute("SELECT COUNT(id) FROM products").fetchone()[0]
        total_users = conn.execute("SELECT COUNT(id) FROM users").fetchone()[0]

        recent_orders = conn.execute("""
            SELECT o.*, u.name as customer_name
            FROM orders o
            LEFT JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC
            LIMIT 15
        """).fetchall()

        all_products = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()

    return render_template(
        "admin.html",
        total_revenue=round(total_revenue, 2),
        total_orders=total_orders,
        total_products=total_products,
        total_users=total_users,
        recent_orders=recent_orders,
        products=all_products,
        current_user=session.get("user")
    )


@app.route("/admin/orders/status/<int:order_id>", methods=["POST"])
@admin_required
def admin_update_order_status(order_id):
    new_status = request.form.get("status", "confirmed").strip().lower()
    allowed_statuses = ["confirmed", "processing", "dispatched", "delivered", "cancelled"]
    if new_status in allowed_statuses:
        with get_db() as conn:
            conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
            conn.commit()
        flash(f"Order #{order_id} status updated to {new_status.capitalize()}.", "success")
    else:
        flash("Invalid status specified.", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/products/add", methods=["POST"])
@admin_required
def admin_add_product():
    pid = request.form.get("id", "").strip().lower()
    name = request.form.get("name", "").strip()
    try:
        price = float(request.form.get("price", 0))
    except ValueError:
        price = 150.0

    category = request.form.get("category", "Eau de Parfum").strip()
    scent_family = request.form.get("scent_family", "Woody & Amber").strip()
    image = request.form.get("image", "").strip() or "/static/images/elora-hero.png"
    tagline = request.form.get("tagline", "").strip()
    description = request.form.get("description", "").strip()
    top_notes = request.form.get("top_notes", "").strip()
    heart_notes = request.form.get("heart_notes", "").strip()
    base_notes = request.form.get("base_notes", "").strip()
    notes_list = request.form.get("notes_list", "").strip() or top_notes
    stock = int(request.form.get("stock", 50))
    featured = 1 if request.form.get("featured") else 0

    if not pid or not name or price <= 0:
        flash("Product ID, Name, and a valid positive price are required.", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM products WHERE id = ?", (pid,)).fetchone()
        if existing:
            flash(f"Product ID '{pid}' already exists in catalog.", "error")
            return redirect(url_for("admin_dashboard"))

        conn.execute("""
            INSERT INTO products (
                id, name, price, image, category, scent_family, tagline, description,
                top_notes, heart_notes, base_notes, notes_list, volume, stock, featured
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '100 ml / 3.4 fl oz', ?, ?)
        """, (pid, name, price, image, category, scent_family, tagline, description,
              top_notes, heart_notes, base_notes, notes_list, stock, featured))
        conn.commit()

    flash(f"Fragrance '{name}' added to the ELORA catalog successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/products/edit/<product_id>", methods=["POST"])
@admin_required
def admin_edit_product(product_id):
    name = request.form.get("name", "").strip()
    try:
        price = float(request.form.get("price", 0))
    except ValueError:
        price = 0
    category = request.form.get("category", "").strip()
    scent_family = request.form.get("scent_family", "").strip()
    tagline = request.form.get("tagline", "").strip()
    description = request.form.get("description", "").strip()
    notes_list = request.form.get("notes_list", "").strip()
    stock = int(request.form.get("stock", 50))
    featured = 1 if request.form.get("featured") else 0

    if not name or price <= 0:
        flash("Valid name and price required.", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db() as conn:
        conn.execute("""
            UPDATE products
            SET name = ?, price = ?, category = ?, scent_family = ?, tagline = ?,
                description = ?, notes_list = ?, stock = ?, featured = ?
            WHERE id = ?
        """, (name, price, category, scent_family, tagline, description, notes_list, stock, featured, product_id))
        conn.commit()

    flash(f"Fragrance '{name}' updated successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/products/delete/<product_id>", methods=["POST"])
@admin_required
def admin_delete_product(product_id):
    with get_db() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    flash(f"Fragrance '{product_id}' archived from catalog.", "success")
    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------------------------
# Routes — Authentication
# ---------------------------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user"):
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = []
        if not name:
            errors.append("Full name is required.")
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("signup.html", current_user=None, name=name, email=email)

        with get_db() as conn:
            existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                flash("An account with that email already exists. Please log in.", "error")
                return render_template("signup.html", current_user=None, name=name, email=email)

            password_hash = generate_password_hash(password)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email, password_hash, created_at)
            )
            user_id = cur.lastrowid
            conn.commit()

        flash("Your ELORA account has been created. Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html", current_user=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("index"))

    next_url = request.args.get("next") or request.form.get("next") or ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("login.html", current_user=None, email=email, next_url=next_url)

        if not password:
            flash("Password is required.", "error")
            return render_template("login.html", current_user=None, email=email, next_url=next_url)

        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password. Please try again.", "error")
            return render_template("login.html", current_user=None, email=email, next_url=next_url)

        session["user"] = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "is_admin": bool(user["is_admin"])
        }
        flash(f"Welcome back to ELORA, {user['name']}.", "success")

        if next_url and next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url)
        return redirect(url_for("index"))

    return render_template("login.html", current_user=None, next_url=next_url)


@app.route("/logout")
def logout():
    user = session.pop("user", None)
    if user:
        flash("You have been signed out. Until next time.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", current_user=session.get("user")), 404


@app.errorhandler(500)
def server_error(e):
    logging.error("Server error encountered: %s", e)
    return render_template("404.html", current_user=session.get("user"), is_500=True), 500


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
