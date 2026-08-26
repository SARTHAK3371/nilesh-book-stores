Nilesh Book Store - Professional Authentication Upgrade

1. Install: pip install -r requirements.txt
2. Optional: set SECRET_KEY, ADMIN_EMAIL and ADMIN_PASSWORD as environment variables.
3. Run: python app.py
4. Open: http://127.0.0.1:5000

Customer pages require login. Registration creates a SQLite customer record and hashes passwords.
Admin: /admin/login -> /admin/customers
Default development admin credentials are defined only as fallback in app.py; change them before deployment.
