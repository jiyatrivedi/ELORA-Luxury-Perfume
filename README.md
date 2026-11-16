# ELORA — Haute Parfumerie & Luxury E-Commerce

> *A Scent That Becomes Your Signature.*

**ELORA** is a full-stack, luxury e-commerce web platform for a high-end perfume brand. Handcrafted with Python Flask, SQLite, HTML5, CSS3, and JavaScript, it presents an aesthetic of obsidian noir, champagne gold, and ivory, complemented by smooth scroll-triggered animations and mouse-driven parallax flacon visuals.

---

## ✨ Features & Architecture

### 🛍️ Client Shopping Experience
- **Luxury Preloader** — Ambient gold monogram `E` and brand shimmering sequence.
- **Animated Hero Stage** — 3D floating perfume flacons with interactive mouse parallax, golden aura pulses, and pedestal reflections.
- **Real-Time Collection Controls** — Instant client-side search across notes, fragrance names, and olfactory families, with instant category filter tabs (Woody & Amber, Floral & Fresh, Oriental & Spiced, Deep Oud & Leather) and price/rating sorting.
- **In-Page Quick Discover** — Fast preview drawer with olfactory notes pills and immediate quantity adjustment.
- **Dedicated Product Pages (`/product/<id>`)** — High-resolution flacon showcase, tripartite Olfactory Pyramid (Top, Heart, Base notes), longevity and sillage meters, 50ml / 100ml flacon size selector with dynamic pricing, verified customer reviews, and review submission form.
- **Shopping Bag (`/cart`)** — Persistent bag via `localStorage`, live subtotal computation, coupon privilege validation (`ELORA10`, `LUXURY20`, `SIGNATURE`), and complimentary gift wrap.
- **White-Glove Checkout (`/checkout`)** — Pre-filled member contact details and address from user profile, multiple payment methods (Cash on Delivery, Concierge Card Terminal, UPI / Digital Banking), server-side price calculation, and complimentary gift wrap toggle.
- **Order Confirmation & Tracking (`/order/<order_number>`)** — 5-step visual tracking stepper (Order Confirmed → Atelier Bottling → Wax-Sealed → With Courier → Handover Complete), itemized receipt, printable invoice (`window.print()`), and email dispatch.
- **Fully Responsive Luxury Suite & Universal Navigation** — Pixel-perfect adaptation across mobile (320px–480px), tablet (641px–1024px), and desktop. Features a universal slide-in mobile navigation menu, touch-friendly touch targets, horizontally scroll-protected receipt and cart tables, and responsive product cards with no text collisions or layout breaks.

### 👤 Member Account & Profile (`/profile`)
- **Account Overview** — Member standing tier, lifetime orders count, and total valuation spent.
- **Delivery Address Management** — Saved address, city, state, postal code, and telephone contact auto-fills into checkout.
- **Security & Password Management** — Secure password update form with PBKDF2 verification.
- **Order History (`/orders`)** — Complete past order receipts with fulfillment status badges.

### 👑 Executive Admin Atelier Dashboard (`/admin`)
- **Key Metrics Overview** — Total Gross Revenue, Total Orders Handled, Active Fragrances in Catalog, Registered Connoisseurs.
- **Fulfillment & Status Manager** — Live order status updater (`Confirmed`, `Processing`, `Dispatched`, `Delivered`, `Cancelled`).
- **Catalog Management** — Add new fragrances with scent families, notes, and stock levels; edit pricing and details; archive items.
- **Security Guard** — Protected by `@admin_required` decorator.

