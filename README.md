# ✈️ Travel Booking Website
**Project 4 by Pratyush Parashar | GitHub: Pratyush4503**

A full-stack travel booking platform built with Flask + SQLite.
Book flights, hotels, tour packages, and cabs — all in one app.

## Features
- **Flights** — search by route + date, Economy / Business class
- **Hotels** — search by city, filter by star rating, 3 room types
- **Tour Packages** — browse by category (Adventure, Heritage, Beach…)
- **Cabs** — outstation routes, Mini / Sedan / SUV
- **Payment simulation** — Card, UPI, Net Banking, Wallet
- **Booking history** — view + cancel your bookings
- **Admin dashboard** — revenue stats, bar charts, add listings, update orders
- **User auth** — register, login, hashed passwords

## Tech Stack
| Layer    | Technology |
|----------|------------|
| Backend  | Python 3 + Flask |
| Database | SQLite (travel.db, 8 tables) |
| Frontend | HTML5 + Jinja2 + CSS3 |
| Auth     | Werkzeug password hashing |

## Quick Start in GitHub Codespaces

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create all 8 database tables
python database.py

# 3. Load sample data (12 flights, 12 hotels, 8 tours, 12 cabs)
python seed_data.py

# 4. Run the server
python app.py
```

Open port 5000 from the Codespaces popup.

**Become admin:**
1. Register a new account
2. Visit: `/make_admin/1`
3. Go to `/admin` — you now have full admin access

## Project Structure
```
travel-booking-website/
├── app.py            ← All 25+ routes
├── database.py       ← 8 table definitions
├── seed_data.py      ← Sample data loader
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html    ← Hero with 4-tab search
│   ├── register.html / login.html
│   ├── flights/      search.html, book.html
│   ├── hotels/       search.html, book.html
│   ├── tours/        list.html, book.html
│   ├── cabs/         search.html, book.html
│   ├── payment.html  ← Fake payment page
│   ├── confirmation.html
│   ├── bookings.html ← Full booking history
│   └── admin/        dashboard.html, manage.html
└── static/
    └── style.css
```

## Key New Concepts (vs Project 3)
| Concept | Where it's used |
|---------|-----------------|
| Polymorphic association | One `bookings` table for all service types |
| `request.args` vs `request.form` | Search = GET args, forms = POST |
| Two-phase checkout | Session holds pending booking until payment confirmed |
| SQL LEFT JOIN | Bookings page joins payments even if no payment exists |
| SQL COALESCE | `COALESCE(SUM(amount), 0)` handles NULL when no rows exist |
| `PRAGMA foreign_keys = ON` | SQLite doesn't enforce FK by default |
| Fake TXN ID | `'TXN' + random 10 digits` |
| CSS custom properties | Full design token system in `:root {}` |
