# AgriQueue - Beginner Free Version

A simple agricultural procurement registration, slot booking, queue and payment tracking project.

## 1. Install Python
Install Python 3.11+ from python.org.
During installation on Windows, tick **Add Python to PATH**.

## 2. Open the project
Extract this folder. Open it in VS Code.

## 3. Open VS Code terminal
Use:
Terminal -> New Terminal

## 4. Create a virtual environment
Windows:
    py -m venv venv
    venv\Scripts\activate

If `py` does not work:
    python -m venv venv
    venv\Scripts\activate

## 5. Install Flask
    pip install -r requirements.txt

## 6. Run
    python app.py

You should see a local address such as:
    http://127.0.0.1:5000

Open that address in Chrome.

## 7. Farmer flow
Home -> Register -> Book Slot -> Ticket -> Login -> Dashboard

## 8. Admin flow
Open:
    http://127.0.0.1:5000/admin/login

Demo credentials:
    Username: admin
    Password: admin123

IMPORTANT: Change the admin password before real deployment.

## 9. Database
The first run creates:
    agriqueue.db

It is SQLite, so there is no separate database server and no database cost.

## 10. Free version limitations
This starter project uses browser/web notifications through the dashboard only.
Real SMS/WhatsApp messages normally require an external messaging service and may not remain completely free.
QR display is implemented using a free client-side QR library loaded from CDN.

## 11. Before real-world deployment
Add:
- HTTPS
- strong admin authentication
- OTP verification
- proper QR scanner
- role-based admin accounts
- audit logs
- data backups
- privacy/security controls
- real SMS provider if required
- production database if scale grows
