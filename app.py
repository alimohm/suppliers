import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة النظام وقاعدة البيانات (تأسيس حساب علي محجوب تلقائياً)
init_db(app)

# ---------------------------------------------------------
# 2. منطق التوجيه الذكي (Smart Routing)
# ---------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_admin'))
    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'vendor_dashboard'))

# ---------------------------------------------------------
# 3. بوابات الدخول (Admin & Vendor Login)
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        # التحقق من بيانات المدير "علي محجوب" أو الموردين
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': user.role})
            return redirect(url_for('index'))
        flash("بيانات الدخول غير صحيحة", "danger")
    return render_template('login_admin.html')

# ---------------------------------------------------------
# 4. نوافذ الإدارة (Admin Command Center)
# ---------------------------------------------------------

# أ- نافذة الإحصائيات الرئيسية
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah)

# ب- نافذة اعتماد الموردين (الحفظ والكشوفات)
@app.route('/admin/accounts')
def admin_accounts():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    # جلب قائمة الموردين لعرضها في الكشوفات تحت نموذج الإدخال
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_accounts.html', vendors=vendors)

# ---------------------------------------------------------
# 5. محركات العمليات والحفظ (Action Engines)
# ---------------------------------------------------------

# محرك إصدار التراخيص وحفظ الموردين في الكشوفات والحافظ
@app.route('/action/add-vendor', methods=['POST'])
def add_vendor():
    if session.get('role') != 'admin': return "Unauthorized", 403
    
    brand = request.form.get('brand')
    user_name = request.form.get('user')
    pwd = request.form.get('pwd')
    
    # تنفيذ عملية الحفظ في قاعدة البيانات عبر المنطق البرمجي
    success, wallet_no = logic.add_new_vendor(brand, user_name, pwd)
    
    if success:
        flash(f"تم اعتماد الكيان {brand} بنجاح. رقم الحافظ المالي: {wallet_no}", "success")
    else:
        flash("خطأ: هذا المستخدم مسجل مسبقاً في النظام"، "danger")
        
    return redirect(url_for('admin_accounts'))

# ---------------------------------------------------------
# 6. لوحة المورد (Vendor Portal)
# ---------------------------------------------------------
@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login_admin'))
    user = User.query.get(session['user_id'])
    return render_template('vendor_dashboard.html', wallet=user.wallet, products=user.products)

# ---------------------------------------------------------
# 7. الخروج والنظام
# ---------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_admin'))

if __name__ == '__main__':
    # تشغيل متوافق مع بيئة Railway بورت 8080
    app.run(host='0.0.0.0', port=8080)
