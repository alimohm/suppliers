import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

from config import Config
from database import db, init_db
from models import Product, Vendor
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الميديا والرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة قاعدة البيانات اللامركزية
init_db(app)

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if login_vendor(u, p):
            flash("مرحباً بك في محجوب أونلاين - سوقك الذكي", "success")
            return redirect(url_for('dashboard'))
        flash("خطأ في بيانات الدخول.", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    
    # استدعاء بيانات المورد (مشتاق الفقيه) من القاعدة
    vendor_data = Vendor.query.filter_by(username=user_session).first()
    
    # حماية من خطأ 500: إذا لم يجد المورد في القاعدة
    if not vendor_data:
        flash("تنبيه: حسابك غير مسجل في القاعدة اللامركزية.", "warning")
        return redirect(url_for('logout_route'))

    # جلب المنتجات المربوطة به
    products_list = Product.query.filter_by(vendor_username=user_session).all()
    
    # تمرير المتغيرات للهيكل والداشبورد
    return render_template('dashboard.html', 
                           vendor=vendor_data, 
                           products=products_list)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    vendor = Vendor.query.filter_by(username=user_session).first()

    if request.method == 'POST':
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_currency = request.form.get('currency', 'YER')
        p_stock = request.form.get('stock', 1)
        p_desc = request.form.get('description', '')
        p_image = request.files.get('image')

        if p_name and p_price:
            image_filename = None
            if p_image:
                ext = os.path.splitext(p_image.filename)[1]
                image_filename = f"{secure_filename(p_name)}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # إنشاء المنتج وربطه بعلامة المورد (عمار الفقيه للتجارة)
            new_item = Product(
                name=p_name,
                brand=vendor.brand_name, # سحب آلي للبراند من القاعدة
                price=float(p_price),
                currency=p_currency,
                stock=int(p_stock),
                description=p_desc,
                image_file=image_filename,
                vendor_id=vendor.id,
                vendor_username=user_session
            )
            db.session.add(new_item)
            db.session.commit()
            
            # المزامنة الخارجية
            send_to_qumra_webhook(p_name, p_price, p_desc, image_filename, vendor.brand_name)
            flash(f"✅ تم نشر المنتج تحت علامة {vendor.brand_name}", "success")
            return redirect(url_for('dashboard'))

    return render_template('add_product.html', vendor=vendor)

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
