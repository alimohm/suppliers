# ==========================================
# --- 1. التوجيه الرئيسي (Home Redirect) ---
# ==========================================
@app.route('/')
def home_redirect():
    """توجيه المستخدم بناءً على هويته المسجلة"""
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): 
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# ==========================================
# --- 2. بوابة دخول المورد (Login) ---
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        if not u or not p:
            flash("يرجى إدخال اسم المستخدم وكلمة المرور.", "warning")
            return redirect(url_for('login_page'))

        # منطق التحقق المباشر
        vendor = Vendor.query.filter_by(username=u).first()
        if not vendor:
            flash("تنبيه: اسم المستخدم هذا غير مسجل في المنصة اللامركزية.", "danger")
        elif not check_password_hash(vendor.password, p):
            flash("فشل تأمين البوابة: كلمة المرور غير صحيحة.", "danger")
        elif vendor.status == 'blocked':
            flash("وصول مرفوض: الحساب موقف بقرار سيادي.", "danger")
        else:
            session.clear()
            session['user_id'] = vendor.id
            session['username'] = vendor.username
            session['role'] = 'vendor'
            flash(f"أهلاً بك يا سيد {vendor.employee_name} في سوقك الذكي.", "success")
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

# ==========================================
# --- 3. لوحة تحكم المورد (Dashboard) ---
# ==========================================
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.get(session.get('user_id'))
    if not vendor_data:
        session.clear()
        return redirect(url_for('login_page'))
        
    products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

# ==========================================
# --- 4. بوابة دخول الإدارة (Admin Login) ---
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        admin = AdminUser.query.filter_by(username=u).first()
        if admin and check_password_hash(admin.password, p):
            session.clear()
            session['admin_id'] = admin.id
            session['admin_user'] = admin.username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard_route'))
        else:
            flash("بيانات دخول برج المراقبة غير صحيحة.", "danger")
            
    return render_template('admin_login.html')

# ==========================================
# --- 5. لوحة تحكم الإدارة (Admin Dashboard) ---
# ==========================================
@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', vendors=all_vendors, pending_items=pending_items)

# ==========================================
# --- 6. تأمين الخروج (Logout) ---
# ==========================================
@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تأمين البوابات بنجاح. في أمان الله.", "info")
    return redirect(url_for('login_page'))
