import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استدعاء الملفات الجانبية (المنطق المنفصل) ---
# التأكد من مطابقة الأسماء للموجود في مجلدك
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance        # حسابات الـ 30%
    import bridge_logic   # الربط مع المتجر
except ImportError as e:
    # هذا السطر سيطبع لك السبب الحقيقي في سجلات ريلوي
    print(f"خطأ قاتل في استدعاء ملفات المنطق: {e}")

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات (Postgres)
init_db(app)

# إنشاء المجلدات الضرورية للصور
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- تفعيل الهيكل الداخلي عند بدء التشغيل ---
with app.app_context():
    db.create_all() # إنشاء الجداول تلقائياً لمنع خطأ 500
    if not Vendor.query.filter_by(username="ali").first():
        test_v = Vendor(username="ali", password="123", owner_name="Ali Mahjoub")
        db.session.add(test_v)
        db.session.commit()

@app.route('/')
def home():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # بوابة الدخول الملكية
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("خطأ في البيانات")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # الهيكل الداخلي للوحة التحكم
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    price_in = request.form.get('price')

    # 1. استخدام ملف finance.py المنفصل لحساب السعر
    f_price = finance.calculate_final_price(price_in, "USD")

    # 2. حفظ الصورة
    img_url = ""
    if file:
        fname = secure_filename(f"{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, fname))
        img_url = f"{request.url_root.rstrip('/')}/static/uploads/{fname}"

    # 3. الحفظ في قاعدة البيانات
    new_p = Product(name=request.form.get('name'), cost_price=float(price_in), 
                    final_price=f_price, image_url=img_url, vendor_id=v_id)
    db.session.add(new_p)
    db.session.commit()

    # 4. استخدام ملف bridge_logic.py المنفصل للربط
    bridge_logic.push_to_store({"name": new_p.name, "price": f_price, "img": img_url})
    
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
