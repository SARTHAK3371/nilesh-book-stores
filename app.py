import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")

DATABASE = "nilesh_book_store.db"

# --------------------------------------------------
# SAMPLE BOOK DATA - PRESERVED FROM YOUR PROJECT
# --------------------------------------------------
books = [
    {"id": 1, "title": "Python Programming", "author": "Mark Lutz", "price": 699,
     "image": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600"},
    {"id": 2, "title": "Clean Code", "author": "Robert C. Martin", "price": 499,
     "image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600"},
    {"id": 3, "title": "Atomic Habits", "author": "James Clear", "price": 550,
     "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600"},
    {"id": 4, "title": "The Alchemist", "author": "Paulo Coelho", "price": 299,
     "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600"},
    {"id": 5, "title": "Rich Dad Poor Dad", "author": "Robert Kiyosaki", "price": 350,
     "image": "https://images.unsplash.com/photo-1589998059171-988d887df646?w=600"},
    {"id": 6, "title": "Computer Networks", "author": "Andrew S. Tanenbaum", "price": 750,
     "image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600"},
]

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mobile TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            last_login TEXT,
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)
    conn.commit()
    conn.close()

# --------------------------------------------------
# AUTH HELPERS
# --------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "customer_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped

# --------------------------------------------------
# COMMON CSS
# --------------------------------------------------
style = r"""
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Inter,Arial,sans-serif}
body{background:#f5f7fb;color:#172033}
a{text-decoration:none}
.navbar{background:#101828;color:#fff;padding:16px 6%;display:flex;align-items:center;justify-content:space-between;gap:20px;position:sticky;top:0;z-index:50}
.logo{font-size:23px;font-weight:800}
.navbar nav{display:flex;gap:20px;align-items:center;flex-wrap:wrap}
.navbar nav a{color:#dbe3ef;font-size:14px}
.navbar nav a:hover{color:#fff}
.user-pill{background:#ffffff14;border:1px solid #ffffff22;padding:8px 12px;border-radius:999px;color:#fff;font-size:13px}

.auth-page{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:30px 16px;
background:radial-gradient(circle at top left,#635bff55,transparent 35%),linear-gradient(135deg,#0b1020,#1e1b4b 55%,#312e81)}
.auth-card{width:100%;max-width:1100px;min-height:650px;display:grid;grid-template-columns:1.05fr .95fr;background:#fff;border-radius:28px;overflow:hidden;box-shadow:0 30px 80px #0008}
.auth-brand{padding:55px;background:linear-gradient(145deg,#111827,#312e81 55%,#7c3aed);color:#fff;display:flex;flex-direction:column;justify-content:center}
.brand-badge{display:inline-flex;width:max-content;padding:8px 12px;border:1px solid #ffffff35;background:#ffffff14;border-radius:999px;font-size:13px;margin-bottom:22px}
.auth-brand h1{font-size:46px;line-height:1.08;margin-bottom:18px}
.auth-brand p{color:#e5e7eb;line-height:1.7;max-width:470px}
.feature-list{display:grid;gap:12px;margin-top:30px}
.feature{display:flex;gap:10px;align-items:center;color:#f8fafc}
.book-mini{display:flex;gap:10px;margin-top:30px}
.book-mini img{width:68px;height:92px;object-fit:cover;border-radius:9px;box-shadow:0 8px 20px #0005}

.auth-form{padding:55px 52px;display:flex;flex-direction:column;justify-content:center}
.auth-form h2{font-size:32px;color:#111827;margin-bottom:8px}
.auth-sub{color:#667085;margin-bottom:28px}
.input-group{margin-bottom:17px}
.input-group label{display:block;font-size:13px;font-weight:700;color:#344054;margin-bottom:7px}
.input-group input{width:100%;padding:14px 15px;border:1px solid #d0d5dd;border-radius:11px;font-size:15px;outline:none;background:#fff}
.input-group input:focus{border-color:#635bff;box-shadow:0 0 0 4px #635bff18}
.auth-btn{width:100%;border:0;border-radius:11px;padding:14px;background:linear-gradient(90deg,#4f46e5,#7c3aed);color:#fff;font-size:16px;font-weight:800;cursor:pointer;margin-top:5px}
.auth-btn:hover{filter:brightness(1.06);transform:translateY(-1px)}
.auth-switch{text-align:center;margin-top:20px;color:#667085;font-size:14px}
.auth-switch a{color:#5b21b6;font-weight:800}
.alert{padding:12px 14px;border-radius:10px;margin-bottom:18px;font-size:14px}
.alert-error{background:#fef3f2;color:#b42318;border:1px solid #fecdca}
.alert-success{background:#ecfdf3;color:#027a48;border:1px solid #abefc6}

.hero{min-height:430px;padding:70px 8%;display:flex;align-items:center;color:#fff;background:linear-gradient(90deg,#101828ee,#4f46e5bb),url("https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1600") center/cover}
.hero h1{font-size:52px;margin-bottom:14px}
.hero p{font-size:19px;margin-bottom:24px}
.btn{display:inline-block;border:0;padding:12px 20px;border-radius:9px;background:#e11d48;color:#fff;font-weight:800;cursor:pointer}
.container{padding:45px 7%}
.title{text-align:center;margin-bottom:30px;color:#312e81}
.book-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:25px}
.book-card{background:#fff;border-radius:15px;overflow:hidden;box-shadow:0 6px 25px #00000012}
.book-card img{width:100%;height:270px;object-fit:cover}
.book-info{padding:18px}.book-info h3{margin-bottom:7px}.author{color:#667085}.price{color:#e11d48;font-size:20px;font-weight:800;margin:10px 0}
footer{background:#101828;color:#fff;text-align:center;padding:28px}

.dashboard{padding:40px 7%}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:25px 0}
.stat{background:#fff;padding:22px;border-radius:15px;box-shadow:0 5px 20px #00000010}
.stat small{color:#667085}.stat strong{display:block;font-size:27px;margin-top:7px}
.table-wrap{background:#fff;border-radius:15px;overflow:auto;box-shadow:0 5px 20px #00000010}
table{width:100%;border-collapse:collapse;min-width:850px}
th,td{text-align:left;padding:15px;border-bottom:1px solid #eaecf0;font-size:14px}
th{background:#f8fafc;color:#344054}
.badge{display:inline-block;padding:5px 9px;border-radius:999px;background:#ecfdf3;color:#027a48;font-size:12px;font-weight:800}
.profile{max-width:750px;margin:45px auto;background:#fff;padding:30px;border-radius:18px;box-shadow:0 8px 30px #00000012}
.profile-row{display:flex;justify-content:space-between;gap:20px;padding:15px 0;border-bottom:1px solid #eaecf0}
.profile-row span:first-child{color:#667085}.profile-row span:last-child{font-weight:700}

@media(max-width:800px){
.auth-card{grid-template-columns:1fr}.auth-brand{padding:35px 25px}.auth-form{padding:35px 25px}.auth-brand h1{font-size:35px}.stats{grid-template-columns:1fr}.navbar{flex-direction:column}.hero h1{font-size:36px}
}
</style>
"""

# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------
LOGIN_PAGE = """
<!doctype html><html><head><title>Login | Nilesh Book Store</title>{{style|safe}}</head>
<body>
<div class="auth-page">
<div class="auth-card">
<section class="auth-brand">
<div class="brand-badge">📚 NILESH BOOK STORE</div>
<h1>Welcome back.</h1>
<p>Sign in securely to discover books, manage your account and continue your reading journey.</p>
<div class="feature-list">
<div class="feature">✓ Secure customer account</div>
<div class="feature">✓ Personal profile & order history</div>
<div class="feature">✓ Mobile-friendly shopping experience</div>
</div>
<div class="book-mini">
{% for book in books[:4] %}<img src="{{book.image}}" alt="{{book.title}}">{% endfor %}
</div>
</section>
<section class="auth-form">
<h2>Sign in</h2>
<p class="auth-sub">Enter your account details to continue.</p>
{% with messages = get_flashed_messages(with_categories=true) %}
{% for category, message in messages %}<div class="alert alert-{{category}}">{{message}}</div>{% endfor %}
{% endwith %}
{% if error %}<div class="alert alert-error">{{error}}</div>{% endif %}
<form method="POST">
<div class="input-group"><label>Email address</label><input type="email" name="email" placeholder="you@example.com" required></div>
<div class="input-group"><label>Password</label><input type="password" name="password" placeholder="Enter your password" required></div>
<button class="auth-btn" type="submit">🔐 Sign In</button>
</form>
<div class="auth-switch">New customer? <a href="{{url_for('register')}}">Create a new account</a></div>
<div class="auth-switch"><a href="{{url_for('admin_login')}}">Admin login</a></div>
</section>
</div>
</div>
</body></html>
"""