### 📧 Automated Email Notifications
- **Branded HTML Receipt** — Automated order receipt sent via Gmail SMTP.
- **Failure-Safe** — If email credentials are not configured, orders persist reliably without errors.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3 &bull; Flask 3.1 |
| **Database** | SQLite 3 (with auto-migration) |
| **Auth** | PBKDF2 password hashing via `werkzeug.security` |
| **Templating** | Jinja2 |
| **Frontend** | HTML5 &bull; Vanilla CSS3 &bull; Modern Vanilla JS |
| **Fonts** | Google Fonts (*Cormorant Garamond*, *Montserrat*, *Poppins*) |
| **Email** | Python `smtplib` &bull; MIME multipart HTML emails |
| **Environment** | `python-dotenv` |

---

## 📁 Project Structure

```
ELORA/
├── app.py                      # Flask backend, database migrations, routes, admin
├── email_service.py            # Branded HTML email service via SMTP
├── elora.db                    # SQLite database (auto-migrated on startup)
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
├── README.md                   # Documentation & setup guide
├── templates/
│   ├── index.html              # Landing page (hero, collection, atelier, story, reviews)
│   ├── product_detail.html     # Dedicated luxury fragrance product page
│   ├── cart.html               # Shopping bag with coupon code support
│   ├── checkout.html           # White-glove delivery address & payment options
│   ├── order_confirmation.html # Order receipt & visual tracking stepper
│   ├── my_orders.html          # Member order history
│   ├── profile.html            # User account settings, saved address & password
│   ├── admin.html              # Executive admin dashboard (orders & inventory)
│   ├── login.html              # Authentication (sign in)
│   ├── signup.html             # Member registration
│   └── 404.html                # Luxury error page
└── static/
    ├── css/
    │   └── style.css           # Global luxury stylesheet
    ├── js/
    │   └── script.js           # Client interactions, search, filters, cart sync
    └── images/
        ├── elora-hero.png      # High-res flacon centerpiece
        ├── elora-noir.png      # ELORA NOIR transparent PNG
        ├── elora-eclat.png     # ELORA ÉCLAT transparent PNG
        ├── elora-velvet.png    # ELORA VELVET transparent PNG
        ├── elora-oud.png       # ELORA OUD transparent PNG
        └── elora-solaris.png   # ELORA SOLARIS ROYALE transparent PNG
```

---

## ⚙️ Installation & Setup

### 1. Clone or Open the Project Directory

```bash
cd perfume
```

