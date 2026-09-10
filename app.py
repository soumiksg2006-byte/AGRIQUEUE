from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3, secrets, hashlib
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

TRANSLATIONS = {
    "en": {
        "home": "Home",
        "register": "Register",
        "login": "Farmer Login",
        "book_slot": "Book Slot",
        "dashboard": "Dashboard",
        "weather": "Weather",
        "logout": "Logout",
        "admin": "Admin",
        "welcome": "Welcome to AgriQueue",
        "subtitle": "Smart Farmer Procurement & Queue Management",
        "get_started": "Get Started",
        "learn_more": "Learn More",
        "farmer_registration": "Farmer Registration",
        "name": "Name",
        "mobile_number": "Mobile Number",
        "village": "Village",
        "password": "Password",
        "submit": "Submit",
        "crop": "Crop",
        "quantity": "Quantity",
        "booking_date": "Booking Date",
        "slot": "Slot",
        "book": "Book",
        "status": "Status",
        "payment_status": "Payment Status"
    },

    "hi": {
        "home": "होम",
        "register": "पंजीकरण",
        "login": "किसान लॉगिन",
        "book_slot": "स्लॉट बुक करें",
        "dashboard": "डैशबोर्ड",
        "weather": "मौसम",
        "logout": "लॉगआउट",
        "admin": "एडमिन",
        "welcome": "AgriQueue में आपका स्वागत है",
        "subtitle": "स्मार्ट किसान खरीद और कतार प्रबंधन",
        "get_started": "शुरू करें",
        "learn_more": "और जानें",
        "farmer_registration": "किसान पंजीकरण",
        "name": "नाम",
        "mobile_number": "मोबाइल नंबर",
        "village": "गांव",
        "password": "पासवर्ड",
        "submit": "सबमिट करें",
        "crop": "फसल",
        "quantity": "मात्रा",
        "booking_date": "बुकिंग की तारीख",
        "slot": "स्लॉट",
        "book": "बुक करें",
        "status": "स्थिति",
        "payment_status": "भुगतान स्थिति"
    },

    "bn": {
        "home": "হোম",
        "register": "নিবন্ধন",
        "login": "কৃষক লগইন",
        "book_slot": "স্লট বুক করুন",
        "dashboard": "ড্যাশবোর্ড",
        "weather": "আবহাওয়া",
        "logout": "লগআউট",
        "admin": "অ্যাডমিন",
        "welcome": "AgriQueue-তে স্বাগতম",
        "subtitle": "স্মার্ট কৃষক সংগ্রহ ও কিউ ব্যবস্থাপনা",
        "get_started": "শুরু করুন",
        "learn_more": "আরও জানুন",
        "farmer_registration": "কৃষক নিবন্ধন",
        "name": "নাম",
        "mobile_number": "মোবাইল নম্বর",
        "village": "গ্রাম",
        "password": "পাসওয়ার্ড",
        "submit": "জমা দিন",
        "crop": "ফসল",
        "quantity": "পরিমাণ",
        "booking_date": "বুকিংয়ের তারিখ",
        "slot": "স্লট",
        "book": "বুক করুন",
        "status": "স্ট্যাটাস",
        "payment_status": "পেমেন্ট স্ট্যাটাস"
    }
}
@app.context_processor
def inject_translations():
    language = session.get("language", "en")

    return {
        "t": TRANSLATIONS[language],
        "current_language": language
    }


@app.route("/set-language", methods=["POST"])
def set_language():
    language = request.form.get("language", "en")

    if language in TRANSLATIONS:
        session["language"] = language

    return redirect(request.referrer or url_for("index"))

