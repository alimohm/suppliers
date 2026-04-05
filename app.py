import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة النظام وقاعدة البيانات
init_db(app)

# ---------------------------------------------------------
# 2. منطق التوجيه الذكي
# ---------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_admin'))
    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'vendor_dashboard'))

# ---------------------------------------------------------
# 3. بوابات الدخول (Admin & Vendor)
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': user.role})
            return redirect(url_for('index'))
        flash("بيانات الدخول غير صحيحة", "danger")
    return render_template('login_admin.html')

# ---------------------------------------------------------
# 4. لوحة التحكم الإدارية (مركز القيادة)
# ---------------------------------------------------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah)

@app.route('/admin/accounts')
def admin_accounts():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_accounts.html', vendors=vendors)

# ---------------------------------------------------------
# 5. لوحة تحكم المورد (بوابة الشريك)
# ---------------------------------------------------------
@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login_admin'))
    user = User.query.get(session['user_id'])
    return render_template('vendor_dashboard.html', wallet=user.wallet, products=user.products)

# ---------------------------------------------------------
# 6. محركات العمليات والحفظ (The Engine)
# ---------------------------------------------------------

# محرك تسجيل وحفظ المورد الجديد (هذا يحل مشكلة الـ Internal Error)
@app.route('/action/add-vendor', methods=['POST'])
def add_vendor():
    if session.get('role') != 'admin': return "Unauthorized", 403
    
    try:
        brand = request.form.get('brand')
        user_name = request.form.get('user')
        pwd = request.form.get('pwd')
        
        # استدعاء المنطق من logic.py وتأكيد الحفظ في DB
        success, wallet_no = logic.add_new_vendor(brand, user_name, pwd)
        
        if success:
            flash(f"تم اعتماد المورد {brand} بنجاح. رقم المحفظة: {wallet_no}", "success")
        else:
            flash("فشل في التسجيل، قد يكون اسم المستخدم مكرر", "danger")
            
    except Exception as e:
        flash(f"حدث خطأ تقني أثناء الحفظ: {str(e)}", "danger")
        
    return redirect(url_for('admin_accounts'))

# محرك إضافة المنتجات للمورد
@app.route('/action/add-product', methods=['POST'])
def add_product():
    if session.get('role') != 'vendor': return redirect(url_for('index'))
    
    name = request.form.get('name')
    price = request.form.get('price')
    # حفظ المنتج في قاعدة البيانات
    logic.add_vendor_product(session['user_id'], name, price)
    flash("تم إضافة المنتج لمتجرك بنجاح", "success")
    return redirect(url_for('vendor_dashboard'))

# ---------------------------------------------------------
# 7. نظام الخروج الأمن
# ---------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_admin'))

if __name__ == '__main__':
    # التشغيل المتوافق مع Railway
    app.run(host='0.0.0.0', port=os.getenv('PORT', 8080))
