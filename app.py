import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استدعاء المنطق المنفصل (Modular Logic) ---
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance        # منطق زيادة الـ 30%
    import bridge_logic   # منطق الويب هوك والربط
except ImportError as e:
    # طباعة الخطأ في سجلات Railway إذا فقد أحد الملفات
    print(f"خطأ: فشل استدعاء أحد ملفات المنطق المنفصل: {e}")

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'MAHJOUB_ROYAL_2026' # لضمان عمل الجلسات والثبات

# تهيئة قاعدة البيانات
init_db(app)

# إعدادات رفع الصور
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# تفعيل الهيكل وقاعدة البيانات عند التشغيل
with app.app_context():
    db.create_all()
    # التأكد من وجود حساب المالك الافتراضي
    if not Vendor.query.filter_by(username="ali").first():
        v = Vendor(username="ali", password="123", owner_name="Ali Mahjoub", wallet_address="MQ-2026-ROYAL")
        db.session.add(v)
        db.session.commit()

# --- المسارات (Routes) ---

@app.route('/')
def home():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """بوابة الدخول الملكية"""
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("خطأ في بيانات الدخول")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """عرض الهيكل الداخلي الثابت"""
    v_id = session.get('vendor_id')
    if not v_id:
        return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    # نرسل كائن vendor لملء بيانات المحفظة والمنتجات في القوالب المنفصلة
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    """منطق الرفع باستخدام الملفات المنفصلة"""
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    cost_price = request.form.get('price')

    # 1. استدعاء الحسبة المالية من finance.py
    final_price = finance.calculate_final_price(cost_price, "USD")

    # 2. معالجة الصورة
    image_url = ""
    if file:
        filename = secure_filename(f"v{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_url = f"/static/uploads/{filename}"

    # 3. الحفظ عبر database.py
    new_product = Product(
        name=request.form.get('name'),
        cost_price=float(cost_price),
        final_price=final_price,
        image_url=image_url,
        vendor_id=v_id
    )
    db.session.add(new_product)
    db.session.commit()

    # 4. إرسال البيانات للمتجر عبر bridge_logic.py
    bridge_logic.push_to_store({
        "name": new_product.name,
        "price": final_price,
        "wallet": vendor.wallet_address
    })
    
    flash("تم رفع المنتج بنجاح وتفعيل الربط!")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # التشغيل المتوافق مع بورت Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
