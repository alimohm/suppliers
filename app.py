import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# استيراد إعداداتك ومنطق العمل
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات المجلدات والرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

# تهيئة قاعدة البيانات
init_db(app)

# 1. المسار الرئيسي
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# 2. بوابة الدخول (مع تأمين البيانات)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        if login_vendor(user, pw):
            # إنشاء هوية رقمية (Wallet) فور الدخول لمنع خطأ الـ Template
            session['username'] = user
            session['logged_in'] = True
            session['wallet'] = f"0xMAH_{os.urandom(4).hex().upper()}"
            return redirect(url_for('dashboard'))
        
        flash("❌ خطأ في بيانات الدخول، حاول مرة أخرى", "danger")
    
    return render_template('login.html')

# 3. لوحة التحكم (Dashboard) - الربط العميق مع الهيكل
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    
    # جلب بيانات المورد والمنتجات مع معالجة الأخطاء (لضمان عدم ظهور 500)
    try:
        vendor = Vendor.query.filter_by(username=user_session).first()
        products = Product.query.filter_by(vendor_username=user_session).all()
        products_count = len(products) if products else 0
    except Exception as e:
        print(f"⚠️ خطأ في جلب البيانات: {e}")
        vendor = None
        products = []
        products_count = 0

    # تأكيد وجود المحفظة في الجلسة قبل العرض
    if 'wallet' not in session:
        session['wallet'] = "0xPENDING_SYNC"

    return render_template('dashboard.html', 
                           vendor=vendor, 
                           products=products, 
                           products_count=products_count)

# 4. إضافة منتج (مع ربط الويب هوك)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description', '') 
        p_image = request.files.get('image')

        if not p_name or not p_price:
            flash("❌ يرجى تعبئة الحقول الأساسية", "warning")
            return redirect(url_for('dashboard'))

        try:
            image_filename = None
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                image_filename = f"{secure_filename(p_name)}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            new_item = Product(
                name=p_name,
                price=float(p_price),
                description=p_desc,
                image_file=image_filename,
                vendor_username=session['username']
            )
            db.session.add(new_item)
            db.session.commit()
            
            # محاولة المزامنة مع منصة قمرة
            send_to_qumra_webhook(p_name, p_price, p_desc, image_filename)
            flash(f"✅ تم إدراج {p_name} في سلسلة الإمداد", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"❌ حدث خطأ فني: {str(e)}", "danger")
            
        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

# 5. تسجيل الخروج
@app.route('/logout')
def logout_route():
    session.clear() # تنظيف كامل للجلسة لضمان الأمان
    return redirect(url_for('login_page'))

# التشغيل مع وضع التصحيح (Debug Mode)
if __name__ == '__main__':
    # ملاحظة: debug=True ستكشف لك السطر المسبب لخطأ 500 بدقة
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
