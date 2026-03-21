"""
database.py — Creates all 8 tables for the travel booking platform.

NEW CONCEPTS vs Project 3:
- More complex table relationships (bookings links to 4 different services)
- TEXT CHECK constraints validate allowed values directly in the DB
- DEFAULT values save you from writing them in every INSERT

TABLE OVERVIEW:
  users       → people who register on the site
  flights     → available flight routes
  hotels      → available hotels with room types
  tours       → travel packages
  cabs        → cab routes between cities
  bookings    → ONE table for ALL booking types (flight/hotel/tour/cab)
  payments    → payment records linked to bookings
  reviews     → star ratings + comments for any service
"""

import sqlite3

def init_db():
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()

    # Enable foreign key enforcement in SQLite (OFF by default!)
    c.execute("PRAGMA foreign_keys = ON")

    # ── USERS ──────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            phone      TEXT,
            is_admin   INTEGER DEFAULT 0,
            created_at TEXT    DEFAULT (datetime('now'))
        )
    ''')

    # ── FLIGHTS ────────────────────────────────────────────────────────
    # Each row = one flight on one specific date
    c.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            airline        TEXT NOT NULL,
            flight_number  TEXT NOT NULL,
            origin         TEXT NOT NULL,
            destination    TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time   TEXT NOT NULL,
            duration_hrs   REAL NOT NULL,
            price_economy  REAL NOT NULL,
            price_business REAL NOT NULL,
            seats_economy  INTEGER DEFAULT 100,
            seats_business INTEGER DEFAULT 20,
            flight_date    TEXT NOT NULL,
            stops          INTEGER DEFAULT 0
        )
    ''')

    # ── HOTELS ─────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            city         TEXT NOT NULL,
            address      TEXT,
            star_rating  INTEGER DEFAULT 3,
            amenities    TEXT,
            price_single REAL NOT NULL,
            price_double REAL NOT NULL,
            price_suite  REAL NOT NULL,
            description  TEXT,
            image_emoji  TEXT DEFAULT '🏨'
        )
    ''')

    # ── TOURS ──────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS tours (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            destination    TEXT NOT NULL,
            duration_days  INTEGER NOT NULL,
            price_per_person REAL NOT NULL,
            max_people     INTEGER DEFAULT 20,
            inclusions     TEXT,
            description    TEXT,
            category       TEXT DEFAULT 'Adventure',
            start_date     TEXT,
            image_emoji    TEXT DEFAULT '🗺️'
        )
    ''')

    # ── CABS ───────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS cabs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            origin        TEXT NOT NULL,
            destination   TEXT NOT NULL,
            distance_km   INTEGER NOT NULL,
            price_mini    REAL NOT NULL,
            price_sedan   REAL NOT NULL,
            price_suv     REAL NOT NULL,
            duration_hrs  REAL NOT NULL
        )
    ''')

    # ── BOOKINGS ───────────────────────────────────────────────────────
    # WHY ONE TABLE FOR ALL TYPES?
    # Pattern called "polymorphic association" — one booking table works
    # for flights, hotels, tours, and cabs by using a type column.
    # service_id points to the relevant row in the right table.
    # This avoids creating flight_bookings, hotel_bookings, etc.
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            booking_type   TEXT    NOT NULL,  -- 'flight','hotel','tour','cab'
            service_id     INTEGER NOT NULL,  -- id in flights/hotels/tours/cabs
            passengers     INTEGER DEFAULT 1,
            travel_class   TEXT    DEFAULT 'economy',
            check_in_date  TEXT,
            check_out_date TEXT,
            room_type      TEXT,
            total_amount   REAL NOT NULL,
            status         TEXT DEFAULT 'pending',
            created_at     TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ── PAYMENTS ───────────────────────────────────────────────────────
    # Simulated payment records
    # txn_id is a fake transaction ID we generate
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id  INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            method      TEXT    NOT NULL,  -- 'card','upi','netbanking','wallet'
            txn_id      TEXT    UNIQUE,    -- fake: TXN + random digits
            status      TEXT    DEFAULT 'success',
            paid_at     TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (user_id)    REFERENCES users(id)
        )
    ''')

    # ── REVIEWS ────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            service_type TEXT    NOT NULL,  -- 'flight','hotel','tour','cab'
            service_id   INTEGER NOT NULL,
            rating       INTEGER NOT NULL,  -- 1 to 5
            comment      TEXT,
            created_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ travel.db created with 8 tables:")
    print("   users, flights, hotels, tours, cabs, bookings, payments, reviews")

if __name__ == '__main__':
    init_db()