# --------------------------------------------------
# REGISTER PAGE
# --------------------------------------------------
REGISTER_PAGE = """
<!doctype html><html><head><title>Create Account | Nilesh Book Store</title>{{style|safe}}</head>
<body>
<div class="auth-page">
<div class="auth-card">
<section class="auth-brand">
<div class="brand-badge">✨ JOIN NILESH BOOK STORE</div>
<h1>Create your account.</h1>
<p>Register once and get your own secure customer account for the Nilesh Book Store.</p>
<div class="feature-list">
<div class="feature">✓ Your details saved securely</div>
<div class="feature">✓ Password stored as a secure hash</div>
<div class="feature">✓ Ready for future SMS OTP verification</div>
</div>
</section>
<section class="auth-form">
<h2>Create account</h2>
<p class="auth-sub">Fill in your details to get started.</p>
{% with messages = get_flashed_messages(with_categories=true) %}
{% for category, message in messages %}<div class="alert alert-{{category}}">{{message}}</div>{% endfor %}
{% endwith %}
<form method="POST">
<div class="input-group"><label>Full name</label><input name="name" placeholder="Enter your full name" required></div>
<div class="input-group"><label>Email address</label><input type="email" name="email" placeholder="you@example.com" required></div>
<div class="input-group"><label>Mobile number</label><input name="mobile" inputmode="numeric" pattern="[0-9]{10}" maxlength="10" placeholder="10-digit mobile number" required></div>
<div class="input-group"><label>Password</label><input type="password" name="password" minlength="8" placeholder="Minimum 8 characters" required></div>
<button class="auth-btn" type="submit">Create Account →</button>
</form>
<div class="auth-switch">Already registered? <a href="{{url_for('login')}}">Sign in</a></div>
</section>
</div>
</div>
</body></html>
"""

# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------
ADMIN_LOGIN_PAGE = """
<!doctype html><html><head><title>Admin Login | Nilesh Book Store</title>{{style|safe}}</head>
<body>
<div class="auth-page">
<div class="auth-card">
<section class="auth-brand">
<div class="brand-badge">🛡️ ADMIN PORTAL</div>
<h1>Store control center.</h1>
<p>Authorized administrators can view registered customer details and manage the store.</p>
</section>
<section class="auth-form">
<h2>Admin sign in</h2>
<p class="auth-sub">Authorized access only.</p>
{% if error %}<div class="alert alert-error">{{error}}</div>{% endif %}
<form method="POST">
<div class="input-group"><label>Admin email</label><input type="email" name="email" required></div>
<div class="input-group"><label>Admin password</label><input type="password" name="password" required></div>
<button class="auth-btn" type="submit">🛡️ Admin Login</button>
</form>
<div class="auth-switch"><a href="{{url_for('login')}}">← Customer login</a></div>
</section>
</div>
</div>
</body></html>
"""