### 2. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional for Email)

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env`:

```env
ELORA_SECRET_KEY=elora-luxury-secret-key-2026
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_16_digit_app_password
```

*(Note: If email credentials are not set, the entire app and order placement still function smoothly; errors are safely logged).*

### 5. Run the Application

```bash
python app.py
```

Open your browser at:
```
http://127.0.0.1:5000
```

---

## 🔑 Administrative Access

- The first user account created or any account with email `admin@eloraparfum.com` is granted administrative access.
- Existing administrator in `elora.db`: `jiyatrivedi85@gmail.com`.
- Once logged in as an administrator, an **"Admin Atelier"** link appears in the navbar user dropdown, or you can navigate directly to `/admin`.
- In the Admin Atelier, you can:
  - Inspect all client orders and update fulfillment status.
  - Add new fragrances to the catalog with custom notes and prices.
  - Delete or archive existing products.

---

## 🏷️ VIP Privilege Codes

During checkout or on the `/cart` page, test any of the following privilege codes:
- **`ELORA10`** &mdash; 10% off entire order.
- **`LUXURY20`** &mdash; 20% exclusive member discount.
- **`SIGNATURE`** &mdash; $30 signature gift credit.

---

## 🌹 The Signature Fragrances

| Flacon | Scent Family | Concentration | Price (USD) | Signature Notes |
|---|---|---|---|---|
| **ELORA NOIR** | Woody & Amber | Eau de Parfum (100ml) | $185 | Black Amber &bull; Dark Plum &bull; Smoked Birch |
| **ELORA ÉCLAT** | Floral & Fresh | Eau de Parfum (100ml) | $165 | Bergamot &bull; Jasmine Sambac &bull; White Musk |
| **ELORA VELVET** | Oriental & Spiced | Eau de Parfum (100ml) | $195 | Bulgarian Rose &bull; Golden Saffron &bull; Ambergris |
| **ELORA OUD** | Deep Oud & Leather | Eau de Parfum (100ml) | $245 | Cambodian Agarwood &bull; Italian Leather &bull; Bourbon Vanilla |
| **ELORA SOLARIS ROYALE** | Floral & Fresh | Eau de Parfum (100ml) | $225 | Neroli &bull; Solar Amber &bull; Golden Citrus |

---

## 🏛️ Atelier & Concierge Inquiries

For bespoke fragrance consultation, white-glove order assistance, or private appointments:
- **Concierge Email:** `concierge@eloraperfum.example`
- **Concierge Telephone:** `+91 00000 00000`
- **Atelier Address:** `ELORA Atelier, Ahmedabad, Gujarat, India`

---

## 🗃️ Database Schema

### `products`
| Column | Type | Description |
|---|---|---|
| `id` | TEXT PK | Slug identifier (e.g. `noir`, `oud`) |
| `name` | TEXT | Fragrance name |
| `price` | REAL | Price in USD |
| `image` | TEXT | Flacon image path |
| `category` | TEXT | Concentration (e.g. `Eau de Parfum`) |
| `scent_family` | TEXT | Scent family (e.g. `Woody & Amber`) |
| `tagline` | TEXT | Brief poetic description |
| `description` | TEXT | Full narrative description |
| `top_notes` | TEXT | Head olfactory notes |
| `heart_notes` | TEXT | Core heart notes |
| `base_notes` | TEXT | Sillage base notes |
| `notes_list` | TEXT | Bullet-separated note list |
| `volume` | TEXT | Flacon volume (`100 ml / 3.4 fl oz`) |
| `stock` | INTEGER | Inventory count |
| `featured` | INTEGER | Homepage spotlight flag |
| `rating` | REAL | Average star rating |
| `reviews_count` | INTEGER | Total client reviews |

### `users`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `name` | TEXT | Full client name |
| `email` | TEXT UNIQUE | Account email |
| `password_hash` | TEXT | PBKDF2-SHA256 password hash |
| `is_admin` | INTEGER | Admin privilege flag (1 = admin) |
| `phone` | TEXT | Saved telephone number |
| `address` | TEXT | Saved street delivery address |
| `city` | TEXT | Saved city |
| `state` | TEXT | Saved state |
| `pincode` | TEXT | Saved postal code |

### `orders`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `user_id` | INTEGER FK | User ID reference |
| `order_number` | TEXT UNIQUE | Unique reference (`ELORA-YYYYMMDD-XXXXX-XXXX`) |
| `status` | TEXT | `confirmed`, `processing`, `dispatched`, `delivered`, `cancelled` |
| `total` | REAL | Calculated final total |
| `discount` | REAL | Coupon discount deducted |
| `payment_method` | TEXT | Selected payment option |
| `gift_wrap` | INTEGER | Complimentary gift packaging flag |
| `full_name`, `email`, `phone`, `address`, `city`, `state`, `pincode` | TEXT | Delivery recipient details |
| `created_at` | TEXT | Timestamp |

### `order_items`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `order_id` | INTEGER FK | Reference to `orders(id)` |
| `product_id` | TEXT | Product slug |
| `product_name` | TEXT | Product name |
| `unit_price` | REAL | Authoritative price at order time |
| `quantity` | INTEGER | Number of flacons |
| `subtotal` | REAL | Item subtotal |
| `image` | TEXT | Flacon image path |

### `reviews`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `product_id` | TEXT FK | Reference to `products(id)` |
| `user_name` | TEXT | Connoisseur reviewer name |
| `rating` | INTEGER | Star rating (1 to 5) |
| `comment` | TEXT | Review impressions |
| `created_at` | TEXT | Timestamp |

---

&copy; 2026 ELORA Haute Parfumerie. Crafted for those who leave an impression.
