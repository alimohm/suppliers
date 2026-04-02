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

# إعدادات المجلدات والرفع
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
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        
        if login_vendor(user_input, pass_input):
            flash(f"مرحباً بك في محجوب أونلاين - سوقك الذكي", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("خطأ في بيانات الدخول، يرجى التحقق.", "danger")
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    vendor = Vendor.query.filter_by(username=user_session).first()
    # جلب المنتجات التي لم تنشر بعد في قمرة لتظهر في لوحة التحكم المحلية
    products = Product.query.filter_by(vendor_username=user_session, is_published=False).all()
    
    return render_template('dashboard.html', vendor=vendor, products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد لربط العلامة التجارية والمحفظة
    user_session = session.get('username')
    vendor = Vendor.query.filter_by(username=user_session).first()

    if request.method == 'GET':
        return render_template('add_product.html', vendor=vendor)
    
    # استلام البيانات من الفورم المطور
    p_name = request.form.get('name')
    p_brand = vendor.brand_name  # ربط آلي بالعلامة التجارية المسجلة للمورد
    p_price = request.form.get('price')
    p_currency = request.form.get('currency', 'YER')
    p_stock = request.form.get('stock', 1)
    p_desc = request.form.get('description', '')
    p_image = request.files.get('image')

    if p_name and p_price:
        try:
            # معالجة رفع وتسمية الصورة باحترافية
            image_filename = None
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                # تسمية الملف باسم المنتج لتعزيز الـ SEO في محجوب أونلاين
                clean_name = secure_filename(p_name)
                image_filename = f"{clean_name}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # إنشاء كائن المنتج في "القاعجة"
            new_item = Product(
                name=p_name,
                brand=p_brand,
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

            # المزامنة الخارجية (قمرة) مع إرسال بيانات العلامة التجارية والمنصة اللامركزية
            success = send_to_qumra_webhook(
                name=p_name, 
                price=p_price, 
                desc=p_desc, 
                image=image_filename,
                brand=p_brand,
                platform="محجوب أونلاين - المنصة اللامركزية الأولى في اليمن"
            )
            
            if success:
                new_item.is_published = True
                db.session.commit()
                flash(f"✅ تم نشر المنتج '{p_name}' بنجاح في سوقك الذكي!", "success")
            else:
                flash(f"⚠️ المنتج حفظ محلياً، فشل الربط مع السيرفر الخارجي حالياً.", "warning")

            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"❌ خطأ تقني: {str(e)}", "danger")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    # التشغيل المتوافق مع السيرفرات السحابية
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