# --------------------------------------------------
# HOME / BOOKS
# --------------------------------------------------
HOME_PAGE = """
<!doctype html><html><head><title>Nilesh Book Store</title>{{style|safe}}</head><body>
<div class="navbar"><div class="logo">📚 Nilesh Book Store</div>
<nav><a href="{{url_for('home')}}">Home</a><a href="{{url_for('book_page')}}">Books</a><a href="{{url_for('profile')}}">My Profile</a><span class="user-pill">Hi, {{customer.full_name}}</span><a href="{{url_for('logout')}}">Logout</a></nav></div>
<section class="hero"><div><h1>Read. Learn. Grow.</h1><p>Discover books that inspire your next chapter.</p><a class="btn" href="{{url_for('book_page')}}">Explore Books 📚</a></div></section>
<div class="container"><h2 class="title">Popular Books</h2><div class="book-grid">
{% for book in books %}<div class="book-card"><img src="{{book.image}}"><div class="book-info"><h3>{{book.title}}</h3><p class="author">{{book.author}}</p><p class="price">₹{{book.price}}</p><button class="btn" onclick="alert('Book added to cart!')">Add to Cart</button></div></div>{% endfor %}
</div></div><footer>Nilesh Book Store © 2026</footer></body></html>
"""

BOOKS_PAGE = """
<!doctype html><html><head><title>Books | Nilesh Book Store</title>{{style|safe}}</head><body>
<div class="navbar"><div class="logo">📚 Nilesh Book Store</div><nav><a href="{{url_for('home')}}">Home</a><a href="{{url_for('book_page')}}">Books</a><a href="{{url_for('profile')}}">My Profile</a><span class="user-pill">{{customer.full_name}}</span><a href="{{url_for('logout')}}">Logout</a></nav></div>
<div class="container"><h1 class="title">📚 All Books</h1><div class="book-grid">
{% for book in books %}<div class="book-card"><img src="{{book.image}}"><div class="book-info"><h3>{{book.title}}</h3><p class="author">{{book.author}}</p><p class="price">₹{{book.price}}</p><button class="btn" onclick="alert('Added {{book.title}} to cart!')">Add to Cart</button></div></div>{% endfor %}
</div></div><footer>Nilesh Book Store © 2026</footer></body></html>
"""

PROFILE_PAGE = """
<!doctype html><html><head><title>My Profile | Nilesh Book Store</title>{{style|safe}}</head><body>
<div class="navbar"><div class="logo">📚 Nilesh Book Store</div><nav><a href="{{url_for('home')}}">Home</a><a href="{{url_for('book_page')}}">Books</a><a href="{{url_for('profile')}}">My Profile</a><a href="{{url_for('logout')}}">Logout</a></nav></div>
<div class="profile"><h2>👤 My Customer Profile</h2><div class="profile-row"><span>Customer ID</span><span>#{{customer.id}}</span></div><div class="profile-row"><span>Full Name</span><span>{{customer.full_name}}</span></div><div class="profile-row"><span>Email</span><span>{{customer.email}}</span></div><div class="profile-row"><span>Mobile</span><span>{{customer.mobile}}</span></div><div class="profile-row"><span>Registration Date</span><span>{{customer.registration_date}}</span></div><div class="profile-row"><span>Last Login</span><span>{{customer.last_login or 'First login'}}</span></div><div class="profile-row"><span>Status</span><span class="badge">{{customer.status}}</span></div></div>
<footer>Nilesh Book Store © 2026</footer></body></html>
"""

ADMIN_CUSTOMERS_PAGE = """
<!doctype html><html><head><title>Customers | Admin</title>{{style|safe}}</head><body>
<div class="navbar"><div class="logo">🛡️ Nilesh Admin</div><nav><a href="{{url_for('admin_customers')}}">Customers</a><a href="{{url_for('admin_logout')}}">Logout</a></nav></div>
<div class="dashboard"><h1>Customer Management</h1><p style="color:#667085;margin-top:8px">Registered Nilesh Book Store customers</p>
<div class="stats"><div class="stat"><small>Total Customers</small><strong>{{customers|length}}</strong></div><div class="stat"><small>Active Accounts</small><strong>{{active_count}}</strong></div><div class="stat"><small>Store</small><strong>Nilesh Book Store</strong></div></div>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Full Name</th><th>Email</th><th>Mobile</th><th>Registered</th><th>Last Login</th><th>Status</th></tr></thead><tbody>
{% for c in customers %}<tr><td>#{{c.id}}</td><td>{{c.full_name}}</td><td>{{c.email}}</td><td>{{c.mobile}}</td><td>{{c.registration_date}}</td><td>{{c.last_login or 'Never'}}</td><td><span class="badge">{{c.status}}</span></td></tr>{% else %}<tr><td colspan="7">No customers registered yet.</td></tr>{% endfor %}
</tbody></table></div></div>
</body></html>
"""

