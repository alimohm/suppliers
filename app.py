# ==========================================
# --- 1. مسار البداية (Home) ---
# ==========================================
@app.route('/')
def home():
    if session.get('role') == 'admin': return redirect(url_for('admin_dashboard'))
    if session.get('role') == 'vendor': return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login'))

# ==========================================
# --- 2. دخول المورد (Login) ---
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        # استدعاء المنطق من logic.py
        success, message = login_vendor_logic(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(message, "danger")
    return render_template('login.html') # استدعاء صفحة login.html

# ==========================================
# --- 3. لوحة تحكم المورد (Dashboard) ---
# ==========================================
@app.route('/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login'))
    # جلب بيانات المورد ومنتجاته للعرض في HTML
    vendor = Vendor.query.get(session['user_id'])
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

# ==========================================
# --- 4. دخول الإدارة (Admin Login) ---
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        # استدعاء منطق التحقق الخاص بالإدارة
        success, message = verify_admin_credentials(u, p)
        if success:
            return redirect(url_for('admin_dashboard'))
        flash(message, "danger")
    return render_template('admin_login.html')

# ==========================================
# --- 5. لوحة تحكم الإدارة (Admin Dashboard) ---
# ==========================================
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    vendors = Vendor.query.all()
    # استدعاء صفحة admin_dashboard.html التي جهزتها
    return render_template('admin_dashboard.html', vendors=vendors)

# ==========================================
# --- 6. الخروج (Logout) ---
# ==========================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