DB = "agriqueue.db"
DAILY_LIMIT = 50

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        village TEXT,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE NOT NULL,
        farmer_id TEXT NOT NULL,
        crop TEXT NOT NULL,
        quantity REAL NOT NULL,
        booking_date TEXT NOT NULL,
        slot TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Booked',
        actual_quantity REAL,
        rate REAL,
        payment_status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );
    """)
    con.commit()
    con.close()

def make_id(prefix):
    return prefix + datetime.now().strftime("%y%m%d") + secrets.token_hex(3).upper()

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def today_count(d):
    con=db()
    n=con.execute("SELECT COUNT(*) c FROM bookings WHERE booking_date=?", (d,)).fetchone()["c"]
    con.close()
    return n

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form["name"].strip()
        phone=request.form["phone"].strip()
        village=request.form["village"].strip()
        password=request.form["password"]

        if not name or not phone or not password:
            flash("Please fill all required fields.")
            return redirect(url_for("register"))

        con=db()
        existing=con.execute("SELECT * FROM farmers WHERE phone=?", (phone,)).fetchone()
        if existing:
            con.close()
            flash("This mobile number is already registered.")
            return redirect(url_for("register"))

        farmer_id=make_id("F")
        con.execute("""INSERT INTO farmers
            (farmer_id,name,phone,village,password_hash,created_at)
            VALUES (?,?,?,?,?,?)""",
            (farmer_id,name,phone,village,hash_pw(password),datetime.now().isoformat()))
        con.commit()
        con.close()

        session["farmer_id"]=farmer_id
        flash(f"Registration successful. Your Farmer ID is {farmer_id}.")
        return redirect(url_for("book"))

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        phone=request.form["phone"].strip()
        password=request.form["password"]
        con=db()
        f=con.execute("SELECT * FROM farmers WHERE phone=? AND password_hash=?",
                      (phone,hash_pw(password))).fetchone()
        con.close()
        if not f:
         flash("Invalid mobile number or password.")
         return redirect(url_for("login"))
        session["farmer_id"]=f["farmer_id"]
        return redirect(url_for("farmer_dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/book", methods=["GET","POST"])
def book():
    if "farmer_id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":
        farmer_id=session["farmer_id"]
        crop=request.form["crop"]
        quantity=float(request.form["quantity"])
        booking_date=request.form["booking_date"]
        slot=request.form["slot"]

        if booking_date < str(date.today()):
            flash("Please choose today or a future date.")
            return redirect(url_for("book"))

        if today_count(booking_date) >= DAILY_LIMIT:
            flash("Daily limit of 50 farmers has been reached.")
            return redirect(url_for("book"))

        booking_id=make_id("B")
        con=db()
        con.execute("""INSERT INTO bookings
            (booking_id,farmer_id,crop,quantity,booking_date,slot,created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (booking_id,farmer_id,crop,quantity,booking_date,slot,datetime.now().isoformat()))
        con.commit()
        con.close()

        return redirect(url_for("ticket", booking_id=booking_id))

    return render_template("book.html", today=str(date.today()))

@app.route("/ticket/<booking_id>")
def ticket(booking_id):
    con=db()
    b=con.execute("""SELECT b.*,f.name,f.phone,f.village
                     FROM bookings b JOIN farmers f ON b.farmer_id=f.farmer_id
                     WHERE b.booking_id=?""",(booking_id,)).fetchone()
    con.close()
    if not b:
        return "Booking not found",404
    return render_template("ticket.html", b=b)

@app.route("/dashboard")
def farmer_dashboard():
    if "farmer_id" not in session:
        return redirect(url_for("login"))
    con=db()
    f=con.execute("SELECT * FROM farmers WHERE farmer_id=?",(session["farmer_id"],)).fetchone()
    bookings=con.execute("SELECT * FROM bookings WHERE farmer_id=? ORDER BY id DESC",
                         (session["farmer_id"],)).fetchall()
    con.close()
    return render_template("dashboard.html", farmer=f, bookings=bookings)

# Demo admin login: /admin/login
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["username"]=="admin" and request.form["password"]=="admin123":
            session["admin"]=True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin login.")
    return render_template("admin_login.html")

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    con=db()
    bookings=con.execute("""SELECT b.*,f.name,f.phone,f.village
                            FROM bookings b JOIN farmers f ON b.farmer_id=f.farmer_id
                            ORDER BY b.booking_date,b.id""").fetchall()
    con.close()
    return render_template("admin.html", bookings=bookings)

@app.route("/admin/update/<booking_id>", methods=["POST"])
def update_booking(booking_id):
    if not session.get("admin"):
        return jsonify({"error":"Unauthorized"}),401
    status=request.form["status"]
    actual=request.form.get("actual_quantity")
    rate=request.form.get("rate")
    payment=request.form.get("payment_status")

    con=db()
    con.execute("""UPDATE bookings SET status=?,
                 actual_quantity=CASE WHEN ?='' THEN actual_quantity ELSE ? END,
                 rate=CASE WHEN ?='' THEN rate ELSE ? END,
                 payment_status=?
                 WHERE booking_id=?""",
                (status, actual or "", actual or None, rate or "", rate or None,
                 payment or "Pending", booking_id))
    con.commit()
    con.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin",None)
    return redirect(url_for("index"))

@app.route("/api/queue/<booking_id>")
def queue_api(booking_id):
    con=db()
    b=con.execute("SELECT * FROM bookings WHERE booking_id=?",(booking_id,)).fetchone()
    if not b:
        con.close()
        return jsonify({"error":"not found"}),404
    ahead=con.execute("""SELECT COUNT(*) c FROM bookings
                         WHERE booking_date=? AND id < ? AND status NOT IN ('Completed')""",
                      (b["booking_date"],b["id"])).fetchone()["c"]
    con.close()
    return jsonify({"booking_id":booking_id,"status":b["status"],"people_ahead":ahead})

@app.route("/weather")
def weather():
    return render_template("weather.html")

if __name__=="__main__":
    init_db()
    app.run(debug=True)