# --------------------------------------------------
# CUSTOMER ROUTES
# --------------------------------------------------
@app.route("/")
@login_required
def home():
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id=?", (session["customer_id"],)).fetchone()
    conn.close()
    return render_template_string(HOME_PAGE, style=style, books=books, customer=customer)

@app.route("/books")
@login_required
def book_page():
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id=?", (session["customer_id"],)).fetchone()
    conn.close()
    return render_template_string(BOOKS_PAGE, style=style, books=books, customer=customer)

@app.route("/profile")
@login_required
def profile():
    conn = get_db()
    customer = conn.execute("SELECT * FROM customers WHERE id=?", (session["customer_id"],)).fetchone()
    conn.close()
    return render_template_string(PROFILE_PAGE, style=style, customer=customer)

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("customer_id"):
        return redirect(url_for("home"))
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        customer = conn.execute("SELECT * FROM customers WHERE email=?", (email,)).fetchone()
        if customer and customer["status"] == "Active" and check_password_hash(customer["password_hash"], password):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE customers SET last_login=? WHERE id=?", (now, customer["id"]))
            conn.commit()
            conn.close()
            session.clear()
            session["customer_id"] = customer["id"]
            session["customer_name"] = customer["full_name"]
            next_url = request.args.get("next")
            return redirect(next_url if next_url and next_url.startswith("/") else url_for("home"))
        conn.close()
        error = "Invalid email or password."
    return render_template_string(LOGIN_PAGE, style=style, books=books, error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("customer_id"):
        return redirect(url_for("home"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        mobile = request.form.get("mobile", "").strip()
        password = request.form.get("password", "")
        if len(name) < 2:
            flash("Please enter your full name.", "error")
            return redirect(url_for("register"))
        if not (mobile.isdigit() and len(mobile) == 10):
            flash("Enter a valid 10-digit mobile number.", "error")
            return redirect(url_for("register"))
        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))
        conn = get_db()
        try:
            conn.execute("""INSERT INTO customers
                (full_name,email,mobile,password_hash,registration_date,status)
                VALUES (?,?,?,?,?,?)""",
                (name, email, mobile, generate_password_hash(password),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Active"))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("An account with this email already exists. Please login.", "error")
            return redirect(url_for("login"))
        conn.close()
        flash("Account created successfully. Please sign in.", "success")
        return redirect(url_for("login"))
    return render_template_string(REGISTER_PAGE, style=style)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# --------------------------------------------------
# ADMIN ROUTES
# NOTE: Replace these environment variables before production.
# --------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_customers"))
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@nileshbookstore.com").lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
        if email == admin_email and password == admin_password:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_customers"))
        error = "Invalid admin credentials."
    return render_template_string(ADMIN_LOGIN_PAGE, style=style, error=error)

@app.route("/admin/customers")
@admin_required
def admin_customers():
    conn = get_db()
    customers = conn.execute("""SELECT id, full_name, email, mobile,
                                registration_date, last_login, status
                                FROM customers ORDER BY id DESC""").fetchall()
    active_count = conn.execute("SELECT COUNT(*) FROM customers WHERE status='Active'").fetchone()[0]
    conn.close()
    return render_template_string(ADMIN_CUSTOMERS_PAGE, style=style,
                                  customers=customers, active_count=active_count)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# --------------------------------------------------
# START
# --------------------------------------------------
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
