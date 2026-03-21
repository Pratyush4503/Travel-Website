"""
seed_data.py — Fills the database with realistic Indian travel data.
Run AFTER database.py.
"""

import sqlite3

def seed():
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM flights")
    if c.fetchone()[0] > 0:
        print("⚠️  Data already exists. Skipping.")
        conn.close()
        return

    # ── FLIGHTS ────────────────────────────────────────────────────────
    flights = [
        # (airline, number, origin, destination, dep, arr, dur_hrs, eco, biz, seats_eco, seats_biz, date, stops)
        ('IndiGo',       '6E-201', 'Delhi',   'Mumbai',   '06:00', '08:10', 2.2,  4500,  12000, 150, 20, '2025-09-01', 0),
        ('IndiGo',       '6E-202', 'Mumbai',  'Delhi',    '09:00', '11:15', 2.3,  4800,  12500, 150, 20, '2025-09-01', 0),
        ('Air India',    'AI-101', 'Delhi',   'Bangalore','07:30', '10:00', 2.5,  5200,  14000, 180, 30, '2025-09-01', 0),
        ('Air India',    'AI-102', 'Bangalore','Delhi',   '11:00', '13:30', 2.5,  5500,  14500, 180, 30, '2025-09-01', 0),
        ('SpiceJet',     'SG-301', 'Delhi',   'Goa',      '08:00', '10:30', 2.5,  4200,  11000, 160, 18, '2025-09-02', 0),
        ('SpiceJet',     'SG-302', 'Goa',     'Delhi',    '12:00', '14:30', 2.5,  4400,  11500, 160, 18, '2025-09-02', 0),
        ('Vistara',      'UK-501', 'Mumbai',  'Bangalore','10:00', '11:30', 1.5,  5800,  15000, 140, 24, '2025-09-01', 0),
        ('Vistara',      'UK-502', 'Bangalore','Mumbai',  '14:00', '15:30', 1.5,  6000,  15500, 140, 24, '2025-09-01', 0),
        ('IndiGo',       '6E-401', 'Delhi',   'Kolkata',  '06:30', '09:00', 2.5,  5100,  13000, 160, 20, '2025-09-03', 0),
        ('Air India',    'AI-601', 'Mumbai',  'Chennai',  '07:00', '09:15', 2.3,  4900,  13500, 170, 28, '2025-09-03', 0),
        ('IndiGo',       '6E-700', 'Delhi',   'Mumbai',   '14:00', '16:10', 2.2,  3900,  10000, 150, 20, '2025-09-05', 0),
        ('SpiceJet',     'SG-801', 'Chennai', 'Delhi',    '08:00', '11:00', 3.0,  5300,  13500, 155, 20, '2025-09-04', 1),
    ]
    c.executemany(
        """INSERT INTO flights (airline,flight_number,origin,destination,departure_time,
           arrival_time,duration_hrs,price_economy,price_business,seats_economy,
           seats_business,flight_date,stops) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        flights
    )
    print("✅ Added 12 flights")

    # ── HOTELS ─────────────────────────────────────────────────────────
    hotels = [
        # (name, city, address, stars, amenities, single, double, suite, desc, emoji)
        ('The Taj Palace',        'Delhi',     'Sardar Patel Marg',     5, 'Pool,Spa,Gym,Restaurant', 8500,  12000, 28000, 'Iconic 5-star luxury in the heart of Delhi', '🏰'),
        ('Lemon Tree Premier',    'Delhi',     'Aerocity',              4, 'Pool,Gym,Restaurant',      4500,  6500,  12000, 'Modern business hotel near the airport',    '🍋'),
        ('Hotel Midland',         'Delhi',     'Paharganj',             2, 'WiFi,AC',                  1200,  1800,  3500,  'Budget stay near New Delhi Railway Station','🏨'),
        ('The Oberoi',            'Mumbai',    'Nariman Point',         5, 'Pool,Spa,Gym,Beach',       9500,  14000, 35000, 'Legendary luxury overlooking the sea',      '🌊'),
        ('Novotel Mumbai',        'Mumbai',    'Juhu Beach',            4, 'Pool,Gym,Restaurant',      5200,  7800,  15000, 'Premium hotel steps from Juhu Beach',       '🏖️'),
        ('Hotel Sea Princess',    'Mumbai',    'Juhu',                  3, 'Restaurant,WiFi',          2800,  4200,  8000,  'Comfortable stay with sea view rooms',      '🐚'),
        ('ITC Windsor',           'Bangalore', 'Golf Course Road',      5, 'Pool,Spa,Golf,Restaurant', 7800,  11500, 26000, 'Palatial heritage hotel in Bangalore',      '🎩'),
        ('Treebo Trend',          'Bangalore', 'Koramangala',           3, 'WiFi,AC,Breakfast',        2200,  3200,  6500,  'Smart budget hotel in tech hub Koramangala','🌿'),
        ('Radisson Blu',          'Goa',       'Cavelossim Beach',      5, 'Pool,Spa,Beach,Bar',       7200,  10500, 24000, 'Beachfront resort with stunning views',     '🌴'),
        ('Cidade de Goa',         'Goa',       'Vainguinim Beach',      4, 'Pool,Restaurant,Beach',    4800,  7200,  16000, 'Portuguese heritage resort in Goa',         '⛱️'),
        ('The Leela Palace',      'Chennai',   'MRC Nagar',             5, 'Pool,Spa,Gym,Restaurant',  8200,  12500, 30000, 'Ultra-luxe palace hotel in Chennai',        '👑'),
        ('Vivanta by Taj',        'Kolkata',   'EM Bypass',             4, 'Pool,Gym,Restaurant',      5500,  8000,  18000, 'Contemporary luxury in Kolkata',            '🌸'),
    ]
    c.executemany(
        """INSERT INTO hotels (name,city,address,star_rating,amenities,price_single,
           price_double,price_suite,description,image_emoji) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        hotels
    )
    print("✅ Added 12 hotels")

    # ── TOURS ──────────────────────────────────────────────────────────
    tours = [
        # (name, destination, days, price/person, max, inclusions, desc, category, start_date, emoji)
        ('Golden Triangle',       'Delhi-Agra-Jaipur', 6,  18000, 20, 'Hotel,Transport,Guide,Breakfast',   'Classic India tour covering Taj Mahal, Red Fort, Amber Palace', 'Heritage',   '2025-09-15', '🏛️'),
        ('Goa Beach Escape',      'Goa',               5,  12000, 15, 'Resort,Meals,Water sports,Taxi',    'Sun, sand and seafood in India\'s party capital',               'Beach',      '2025-09-20', '🏄'),
        ('Kerala Backwaters',     'Kerala',             7,  22000, 12, 'Houseboat,Meals,Ayurveda,Transfers','Serene cruise through palm-lined waterways',                   'Nature',     '2025-09-10', '🚣'),
        ('Leh Ladakh Adventure',  'Ladakh',             8,  28000, 10, 'Hotel,Jeep Safari,Guide,Meals',     'High-altitude desert landscapes and Buddhist monasteries',      'Adventure',  '2025-09-05', '🏔️'),
        ('Rajasthan Royale',      'Rajasthan',         10,  32000, 16, 'Heritage Hotels,Camel Safari,Guide','Palace hotels, desert dunes and colourful culture',             'Heritage',   '2025-10-01', '🐪'),
        ('Andaman Islands',       'Port Blair',         6,  24000, 14, 'Resort,Snorkelling,Ferry,Meals',    'Crystal-clear waters and pristine coral reefs',                 'Beach',      '2025-09-25', '🐠'),
        ('Manali Himalaya Trek',  'Manali',             5,  15000, 12, 'Guesthouse,Trek Guide,Equipment',   'Snow-capped peaks and mountain meadow camping',                 'Adventure',  '2025-09-12', '⛺'),
        ('Varanasi Spiritual',    'Varanasi',           4,  10000, 20, 'Hotel,Boat Ride,Guide,Meals',       'Ancient city, Ganga Aarti and temple walks',                   'Spiritual',  '2025-09-18', '🕯️'),
    ]
    c.executemany(
        """INSERT INTO tours (name,destination,duration_days,price_per_person,max_people,
           inclusions,description,category,start_date,image_emoji) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        tours
    )
    print("✅ Added 8 tour packages")

    # ── CABS ───────────────────────────────────────────────────────────
    cabs = [
        # (origin, destination, km, mini, sedan, suv, hrs)
        ('Delhi',     'Agra',      210, 2800,  3500,  4800,  3.5),
        ('Delhi',     'Jaipur',    270, 3500,  4400,  6000,  4.5),
        ('Mumbai',    'Pune',      155, 2200,  2800,  3900,  2.5),
        ('Mumbai',    'Nashik',    170, 2400,  3000,  4200,  3.0),
        ('Bangalore', 'Mysore',    145, 2000,  2500,  3500,  3.0),
        ('Bangalore', 'Ooty',      260, 3400,  4200,  5800,  4.5),
        ('Chennai',   'Pondicherry',155, 2200, 2800,  3900,  2.5),
        ('Delhi',     'Chandigarh',250, 3200,  4000,  5500,  4.0),
        ('Kolkata',   'Digha',     185, 2500,  3200,  4400,  3.5),
        ('Goa',       'Hampi',     340, 4400,  5500,  7500,  6.0),
        ('Hyderabad', 'Warangal',  145, 2000,  2500,  3400,  2.5),
        ('Jaipur',    'Pushkar',    60,  900,  1100,  1500,  1.5),
    ]
    c.executemany(
        """INSERT INTO cabs (origin,destination,distance_km,price_mini,price_sedan,
           price_suv,duration_hrs) VALUES (?,?,?,?,?,?,?)""",
        cabs
    )
    print("✅ Added 12 cab routes")
    print("\n🎉 Seed complete! Run: python app.py")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed()
