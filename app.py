import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from database import db, init_db, Vendor, Product
import finance, bridge_logic
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# إعداد مجلد الصور
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db(app)

@app.route('/')
def dashboard():
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
    
    # 1. معالجة ورفع الصورة
    image_url = ""
    if file and file.filename != '':
        filename = secure_filename(f"qmr_{v_id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        # رابط الصورة المباشر (استبدل الدومين برابط ريلوي الخاص بك)
        image_url = f"{request.url_root.rstrip('/')}/static/uploads/{filename}"

    # 2. الحساب المالي
    raw_p = request.form.get('price')
    curr = request.form.get('currency')
    f_price = finance.calculate_final_price(raw_p, curr)

    # 3. الحفظ في قاعدة بيانات قمرة
    new_p = Product(
        name=request.form.get('name'),
        description=request.form.get('description'),
        cost_price=float(raw_p),
        final_price=f_price,
        image_url=image_url,
        currency=curr,
        vendor_id=v_id
    )
    db.session.add(new_p)
    db.session.commit()

    # 4. النشر عبر الويب هوك للمتجر
    data = {
        "name": new_p.name,
        "final_price": f_price,
        "description": new_p.description,
        "image_url": image_url,
        "wallet": vendor.wallet_address
    }
    
    if bridge_logic.push_to_store(data):
        flash(f"تم الحفظ والنشر بنجاح! السعر النهائي: {f_price} ر.س")
    else:
        flash("تم الحفظ في قمرة ولكن فشل الربط مع المتجر.")
        
    return redirect(url_for('dashboard'))

# مسارات تسجيل الدخول والخروج (تأكد من وجود منطق الـ Login في logic.py)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # كود الدخول المبسط
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("بيانات الدخول غير صحيحة")
    return render_template('login.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # إنشاء الجداول تلقائياً عند التشغيل
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
