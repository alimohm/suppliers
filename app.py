import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات (تنشئ الجداول وحساب علي محجوب تلقائياً)
init_db(app)

# ---------------------------------------------------------
# 1. التوجيه الرئيسي (Root Router)
# ---------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_admin'))
    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'vendor_dashboard'))

# ---------------------------------------------------------
# 2. بوابات الدخول (Auth Gates)
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        # التحقق من قاعدة البيانات
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': user.role})
            return redirect(url_for('index'))
        flash("بيانات الدخول غير صحيحة"، "danger")
    return render_template('login_admin.html')

# ---------------------------------------------------------
# 3. لوحة الإدارة - النوافذ المنفصلة (Admin Windows)
# ---------------------------------------------------------

# نافذة الإحصائيات الرئيسية (الرئيسية)
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    products_count = Product.query.count()
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah, products_count=products_count)

# نافذة اعتماد الحسابات (الموردين)
@app.route('/admin/accounts')
def admin_accounts():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_accounts.html', vendors=vendors)

# نافذة إدارة المحافظ والسيولة
@app.route('/admin/wallets')
def admin_wallets():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_wallets.html', vendors=vendors)

# نافذة إدارة الصلاحيات
@app.route('/admin/permissions')
def admin_permissions():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    return render_template('admin_permissions.html')

# ---------------------------------------------------------
# 4. لوحة المورد (Vendor Dashboard)
# ---------------------------------------------------------
@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login_admin'))
    user = User.query.get(session['user_id'])
    return render_template('vendor_dashboard.html', wallet=user.wallet, products=user.products)

# ---------------------------------------------------------
# 5. محركات الأفعال (Action Engines)
# ---------------------------------------------------------

@app.route('/action/add-vendor', methods=['POST'])
def add_vendor():
    if session.get('role') != 'admin': return "Unauthorized", 403
    brand = request.form.get('brand')
    user = request.form.get('user')
    pwd = request.form.get('pwd')
    logic.add_new_vendor(brand, user, pwd)
    flash(f"تم اعتماد المورد {brand} بنجاح"، "success")
    return redirect(url_for('admin_accounts'))

@app.route('/action/transfer', methods=['POST'])
def transfer():
    if 'user_id' not in session: return redirect(url_for('login_admin'))
    target = request.form.get('target')
    amount = float(request.form.get('amount', 0))
    success, msg = logic.execute_transfer(session['user_id'], target, amount, "تحويل داخلي")
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendor_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_admin'))

# ---------------------------------------------------------
# تشغيل النظام
# ---------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
