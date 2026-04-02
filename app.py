import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# استيراد الإعدادات والقاعدة والموديلات
from config import Config
from database import db, init_db
from models import Product, Vendor
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات المجلدات (Media)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة قاعدة البيانات (PostgreSQL/SQLite)
init_db(app)

# --- المسارات (Routes) ---

@app.route('/')
def index():
    """توجيه المستخدم حسب حالة تسجيل الدخول"""
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
        
        # التحقق من قاعدة البيانات عبر دالة اللوجيك
        if login_vendor(user_input, pass_input):
            flash("مرحباً بك في محجوب أونلاين - المنصة اللامركزية الأولى", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("بيانات الدخول غير صحيحة، حاول مجدداً.", "danger")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم: تستدعي الهيكل وتعرض بيانات المورد والمنتجات"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    # جلب بيانات المورد لظهور البراند والمحفظة في الهيكل
    vendor_data = Vendor.query.filter_by(username=user_session).first()
    
    if not vendor_data:
        return logout() # أمان إضافي في حال حذف الحساب

    # جلب المنتجات المحلية التي لم تنشر بعد في المنصات الخارجية
    products_list = Product.query.filter_by(vendor_username=user_session, is_published=False).all()
    
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """إضافة منتج: الربط مع الذكاء الاصطناعي والعلامة التجارية للمورد"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    vendor = Vendor.query.filter_by(username=user_session).first()

    if request.method == 'GET':
        # نمرر الـ vendor لكي يعرف الـ HTML البراند المربوط به
        return render_template('add_product.html', vendor=vendor)
    
    # استلام البيانات من الفورم الاحترافي
    p_name = request.form.get('name')
    p_price = request.form.get('price')
    p_currency = request.form.get('currency', 'YER')
    p_stock = request.form.get('stock', 1)
    p_desc = request.form.get('description', '') # الوصف المولد بذكاء
    p_image = request.files.get('image')

    if p_name and p_price:
        try:
            # 1. معالجة وتسمية الصورة (باسم المنتج + كود فريد) لـ SEO سوقك الذكي
            image_filename = None
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                safe_name = secure_filename(p_name)
                image_filename = f"{safe_name}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # 2. إنشاء المنتج في "القاعجة" مع ربطه بالبراند واللامركزية
            new_product = Product(
                name=p_name,
                brand=vendor.brand_name, # الربط الآلي بالبراند المربوط بالمستخدم
                price=float(p_price),
                currency=p_currency,
                stock=int(p_stock),
                description=p_desc,
                image_file=image_filename,
                vendor_id=vendor.id,
                vendor_username=user_session
            )
            
            db.session.add(new_product)
            db.session.commit()

            # 3. المزامنة الخارجية (إرسال البيانات لـ قمرة أو الويب هوك)
            # نرسل "اللامركزية" كجزء من البيانات التأكيدية
            sync_success = send_to_qumra_webhook(
                name=p_name, 
                price=p_price, 
                desc=p_desc, 
                image=image_filename,
                brand=vendor.brand_name,
                platform="محجوب أونلاين - المنصة اللامركزية الأولى في اليمن"
            )
            
            if sync_success:
                new_product.is_published = True
                db.session.commit()
                flash(f"✅ تم نشر المنتج '{p_name}' بنجاح في سوقك الذكي!", "success")
            else:
                flash(f"⚠️ المنتج حفظ محلياً، فشلت المزامنة الخارجية حالياً.", "warning")

            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ خطأ في النظام: {str(e)}", "danger")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout_route():
    return logout()

# تشغيل التطبيق بنمط الإنتاج
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
