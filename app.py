"""
app.py — Travel Booking Platform
All routes for: flights, hotels, tours, cabs, bookings, payments, admin.

NEW CONCEPTS vs Project 3:
- BLUEPRINTS pattern avoided for simplicity — all routes in one file
- URL query parameters for search (?from=Delhi&to=Mumbai&date=...)
- request.args vs request.form:
    request.args  → GET params from URL  (?key=value)
    request.form  → POST params from form submission
- Random transaction ID generation for fake payments
- SQL aggregate functions: COUNT(), SUM(), AVG()
"""

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, random, string
from functools import wraps
from database import init_db

app = Flask(__name__)
import os
app.secret_key = os.environ.get('SECRET_KEY', 'travel-app-secret-2025-fallback')

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect('travel.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper

def make_txn_id():
    """Generates a fake transaction ID like TXN8473920154."""
    return 'TXN' + ''.join(random.choices(string.digits, k=10))

# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────

@app.route('/')
def index():
    """
    Home page with search hero.
    Shows popular destinations and recent stats.
    """
    db = get_db()
    # Get distinct cities for autocomplete hints
    flight_cities = db.execute(
        "SELECT DISTINCT origin FROM flights UNION SELECT DISTINCT destination FROM flights ORDER BY 1"
    ).fetchall()
    hotel_cities = db.execute("SELECT DISTINCT city FROM hotels ORDER BY city").fetchall()
    tour_categories = db.execute("SELECT DISTINCT category FROM tours ORDER BY category").fetchall()
    db.close()
    return render_template('index.html',
                           flight_cities=[r['origin'] for r in flight_cities],
                           hotel_cities=[r['city'] for r in hotel_cities],
                           tour_categories=[r['category'] for r in tour_categories])

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        phone    = request.form.get('phone', '').strip()

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name,email,password,phone) VALUES (?,?,?,?)",
                (name, email, generate_password_hash(password), phone)
            )
            db.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user_id']  = user['id']
            session['username'] = user['name']
            session['is_admin'] = bool(user['is_admin'])
            flash(f"Welcome back, {user['name']}! ✈️", 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ─────────────────────────────────────────────
# FLIGHTS
# ─────────────────────────────────────────────

@app.route('/flights')
def flights_search():
    """
    GET /flights              → show search form (no results)
    GET /flights?from=X&to=Y&date=Z&passengers=1 → show results

    SQL LIKE operator: LIKE '%Delhi%' matches any string containing 'Delhi'
    UPPER() makes the comparison case-insensitive.
    """
    origin      = request.args.get('from', '').strip()
    destination = request.args.get('to', '').strip()
    date        = request.args.get('date', '')
    passengers  = int(request.args.get('passengers', 1))
    travel_class= request.args.get('class', 'economy')

    results = []
    if origin and destination:
        db = get_db()
        query = """
            SELECT * FROM flights
            WHERE UPPER(origin) LIKE UPPER(?)
              AND UPPER(destination) LIKE UPPER(?)
        """
        params = [f'%{origin}%', f'%{destination}%']
        if date:
            query += " AND flight_date = ?"
            params.append(date)
        query += " ORDER BY price_economy ASC"
        results = db.execute(query, params).fetchall()
        db.close()

    return render_template('flights/search.html',
                           results=results, origin=origin,
                           destination=destination, date=date,
                           passengers=passengers, travel_class=travel_class)

@app.route('/flights/book/<int:flight_id>')
@login_required
def flight_book(flight_id):
    """Show booking form for a specific flight."""
    db = get_db()
    flight = db.execute("SELECT * FROM flights WHERE id=?", (flight_id,)).fetchone()
    db.close()
    if not flight:
        flash('Flight not found.', 'danger')
        return redirect(url_for('flights_search'))
    passengers   = int(request.args.get('passengers', 1))
    travel_class = request.args.get('class', 'economy')
    price = flight['price_economy'] if travel_class == 'economy' else flight['price_business']
    total = price * passengers
    return render_template('flights/book.html', flight=flight,
                           passengers=passengers, travel_class=travel_class, total=total)

# ─────────────────────────────────────────────
# HOTELS
# ─────────────────────────────────────────────

@app.route('/hotels')
def hotels_search():
    city      = request.args.get('city', '').strip()
    check_in  = request.args.get('check_in', '')
    check_out = request.args.get('check_out', '')
    guests    = int(request.args.get('guests', 1))
    min_stars = int(request.args.get('stars', 0))

    results = []
    if city:
        db = get_db()
        query = "SELECT * FROM hotels WHERE UPPER(city) LIKE UPPER(?)"
        params = [f'%{city}%']
        if min_stars:
            query += " AND star_rating >= ?"
            params.append(min_stars)
        query += " ORDER BY star_rating DESC"
        results = db.execute(query, params).fetchall()
        db.close()

    return render_template('hotels/search.html',
                           results=results, city=city,
                           check_in=check_in, check_out=check_out,
                           guests=guests, min_stars=min_stars)

@app.route('/hotels/book/<int:hotel_id>')
@login_required
def hotel_book(hotel_id):
    db = get_db()
    hotel = db.execute("SELECT * FROM hotels WHERE id=?", (hotel_id,)).fetchone()
    db.close()
    if not hotel:
        flash('Hotel not found.', 'danger')
        return redirect(url_for('hotels_search'))
    check_in   = request.args.get('check_in', '')
    check_out  = request.args.get('check_out', '')
    room_type  = request.args.get('room', 'single')
    guests     = int(request.args.get('guests', 1))

    # Calculate nights and total
    nights = 1
    if check_in and check_out:
        from datetime import datetime
        try:
            d1 = datetime.strptime(check_in, '%Y-%m-%d')
            d2 = datetime.strptime(check_out, '%Y-%m-%d')
            nights = max(1, (d2 - d1).days)
        except ValueError:
            pass

    price_map = {'single': hotel['price_single'], 'double': hotel['price_double'], 'suite': hotel['price_suite']}
    total = price_map.get(room_type, hotel['price_single']) * nights

    return render_template('hotels/book.html', hotel=hotel,
                           check_in=check_in, check_out=check_out,
                           room_type=room_type, guests=guests,
                           nights=nights, total=total)

# ─────────────────────────────────────────────
# TOURS
# ─────────────────────────────────────────────

@app.route('/tours')
def tours_list():
    category = request.args.get('category', '')
    db = get_db()
    if category:
        tours = db.execute(
            "SELECT * FROM tours WHERE category=? ORDER BY price_per_person", (category,)
        ).fetchall()
    else:
        tours = db.execute("SELECT * FROM tours ORDER BY price_per_person").fetchall()
    categories = db.execute("SELECT DISTINCT category FROM tours ORDER BY category").fetchall()
    db.close()
    return render_template('tours/list.html', tours=tours,
                           categories=categories, selected_category=category)

@app.route('/tours/book/<int:tour_id>')
@login_required
def tour_book(tour_id):
    db = get_db()
    tour = db.execute("SELECT * FROM tours WHERE id=?", (tour_id,)).fetchone()
    db.close()
    if not tour:
        flash('Tour not found.', 'danger')
        return redirect(url_for('tours_list'))
    people = int(request.args.get('people', 1))
    total  = tour['price_per_person'] * people
    return render_template('tours/book.html', tour=tour, people=people, total=total)

# ─────────────────────────────────────────────
# CABS
# ─────────────────────────────────────────────

@app.route('/cabs')
def cabs_search():
    origin      = request.args.get('from', '').strip()
    destination = request.args.get('to', '').strip()
    cab_date    = request.args.get('date', '')

    results = []
    if origin and destination:
        db = get_db()
        results = db.execute(
            """SELECT * FROM cabs
               WHERE UPPER(origin) LIKE UPPER(?) AND UPPER(destination) LIKE UPPER(?)
               ORDER BY price_mini""",
            (f'%{origin}%', f'%{destination}%')
        ).fetchall()
        db.close()

    # Get distinct cities for dropdowns
    db = get_db()
    cab_cities = db.execute(
        "SELECT DISTINCT origin FROM cabs UNION SELECT DISTINCT destination FROM cabs ORDER BY 1"
    ).fetchall()
    db.close()

    return render_template('cabs/search.html', results=results,
                           origin=origin, destination=destination,
                           cab_date=cab_date,
                           cab_cities=[r['origin'] for r in cab_cities])

@app.route('/cabs/book/<int:cab_id>')
@login_required
def cab_book(cab_id):
    db = get_db()
    cab = db.execute("SELECT * FROM cabs WHERE id=?", (cab_id,)).fetchone()
    db.close()
    if not cab:
        flash('Cab route not found.', 'danger')
        return redirect(url_for('cabs_search'))
    cab_type = request.args.get('type', 'mini')
    cab_date = request.args.get('date', '')
    price_map = {'mini': cab['price_mini'], 'sedan': cab['price_sedan'], 'suv': cab['price_suv']}
    total = price_map.get(cab_type, cab['price_mini'])
    return render_template('cabs/book.html', cab=cab,
                           cab_type=cab_type, cab_date=cab_date, total=total)

# ─────────────────────────────────────────────
# PAYMENT (shared by all booking types)
# ─────────────────────────────────────────────

@app.route('/payment', methods=['POST'])
@login_required
def payment():
    """
    Receives booking form data, shows payment page.

    We store pending booking data in session (not DB yet) —
    the DB insert happens only after payment is confirmed.
    This is the "two-phase commit" pattern for checkout flows.
    """
    # Collect all form fields into session for use after payment
    session['pending_booking'] = {
        'booking_type':   request.form['booking_type'],
        'service_id':     int(request.form['service_id']),
        'passengers':     int(request.form.get('passengers', 1)),
        'travel_class':   request.form.get('travel_class', 'economy'),
        'check_in_date':  request.form.get('check_in_date', ''),
        'check_out_date': request.form.get('check_out_date', ''),
        'room_type':      request.form.get('room_type', ''),
        'total_amount':   float(request.form['total_amount']),
        'service_name':   request.form.get('service_name', ''),
    }
    session.modified = True
    return render_template('payment.html',
                           booking=session['pending_booking'],
                           total=session['pending_booking']['total_amount'])

@app.route('/payment/confirm', methods=['POST'])
@login_required
def payment_confirm():
    """
    Processes the fake payment and creates the booking + payment records.

    WHAT WE SIMULATE:
    - Card / UPI / Net Banking / Wallet payment methods
    - 95% success rate (random failure for realism)
    - Generate a fake TXN ID
    """
    pending = session.get('pending_booking')
    if not pending:
        flash('Session expired. Please try again.', 'danger')
        return redirect(url_for('index'))

    method = request.form.get('payment_method', 'card')

    # Simulate 5% failure rate
    if random.random() < 0.05:
        flash('Payment failed. Please try again.', 'danger')
        return redirect(url_for('index'))

    db = get_db()
    try:
        # 1. Create the booking (status = confirmed)
        cursor = db.execute(
            """INSERT INTO bookings
               (user_id,booking_type,service_id,passengers,travel_class,
                check_in_date,check_out_date,room_type,total_amount,status)
               VALUES (?,?,?,?,?,?,?,?,?,'confirmed')""",
            (
                session['user_id'],
                pending['booking_type'],
                pending['service_id'],
                pending['passengers'],
                pending['travel_class'],
                pending['check_in_date'],
                pending['check_out_date'],
                pending['room_type'],
                pending['total_amount'],
            )
        )
        booking_id = cursor.lastrowid

        # 2. Create the payment record
        txn_id = make_txn_id()
        db.execute(
            """INSERT INTO payments (booking_id,user_id,amount,method,txn_id,status)
               VALUES (?,?,?,?,?,'success')""",
            (booking_id, session['user_id'], pending['total_amount'], method, txn_id)
        )

        db.commit()
        session.pop('pending_booking', None)

        flash(f"🎉 Booking confirmed! Transaction ID: {txn_id}", 'success')
        return redirect(url_for('confirmation', booking_id=booking_id))

    except Exception as e:
        db.rollback()
        flash(f'Error processing booking: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        db.close()

@app.route('/confirmation/<int:booking_id>')
@login_required
def confirmation(booking_id):
    db = get_db()
    booking = db.execute(
        "SELECT * FROM bookings WHERE id=? AND user_id=?",
        (booking_id, session['user_id'])
    ).fetchone()
    payment = db.execute(
        "SELECT * FROM payments WHERE booking_id=?", (booking_id,)
    ).fetchone()
    db.close()
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('index'))
    return render_template('confirmation.html', booking=booking, payment=payment)

# ─────────────────────────────────────────────
# MY BOOKINGS
# ─────────────────────────────────────────────

@app.route('/bookings')
@login_required
def my_bookings():
    """
    Shows all bookings for the logged-in user.

    COMPLEX SQL:
    We LEFT JOIN payments to get the txn_id alongside each booking.
    LEFT JOIN = include the booking row even if no matching payment exists.
    (Inner JOIN would hide bookings without payments.)
    """
    db = get_db()
    bookings = db.execute(
        """SELECT b.*, p.txn_id, p.method, p.paid_at
           FROM bookings b
           LEFT JOIN payments p ON p.booking_id = b.id
           WHERE b.user_id = ?
           ORDER BY b.created_at DESC""",
        (session['user_id'],)
    ).fetchall()

    # Enrich each booking with service details
    enriched = []
    for b in bookings:
        detail = None
        btype = b['booking_type']
        sid   = b['service_id']
        if btype == 'flight':
            detail = db.execute("SELECT * FROM flights WHERE id=?", (sid,)).fetchone()
        elif btype == 'hotel':
            detail = db.execute("SELECT * FROM hotels WHERE id=?", (sid,)).fetchone()
        elif btype == 'tour':
            detail = db.execute("SELECT * FROM tours WHERE id=?", (sid,)).fetchone()
        elif btype == 'cab':
            detail = db.execute("SELECT * FROM cabs WHERE id=?", (sid,)).fetchone()
        enriched.append({'booking': b, 'detail': detail})

    db.close()
    return render_template('bookings.html', enriched=enriched)

@app.route('/bookings/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    db = get_db()
    booking = db.execute(
        "SELECT * FROM bookings WHERE id=? AND user_id=?",
        (booking_id, session['user_id'])
    ).fetchone()
    if not booking or booking['status'] == 'cancelled':
        flash('Cannot cancel this booking.', 'danger')
    else:
        db.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
        db.commit()
        flash(f'Booking #{booking_id} has been cancelled.', 'info')
    db.close()
    return redirect(url_for('my_bookings'))

# ─────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """
    Admin stats page.
    SQL aggregates: COUNT, SUM, AVG computed directly in SQL for efficiency.
    """
    db = get_db()

    stats = {
        'total_bookings':  db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],
        'confirmed':       db.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'").fetchone()[0],
        'total_revenue':   db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='success'").fetchone()[0],
        'total_users':     db.execute("SELECT COUNT(*) FROM users WHERE is_admin=0").fetchone()[0],
        'flight_bookings': db.execute("SELECT COUNT(*) FROM bookings WHERE booking_type='flight'").fetchone()[0],
        'hotel_bookings':  db.execute("SELECT COUNT(*) FROM bookings WHERE booking_type='hotel'").fetchone()[0],
        'tour_bookings':   db.execute("SELECT COUNT(*) FROM bookings WHERE booking_type='tour'").fetchone()[0],
        'cab_bookings':    db.execute("SELECT COUNT(*) FROM bookings WHERE booking_type='cab'").fetchone()[0],
    }

    recent_bookings = db.execute(
        """SELECT b.*, u.name as user_name, p.txn_id, p.method
           FROM bookings b
           JOIN users u ON b.user_id = u.id
           LEFT JOIN payments p ON p.booking_id = b.id
           ORDER BY b.created_at DESC
           LIMIT 20"""
    ).fetchall()

    # Revenue by type
    revenue_by_type = db.execute(
        """SELECT b.booking_type, COALESCE(SUM(p.amount),0) as rev
           FROM bookings b LEFT JOIN payments p ON p.booking_id=b.id
           GROUP BY b.booking_type"""
    ).fetchall()

    db.close()
    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_bookings=recent_bookings,
                           revenue_by_type=revenue_by_type)

@app.route('/admin/manage')
@login_required
@admin_required
def admin_manage():
    db = get_db()
    flights = db.execute("SELECT * FROM flights ORDER BY flight_date, origin").fetchall()
    hotels  = db.execute("SELECT * FROM hotels ORDER BY city, name").fetchall()
    tours   = db.execute("SELECT * FROM tours ORDER BY name").fetchall()
    cabs    = db.execute("SELECT * FROM cabs ORDER BY origin").fetchall()
    db.close()
    return render_template('admin/manage.html',
                           flights=flights, hotels=hotels,
                           tours=tours, cabs=cabs)

@app.route('/admin/add_flight', methods=['POST'])
@login_required
@admin_required
def admin_add_flight():
    f = request.form
    db = get_db()
    db.execute(
        """INSERT INTO flights (airline,flight_number,origin,destination,departure_time,
           arrival_time,duration_hrs,price_economy,price_business,flight_date,stops)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (f['airline'], f['flight_number'], f['origin'], f['destination'],
         f['departure_time'], f['arrival_time'], float(f['duration_hrs']),
         float(f['price_economy']), float(f['price_business']),
         f['flight_date'], int(f.get('stops', 0)))
    )
    db.commit()
    db.close()
    flash('Flight added!', 'success')
    return redirect(url_for('admin_manage'))

@app.route('/admin/add_hotel', methods=['POST'])
@login_required
@admin_required
def admin_add_hotel():
    f = request.form
    db = get_db()
    db.execute(
        """INSERT INTO hotels (name,city,address,star_rating,amenities,
           price_single,price_double,price_suite,description)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (f['name'], f['city'], f['address'], int(f['star_rating']), f['amenities'],
         float(f['price_single']), float(f['price_double']), float(f['price_suite']),
         f['description'])
    )
    db.commit()
    db.close()
    flash('Hotel added!', 'success')
    return redirect(url_for('admin_manage'))

@app.route('/admin/update_booking/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_booking(booking_id):
    status = request.form['status']
    db = get_db()
    db.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    db.commit()
    db.close()
    flash(f'Booking #{booking_id} updated to {status}.', 'success')
    return redirect(url_for('admin_dashboard'))

# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

@app.route('/make_admin/<int:user_id>')
def make_admin(user_id):
    """Dev utility — remove in production."""
    db = get_db()
    db.execute("UPDATE users SET is_admin=1 WHERE id=?", (user_id,))
    db.commit()
    db.close()
    flash(f'User #{user_id} is now admin.', 'success')
    return redirect(url_for('index'))

# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

def initialize():
    """
    Always run on startup — creates DB and seeds data if missing.
    On Render's free tier the filesystem resets on every deploy,
    so we can't rely on the build command having done this.
    """
    from database import init_db
    from seed_data import seed
    if not os.path.exists('travel.db'):
        print("🔧 Initializing database...")
        init_db()
        seed()
        print("✅ Database ready.")

# Run initialization immediately when the module loads
# This runs before gunicorn serves any requests
initialize()

def initialize():
    """
    Always run on startup — creates DB and seeds data if missing.
    On Render's free tier the filesystem resets on every deploy,
    so we can't rely on the build command having done this.
    """
    from database import init_db
    from seed_data import seed
    if not os.path.exists('travel.db'):
        print("🔧 Initializing database...")
        init_db()
        seed()
        print("✅ Database ready.")

# Run initialization immediately when the module loads
# This runs before gunicorn serves any requests
initialize()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
