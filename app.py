import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استدعاء الملفات الجانبية (نظام المنطق المنفصل) ---
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance
    import bridge_logic
except ImportError as e:
    # طباعة الخطأ بوضوح في سجلات Railway إذا فشل الاستدعاء
    print(f"CRITICAL ERROR: فشل استدعاء الملفات المنطقية: {e}")

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة قاعدة البيانات ومجلد الصور
init_db(app)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 2. إنشاء الجداول والمستخدم التجريبي (ضمان عدم حدوث خطأ 500)
def setup_application():
    with app.app_context():
        db.create_all()  # إنشاء الجداول في Postgres إذا لم تكن موجودة
        if not Vendor.query.filter_by(username="ali").first():
            # إنشاء حساب المالك الافتراضي (الحساب الملكي)
            test_v = Vendor(
                username="ali", 
                password="123", 
                owner_name="Ali Mahjoub",
                wallet_address="MQ-ROYAL-2026"
            )
            db.session.add(test_v)
            db.session.commit()

# --- المسارات (Routes) ---

@app.route('/')
def home():
    """توجيه المستخدم بناءً على حالة الجلسة"""
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """بوابة الدخول الملكية لمحجوب أونلاين"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Vendor.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['vendor_id'] = user.id
            session.permanent = True  # الحفاظ على تسجيل الدخول
            return redirect(url_for('dashboard'))
        
        flash("عذراً، بيانات الدخول غير صحيحة")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """الهيكل الداخلي للوحة التحكم"""
    v_id = session.get('vendor_id')
    if not v_id:
        return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    """منطق إضافة المنتجات والربط مع المتجر"""
    v_id = session.get('vendor_id')
    if not v_id:
        return redirect(url_for('login'))
        
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    name = request.form.get('name')
    price = request.form.get('price')
    currency = request.form.get('currency', 'USD')
    
    # 1. معالجة وحفظ الصورة
    image_url = ""
    if file and file.filename != '':
        filename = secure_filename(f"v{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_url = f"{request.url_root.rstrip('/')}/static/uploads/{filename}"

    try:
        # 2. الحسبة المالية (زيادة الربح الرقمي 30%) عبر ملف finance.py
        f_price = finance.calculate_final_price(price, currency)

        # 3. الحفظ في قاعدة البيانات
        new_p = Product(
            name=name,
            cost_price=float(price),
            final_price=f_price,
            image_url=image_url,
            vendor_id=v_id
        )
        db.session.add(new_p)
        db.session.commit()

        # 4. دفع البيانات للمتجر (Webhook) عبر bridge_logic.py
        bridge_logic.push_to_store({
            "name": new_p.name, 
            "final_price": f_price, 
            "image_url": image_url, 
            "vendor": vendor.owner_name,
            "wallet": vendor.wallet_address
        })
        
        flash(f"تم نشر {name} بنجاح في المنصة!")
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء النشر: {str(e)}")
        
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    setup_application()
    # التشغيل المتوافق مع بيئة Railway و Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
