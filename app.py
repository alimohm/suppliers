import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from database import db, init_db, Vendor, Product
import logic, finance, bridge_logic
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# إعداد مجلد رفع الصور
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db(app)

@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
    vendor = Vendor.query.get(v_id)
    
    # 1. معالجة الصورة المرفوعة
    file = request.files.get('image')
    image_url = ""
    if file and file.filename != '':
        filename = secure_filename(f"{vendor.id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        # رابط الصورة (يجب أن يكون متاحاً للعموم ليراه المتجر)
        image_url = f"https://your-app-name.up.railway.app/static/uploads/{filename}"

    # 2. الحساب المالي (30% + تحويل العملة)
    final_price = finance.calculate_final_price(
        request.form.get('price'), 
        request.form.get('currency')
    )
    
    # 3. الحفظ في قاعدة بيانات قمرة أولاً
    new_p = Product(
        name=request.form.get('name'),
        description=request.form.get('description'),
        cost_price=float(request.form.get('price')),
        final_price=final_price,
        image_url=image_url,
        currency=request.form.get('currency'),
        vendor_id=v_id
    )
    db.session.add(new_p)
    db.session.commit()

    # 4. النشر عبر الويب هوك لمتجر محجوب أونلاين
    data = {
        "name": new_p.name,
        "final_price": final_price,
        "description": new_p.description,
        "image_url": image_url,
        "wallet": vendor.wallet_address
    }
    
    if bridge_logic.push_to_store(data):
        flash(f"تم الحفظ والنشر كمسودة بنجاح! السعر النهائي: {final_price} ر.س")
    else:
        flash("تم الحفظ في قمرة ولكن فشل إرسال الويب هوك للمتجر.")
        
    return redirect(url_for('dashboard'))

# ... بقية المسارات (login, logout, dashboard) ...

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
