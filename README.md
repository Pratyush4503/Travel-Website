# ✈️ TripEase — Travel Booking Platform

> A full-stack travel booking web application built with **Python Flask + SQLite**.  
> Book flights, hotels, tour packages, and cabs — with payment simulation and an admin dashboard.

🌐 **Live Demo:** [travel-website-agfv.onrender.com](https://travel-website-agfv.onrender.com)  
👤 **Author:** Pratyush Parashar · [@Pratyush4503](https://github.com/Pratyush4503)  
📦 **Stack:** Python · Flask · SQLite · Jinja2 · HTML/CSS

---

## 📸 Features

| Module | What it does |
|--------|-------------|
| ✈️ **Flights** | Search by route + date, Economy / Business class, multi-airline results |
| 🏨 **Hotels** | Search by city, filter by star rating, 3 room types with per-night pricing |
| 🗺️ **Tour Packages** | Browse by category (Adventure, Heritage, Beach, Spiritual), group booking |
| 🚗 **Cabs** | Outstation routes across India, Mini / Sedan / SUV pricing |
| 💳 **Payment Simulation** | Card, UPI, Net Banking, Wallet — fake TXN ID generated on success |
| 📋 **Booking History** | View, track status, and cancel all bookings in one place |
| ⚙️ **Admin Dashboard** | Revenue stats, booking breakdown by type, add flights/hotels, update order status |
| 🔐 **User Auth** | Register, login, hashed passwords via Werkzeug |

---

## 🗄️ Database Schema

8 SQLite tables:

```
users         → registered accounts (id, name, email, password, is_admin)
flights       → available routes (airline, origin, destination, date, price)
hotels        → properties (city, star_rating, price_single/double/suite)
tours         → packages (destination, duration, price_per_person, category)
cabs          → intercity routes (origin, destination, price_mini/sedan/suv)
bookings      → all booking types in one table (polymorphic: type + service_id)
payments      → simulated payment records (method, txn_id, amount)
reviews       → star ratings and comments (linked to any service type)
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/Pratyush4503/travel-booking-website.git
cd travel-booking-website

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database tables
python database.py

# 4. Load sample data
python seed_data.py

# 5. Start the server
python app.py
```

Open `http://localhost:5000` in your browser.

**Make yourself admin:**
1. Register a new account at `/register`
2. Visit `/make_admin/1`
3. Go to `/admin` — full dashboard access

---

## 📁 Project Structure

```
travel-booking-website/
├── app.py                  ← All 25+ Flask routes
├── database.py             ← 8 table definitions (run once)
├── seed_data.py            ← Sample data: 12 flights, 12 hotels, 8 tours, 12 cabs
├── requirements.txt
├── render.yaml             ← Render deployment config
├── templates/
│   ├── base.html           ← Shared navbar, flash messages, footer
│   ├── index.html          ← Hero with 4-tab search widget
│   ├── register.html
│   ├── login.html
│   ├── bookings.html       ← Unified booking history
│   ├── payment.html        ← Simulated payment page
│   ├── confirmation.html   ← Post-booking confirmation
│   ├── flights/            search.html, book.html
│   ├── hotels/             search.html, book.html
│   ├── tours/              list.html, book.html
│   ├── cabs/               search.html, book.html
│   └── admin/              dashboard.html, manage.html
└── static/
    └── style.css           ← ~600 lines, full custom design system
```

---

## 🧠 Key Concepts Demonstrated

| Concept | Where it appears |
|---------|-----------------|
| Flask routing + Jinja2 templates | Every page |
| `request.args` (GET) vs `request.form` (POST) | Search vs booking forms |
| Session-based pending booking | `session['pending_booking']` in payment flow |
| Polymorphic DB association | One `bookings` table handles all 4 service types |
| Two-phase checkout | Booking only saved to DB after payment confirms |
| SQL `LEFT JOIN` | Booking history joins payments without hiding unpaid rows |
| `COALESCE(SUM(...), 0)` | Admin revenue handles NULL when no payments exist |
| Password hashing | `werkzeug.security.generate_password_hash` |
| Decorator-based auth | `@login_required`, `@admin_required` |
| Auto DB init on startup | `initialize()` with `app.app_context()` for Render deploy |

---

## 🌐 Deployment

Deployed on **Render** (free tier). Auto-redeploys on every push to `main`.

The app self-initializes on startup — if `travel.db` doesn't exist (e.g. after a Render redeploy), it creates all tables and seeds sample data automatically before serving any requests.

```yaml
# render.yaml
buildCommand: "pip install -r requirements.txt"
startCommand:  "gunicorn app:app"
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Web framework | Flask 3.x |
| Database | SQLite (via Python's built-in `sqlite3`) |
| Templating | Jinja2 |
| Auth | Werkzeug password hashing |
| Production server | Gunicorn |
| Hosting | Render (free tier) |
| Frontend | Vanilla HTML5 + CSS3 (no frameworks) |

---

## 🗺️ Sample Data Included

- **12 flights** — IndiGo, Air India, SpiceJet, Vistara across Delhi, Mumbai, Bangalore, Goa, Chennai, Kolkata
- **12 hotels** — from budget guesthouses to 5-star palaces across 6 cities
- **8 tour packages** — Golden Triangle, Kerala Backwaters, Leh Ladakh, Goa Beach, Rajasthan Royale and more
- **12 cab routes** — Delhi→Agra, Mumbai→Pune, Bangalore→Mysore and more

---

*Part of a series of Python projects by Pratyush Parashar — [github.com/Pratyush4503](https://github.com/Pratyush4503)*
