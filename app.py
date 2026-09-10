from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3, secrets, hashlib, os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

TRANSLATIONS = {
    "en": {
        # Navigation
        "home": "Home",
        "register": "Register",
        "login": "Farmer Login",
        "book_slot": "Book Slot",
        "dashboard": "Dashboard",
        "weather": "Weather",
        "logout": "Logout",
        "admin": "Admin",
        "footer_text": "AgriQueue by AGROVISION",

        # Index / Hero
        "hero_title": "Smart Agricultural Procurement",
        "hero_description": "Register farmers, book procurement slots, manage queues and track payments.",
        "farmer_registration": "Farmer Registration",
        "admin_panel": "Admin Panel",
        "slot_booking": "Slot Booking",
        "slot_booking_desc": "Distribute farmers across available dates and time slots.",
        "queue_management": "Queue Management",
        "queue_management_desc": "Track Booked, Arrived, Weighing and Completed farmers.",
        "payment_tracking": "Payment Tracking",
        "payment_tracking_desc": "Store actual quantity, rate and payment status.",

        # Common form fields
        "name": "Name",
        "mobile_number": "Mobile Number",
        "village": "Village",
        "password": "Password",
        "submit": "Submit",
        "login_button": "Login",

        # Register page
        "welcome": "Welcome to AgriQueue",
        "subtitle": "Smart Farmer Procurement & Queue Management",
        "get_started": "Get Started",
        "learn_more": "Learn More",

        # Book page
        "book_procurement_slot": "Book Procurement Slot",
        "max_farmers_note": "Maximum 50 farmers are accepted per day in this prototype.",
        "crop": "Crop",
        "select_crop": "Select crop",
        "paddy": "Paddy",
        "wheat": "Wheat",
        "maize": "Maize",
        "other": "Other",
        "expected_quantity": "Expected Quantity (quintals)",
        "date": "Date",
        "time_slot": "Time Slot",
        "confirm_booking": "Confirm Booking",
        "quantity": "Quantity",
        "booking_date": "Booking Date",
        "slot": "Slot",
        "book": "Book",

        # Dashboard page
        "farmer_dashboard": "Farmer Dashboard",
        "farmer_id_label": "Farmer ID:",
        "name_label": "Name:",
        "mobile_label": "Mobile:",
        "book_new_slot": "Book New Slot",
        "my_bookings": "My Bookings",
        "token": "Token",
        "qty": "Qty",
        "payment": "Payment",
        "no_bookings": "No bookings yet.",
        "status": "Status",
        "payment_status": "Payment Status",

        # Ticket page
        "procurement_token": "Procurement Token",
        "farmer_label": "Farmer:",
        "village_label": "Village:",
        "crop_label": "Crop:",
        "expected_quantity_label": "Expected quantity:",
        "quintals": "quintals",
        "date_label": "Date:",
        "slot_label": "Slot:",
        "status_label": "Status:",
        "show_token_msg": "Show this token/QR at the procurement centre.",
        "go_to_dashboard": "Go to Dashboard",

        # Admin page
        "admin_procurement_dashboard": "Admin Procurement Dashboard",
        "admin_scan_msg": "Scan/search the farmer's token and update the procurement status.",
        "farmer_label_short": "Farmer",
        "phone": "Phone",
        "actual_qty": "Actual Qty",
        "rate": "Rate",
        "save": "Save",

        # Admin login page
        "admin_login": "Admin Login",
        "username": "Username",

        # Flash messages
        "flash_fill_fields": "Please fill all required fields.",
        "flash_already_registered": "This mobile number is already registered.",
        "flash_registration_success": "Registration successful. Your Farmer ID is {farmer_id}.",
        "flash_invalid_login": "Invalid mobile number or password.",
        "flash_choose_date": "Please choose today or a future date.",
        "flash_daily_limit": "Daily limit of 50 farmers has been reached.",
        "flash_invalid_admin": "Invalid admin login.",

        # Verify page
        "verify_title": "QR Verification",
        "booking_details": "Booking Details",
        "fetching_location": "📍 Fetching your location...",
        "location_captured": "📍 Location captured!",
        "location_unavailable": "⚠️ Location unavailable (will proceed without it)",
        "confirm_arrival_btn": "✅ Verify & Confirm Arrival",
        "verification_success": "✅ Verification Successful!",
        "sms_sent_to": "SMS notification sent to",
        "view_on_map": "📍 View on Google Maps",
        "already_arrived": "This farmer has already been verified as Arrived.",
        "back_to_admin": "Back to Admin Panel",

        # Scan page
        "scan_qr": "📷 Scan QR Code",
        "scan_instruction": "Point your camera at the farmer's QR code to verify their arrival.",
        "start_scanner": "Start Scanner",
        "stop_scanner": "Stop Scanner",

        # SMS logs
        "sms_logs": "SMS Logs",
        "sms_message": "Message",
        "sms_sent_at": "Sent At",
        "sms_location": "Location",
        "no_sms_logs": "No SMS logs yet.",
        "view_sms_logs": "📩 SMS Logs",
    },

    "hi": {
        # Navigation
        "home": "होम",
        "register": "पंजीकरण",
        "login": "किसान लॉगिन",
        "book_slot": "स्लॉट बुक करें",
        "dashboard": "डैशबोर्ड",
        "weather": "मौसम",
        "logout": "लॉगआउट",
        "admin": "एडमिन",
        "footer_text": "AgriQueue द्वारा AGROVISION",

        # Index / Hero
        "hero_title": "स्मार्ट कृषि खरीद",
        "hero_description": "किसानों का पंजीकरण करें, खरीद स्लॉट बुक करें, कतार प्रबंधित करें और भुगतान ट्रैक करें।",
        "farmer_registration": "किसान पंजीकरण",
        "admin_panel": "एडमिन पैनल",
        "slot_booking": "स्लॉट बुकिंग",
        "slot_booking_desc": "किसानों को उपलब्ध तिथियों और समय स्लॉट में वितरित करें।",
        "queue_management": "कतार प्रबंधन",
        "queue_management_desc": "बुक किए गए, आए हुए, तौल और पूर्ण किसानों को ट्रैक करें।",
        "payment_tracking": "भुगतान ट्रैकिंग",
        "payment_tracking_desc": "वास्तविक मात्रा, दर और भुगतान स्थिति संग्रहीत करें।",

        # Common form fields
        "name": "नाम",
        "mobile_number": "मोबाइल नंबर",
        "village": "गांव",
        "password": "पासवर्ड",
        "submit": "सबमिट करें",
        "login_button": "लॉगिन",

        # Register page
        "welcome": "AgriQueue में आपका स्वागत है",
        "subtitle": "स्मार्ट किसान खरीद और कतार प्रबंधन",
        "get_started": "शुरू करें",
        "learn_more": "और जानें",

        # Book page
        "book_procurement_slot": "खरीद स्लॉट बुक करें",
        "max_farmers_note": "इस प्रोटोटाइप में प्रतिदिन अधिकतम 50 किसान स्वीकार किए जाते हैं।",
        "crop": "फसल",
        "select_crop": "फसल चुनें",
        "paddy": "धान",
        "wheat": "गेहूँ",
        "maize": "मक्का",
        "other": "अन्य",
        "expected_quantity": "अपेक्षित मात्रा (क्विंटल)",
        "date": "तारीख",
        "time_slot": "समय स्लॉट",
        "confirm_booking": "बुकिंग पक्की करें",
        "quantity": "मात्रा",
        "booking_date": "बुकिंग की तारीख",
        "slot": "स्लॉट",
        "book": "बुक करें",

        # Dashboard page
        "farmer_dashboard": "किसान डैशबोर्ड",
        "farmer_id_label": "किसान आईडी:",
        "name_label": "नाम:",
        "mobile_label": "मोबाइल:",
        "book_new_slot": "नया स्लॉट बुक करें",
        "my_bookings": "मेरी बुकिंग",
        "token": "टोकन",
        "qty": "मात्रा",
        "payment": "भुगतान",
        "no_bookings": "अभी तक कोई बुकिंग नहीं।",
        "status": "स्थिति",
        "payment_status": "भुगतान स्थिति",

        # Ticket page
        "procurement_token": "खरीद टोकन",
        "farmer_label": "किसान:",
        "village_label": "गांव:",
        "crop_label": "फसल:",
        "expected_quantity_label": "अपेक्षित मात्रा:",
        "quintals": "क्विंटल",
        "date_label": "तारीख:",
        "slot_label": "स्लॉट:",
        "status_label": "स्थिति:",
        "show_token_msg": "इस टोकन/QR को खरीद केंद्र पर दिखाएं।",
        "go_to_dashboard": "डैशबोर्ड पर जाएं",

        # Admin page
        "admin_procurement_dashboard": "एडमिन खरीद डैशबोर्ड",
        "admin_scan_msg": "किसान का टोकन स्कैन/खोजें और खरीद स्थिति अपडेट करें।",
        "farmer_label_short": "किसान",
        "phone": "फ़ोन",
        "actual_qty": "वास्तविक मात्रा",
        "rate": "दर",
        "save": "सेव करें",

        # Admin login page
        "admin_login": "एडमिन लॉगिन",
        "username": "उपयोगकर्ता नाम",

        # Flash messages
        "flash_fill_fields": "कृपया सभी आवश्यक फ़ील्ड भरें।",
        "flash_already_registered": "यह मोबाइल नंबर पहले से पंजीकृत है।",
        "flash_registration_success": "पंजीकरण सफल। आपकी किसान आईडी {farmer_id} है।",
        "flash_invalid_login": "अमान्य मोबाइल नंबर या पासवर्ड।",
        "flash_choose_date": "कृपया आज या भविष्य की तारीख चुनें।",
        "flash_daily_limit": "50 किसानों की दैनिक सीमा पूरी हो चुकी है।",
        "flash_invalid_admin": "अमान्य एडमिन लॉगिन।",

        # Verify page
        "verify_title": "QR सत्यापन",
        "booking_details": "बुकिंग विवरण",
        "fetching_location": "📍 आपका स्थान प्राप्त कर रहे हैं...",
        "location_captured": "📍 स्थान प्राप्त हुआ!",
        "location_unavailable": "⚠️ स्थान उपलब्ध नहीं (बिना इसके आगे बढ़ेंगे)",
        "confirm_arrival_btn": "✅ सत्यापित करें और आगमन की पुष्टि करें",
        "verification_success": "✅ सत्यापन सफल!",
        "sms_sent_to": "SMS सूचना भेजी गई",
        "view_on_map": "📍 Google Maps पर देखें",
        "already_arrived": "इस किसान का आगमन पहले ही सत्यापित हो चुका है।",
        "back_to_admin": "एडमिन पैनल पर वापस जाएं",

        # Scan page
        "scan_qr": "📷 QR कोड स्कैन करें",
        "scan_instruction": "किसान के QR कोड पर कैमरा दिखाएं।",
        "start_scanner": "स्कैनर शुरू करें",
        "stop_scanner": "स्कैनर बंद करें",

        # SMS logs
        "sms_logs": "SMS लॉग",
        "sms_message": "संदेश",
        "sms_sent_at": "भेजा गया",
        "sms_location": "स्थान",
        "no_sms_logs": "अभी तक कोई SMS लॉग नहीं।",
        "view_sms_logs": "📩 SMS लॉग",
    },

    "bn": {
        # Navigation
        "home": "হোম",
        "register": "নিবন্ধন",
        "login": "কৃষক লগইন",
        "book_slot": "স্লট বুক করুন",
        "dashboard": "ড্যাশবোর্ড",
        "weather": "আবহাওয়া",
        "logout": "লগআউট",
        "admin": "অ্যাডমিন",
        "footer_text": "AgriQueue by AGROVISION",

        # Index / Hero
        "hero_title": "স্মার্ট কৃষি সংগ্রহ",
        "hero_description": "কৃষকদের নিবন্ধন করুন, সংগ্রহ স্লট বুক করুন, কিউ পরিচালনা করুন এবং পেমেন্ট ট্র্যাক করুন।",
        "farmer_registration": "কৃষক নিবন্ধন",
        "admin_panel": "অ্যাডমিন প্যানেল",
        "slot_booking": "স্লট বুকিং",
        "slot_booking_desc": "কৃষকদের উপলব্ধ তারিখ এবং সময় স্লটে বিতরণ করুন।",
        "queue_management": "কিউ ব্যবস্থাপনা",
        "queue_management_desc": "বুক করা, আগত, ওজন এবং সম্পন্ন কৃষকদের ট্র্যাক করুন।",
        "payment_tracking": "পেমেন্ট ট্র্যাকিং",
        "payment_tracking_desc": "প্রকৃত পরিমাণ, দর এবং পেমেন্ট স্ট্যাটাস সংরক্ষণ করুন।",

        # Common form fields
        "name": "নাম",
        "mobile_number": "মোবাইল নম্বর",
        "village": "গ্রাম",
        "password": "পাসওয়ার্ড",
        "submit": "জমা দিন",
        "login_button": "লগইন",

        # Register page
        "welcome": "AgriQueue-তে স্বাগতম",
        "subtitle": "স্মার্ট কৃষক সংগ্রহ ও কিউ ব্যবস্থাপনা",
        "get_started": "শুরু করুন",
        "learn_more": "আরও জানুন",

        # Book page
        "book_procurement_slot": "সংগ্রহ স্লট বুক করুন",
        "max_farmers_note": "এই প্রোটোটাইপে প্রতিদিন সর্বোচ্চ ৫০ জন কৃষক গ্রহণ করা হয়।",
        "crop": "ফসল",
        "select_crop": "ফসল নির্বাচন করুন",
        "paddy": "ধান",
        "wheat": "গম",
        "maize": "ভুট্টা",
        "other": "অন্যান্য",
        "expected_quantity": "প্রত্যাশিত পরিমাণ (কুইন্টাল)",
        "date": "তারিখ",
        "time_slot": "সময় স্লট",
        "confirm_booking": "বুকিং নিশ্চিত করুন",
        "quantity": "পরিমাণ",
        "booking_date": "বুকিংয়ের তারিখ",
        "slot": "স্লট",
        "book": "বুক করুন",

        # Dashboard page
        "farmer_dashboard": "কৃষক ড্যাশবোর্ড",
        "farmer_id_label": "কৃষক আইডি:",
        "name_label": "নাম:",
        "mobile_label": "মোবাইল:",
        "book_new_slot": "নতুন স্লট বুক করুন",
        "my_bookings": "আমার বুকিং",
        "token": "টোকেন",
        "qty": "পরিমাণ",
        "payment": "পেমেন্ট",
        "no_bookings": "এখনও কোনো বুকিং নেই।",
        "status": "স্ট্যাটাস",
        "payment_status": "পেমেন্ট স্ট্যাটাস",

        # Ticket page
        "procurement_token": "সংগ্রহ টোকেন",
        "farmer_label": "কৃষক:",
        "village_label": "গ্রাম:",
        "crop_label": "ফসল:",
        "expected_quantity_label": "প্রত্যাশিত পরিমাণ:",
        "quintals": "কুইন্টাল",
        "date_label": "তারিখ:",
        "slot_label": "স্লট:",
        "status_label": "স্ট্যাটাস:",
        "show_token_msg": "সংগ্রহ কেন্দ্রে এই টোকেন/QR দেখান।",
        "go_to_dashboard": "ড্যাশবোর্ডে যান",

        # Admin page
        "admin_procurement_dashboard": "অ্যাডমিন সংগ্রহ ড্যাশবোর্ড",
        "admin_scan_msg": "কৃষকের টোকেন স্ক্যান/খুঁজুন এবং সংগ্রহ স্ট্যাটাস আপডেট করুন।",
        "farmer_label_short": "কৃষক",
        "phone": "ফোন",
        "actual_qty": "প্রকৃত পরিমাণ",
        "rate": "দর",
        "save": "সেভ করুন",

        # Admin login page
        "admin_login": "অ্যাডমিন লগইন",
        "username": "ইউজারনেম",

        # Flash messages
        "flash_fill_fields": "অনুগ্রহ করে সমস্ত প্রয়োজনীয় ক্ষেত্র পূরণ করুন।",
        "flash_already_registered": "এই মোবাইল নম্বরটি ইতিমধ্যে নিবন্ধিত।",
        "flash_registration_success": "নিবন্ধন সফল। আপনার কৃষক আইডি {farmer_id}।",
        "flash_invalid_login": "অবৈধ মোবাইল নম্বর বা পাসওয়ার্ড।",
        "flash_choose_date": "অনুগ্রহ করে আজ বা ভবিষ্যতের তারিখ নির্বাচন করুন।",
        "flash_daily_limit": "৫০ জন কৃষকের দৈনিক সীমা পূর্ণ হয়েছে।",
        "flash_invalid_admin": "অবৈধ অ্যাডমিন লগইন।",

        # Verify page
        "verify_title": "QR যাচাইকরণ",
        "booking_details": "বুকিং বিবরণ",
        "fetching_location": "📍 আপনার অবস্থান সংগ্রহ করা হচ্ছে...",
        "location_captured": "📍 অবস্থান সংগৃহীত!",
        "location_unavailable": "⚠️ অবস্থান অনুপলব্ধ (এটি ছাড়াই এগিয়ে যাবে)",
        "confirm_arrival_btn": "✅ যাচাই করুন ও আগমন নিশ্চিত করুন",
        "verification_success": "✅ যাচাইকরণ সফল!",
        "sms_sent_to": "SMS বিজ্ঞপ্তি পাঠানো হয়েছে",
        "view_on_map": "📍 Google Maps-এ দেখুন",
        "already_arrived": "এই কৃষকের আগমন ইতিমধ্যে যাচাই করা হয়েছে।",
        "back_to_admin": "অ্যাডমিন প্যানেলে ফিরে যান",

        # Scan page
        "scan_qr": "📷 QR কোড স্ক্যান করুন",
        "scan_instruction": "কৃষকের QR কোডে ক্যামেরা দেখান।",
        "start_scanner": "স্ক্যানার শুরু করুন",
        "stop_scanner": "স্ক্যানার বন্ধ করুন",

        # SMS logs
        "sms_logs": "SMS লগ",
        "sms_message": "বার্তা",
        "sms_sent_at": "পাঠানো হয়েছে",
        "sms_location": "অবস্থান",
        "no_sms_logs": "এখনও কোনো SMS লগ নেই।",
        "view_sms_logs": "📩 SMS লগ",
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

def get_t():
    """Get translation dict for current language (for use in route handlers)."""
    lang = session.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])

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
        verified_lat TEXT,
        verified_lng TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sms_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT,
        phone TEXT NOT NULL,
        message TEXT NOT NULL,
        latitude TEXT,
        longitude TEXT,
        sent_at TEXT NOT NULL
    );
    """)
    # Add verified_lat/lng columns if they don't exist (for existing databases)
    try:
        con.execute("ALTER TABLE bookings ADD COLUMN verified_lat TEXT")
    except:
        pass
    try:
        con.execute("ALTER TABLE bookings ADD COLUMN verified_lng TEXT")
    except:
        pass
    con.commit()
    con.close()

def send_sms(phone, message, booking_id=None, lat=None, lng=None):
    """Send SMS via Twilio if configured, otherwise simulate (log to console + DB)."""
    # Always log to database
    con = db()
    con.execute(
        "INSERT INTO sms_logs (booking_id, phone, message, latitude, longitude, sent_at) VALUES (?,?,?,?,?,?)",
        (booking_id, phone, message, lat, lng, datetime.now().isoformat())
    )
    con.commit()
    con.close()

    # Try Twilio if credentials are set
    twilio_sid = os.environ.get("TWILIO_SID")
    twilio_token = os.environ.get("TWILIO_TOKEN")
    twilio_from = os.environ.get("TWILIO_FROM")

    if twilio_sid and twilio_token and twilio_from:
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            client.messages.create(body=message, from_=twilio_from, to=f"+91{phone}")
            print(f"[SMS SENT via Twilio] To: +91{phone}")
            return True
        except Exception as e:
            print(f"[SMS ERROR - Twilio] {e}")
            return False
    else:
        # Simulation mode — print to console
        print(f"\n{'='*55}")
        print(f"  📩 SMS SIMULATION (set TWILIO env vars for real SMS)")
        print(f"  To:      +91{phone}")
        print(f"  Message: {message}")
        print(f"{'='*55}\n")
        return True

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
            flash(get_t()["flash_fill_fields"])
            return redirect(url_for("register"))

        con=db()
        existing=con.execute("SELECT * FROM farmers WHERE phone=?", (phone,)).fetchone()
        if existing:
            con.close()
            flash(get_t()["flash_already_registered"])
            return redirect(url_for("register"))

        farmer_id=make_id("F")
        con.execute("""INSERT INTO farmers
            (farmer_id,name,phone,village,password_hash,created_at)
            VALUES (?,?,?,?,?,?)""",
            (farmer_id,name,phone,village,hash_pw(password),datetime.now().isoformat()))
        con.commit()
        con.close()

        session["farmer_id"]=farmer_id
        flash(get_t()["flash_registration_success"].format(farmer_id=farmer_id))
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
         flash(get_t()["flash_invalid_login"])
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
            flash(get_t()["flash_choose_date"])
            return redirect(url_for("book"))

        if today_count(booking_date) >= DAILY_LIMIT:
            flash(get_t()["flash_daily_limit"])
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
    verify_url = request.host_url.rstrip("/") + url_for("verify", booking_id=booking_id)
    return render_template("ticket.html", b=b, verify_url=verify_url)

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
        flash(get_t()["flash_invalid_admin"])
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

# ─── QR VERIFICATION + SMS ───────────────────────────────

@app.route("/verify/<booking_id>", methods=["GET","POST"])
def verify(booking_id):
    con=db()
    b=con.execute("""SELECT b.*,f.name,f.phone,f.village
                     FROM bookings b JOIN farmers f ON b.farmer_id=f.farmer_id
                     WHERE b.booking_id=?""",(booking_id,)).fetchone()
    if not b:
        con.close()
        return "Booking not found",404

    if request.method=="POST":
        lat=request.form.get("latitude","")
        lng=request.form.get("longitude","")

        # Update booking status and store verified location
        con.execute("""UPDATE bookings SET status='Arrived',
                      verified_lat=?, verified_lng=? WHERE booking_id=?""",
                    (lat or None, lng or None, booking_id))
        con.commit()

        # Build SMS message
        maps_link=""
        if lat and lng:
            maps_link=f"https://maps.google.com/?q={lat},{lng}"

        sms_text=(
            f"AgriQueue: Dear {b['name']}, your arrival at the procurement center "
            f"has been confirmed.\n"
            f"Token: {booking_id}\n"
            f"Date: {b['booking_date']}\n"
            f"Slot: {b['slot']}"
        )
        if maps_link:
            sms_text+=f"\nCenter Location: {maps_link}"

        send_sms(b["phone"], sms_text, booking_id=booking_id, lat=lat, lng=lng)
        con.close()

        return render_template("verify.html", b=b, verified=True,
                             lat=lat, lng=lng, maps_link=maps_link)

    con.close()
    already = b["status"] in ("Arrived","Waiting","Weighing","Procurement","Completed")
    return render_template("verify.html", b=b, verified=False, already=already)

@app.route("/admin/scan")
def admin_scan():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    return render_template("scan.html")

@app.route("/admin/sms-logs")
def admin_sms_logs():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    con=db()
    logs=con.execute("SELECT * FROM sms_logs ORDER BY id DESC").fetchall()
    con.close()
    return render_template("sms_logs.html", logs=logs)

if __name__=="__main__":
    init_db()
    app.run(debug=True)
