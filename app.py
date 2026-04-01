import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات والربط مع Railway مع التحديث التلقائي للأعمدة
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
        user = request.form.get('username')
        pw = request.form.get('password')
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم - عرض الإحصائيات مع الخصوصية لكل مورد"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد الحالي
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    # جلب عدد المنتجات الخاصة بهذا المورد فقط
    try:
        products_count = Product.query.filter_by(vendor_username=session['username']).count()
    except Exception as e:
        print(f"⚠️ تنبيه أثناء جلب الإحصائيات: {e}")
        products_count = 0
    
    return render_template('dashboard.html', vendor=vendor, products_count=products_count)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """إضافة منتج جديد - الحفظ المحلي السريع ثم إطلاق شرارة المزامنة"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # 1. سحب البيانات والتحقق الأولي
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description', '') 
        
        if not p_name or not p_price:
            flash("❌ يرجى إدخال اسم المنتج وسعره.", "danger")
            return redirect(url_for('add_product'))

        try:
            final_price = float(p_price)

            # 2. الحفظ المحلي الفوري (لضمان بقاء البيانات في محجوب أونلاين حتى لو فشل الاتصال الخارجي)
            new_item = Product(
                name=p_name,
                price=final_price,
                description=p_desc,
                vendor_username=session['username']
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # 3. إطلاق المزامنة مع قمرة (المورد سيشعر بالسرعة لأننا سنعطيه الرد فوراً)
            try:
                # نرسل إشارة "طلب إضافة" لقمرة
                status = send_to_qumra_webhook(p_name, str(final_price), p_desc)
                if status:
                    flash(f"🚀 تم رفع {p_name} ومزامنته مع المتجر بنجاح!", "success")
                else:
                    flash(f"✅ تم الحفظ في لوحة محجوب، وجاري التحديث في المتجر.", "info")
            except Exception as sync_err:
                # في حال حدوث Timeout أو خطأ خارجي، يظل المنتج محفوظاً محلياً
                print(f"📡 خطأ مزامنة: {sync_err}")
                flash(f"⚠️ المنتج متاح في لوحتك، سيتم تحديث المتجر الخارجي آلياً.", "warning")

            return redirect(url_for('dashboard'))

        except ValueError:
            flash("❌ خطأ: السعر يجب أن يكون رقماً.", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ قاعدة بيانات: {e}")
            flash(f"❌ حدث خطأ فني أثناء الحفظ المحلي.", "danger")
            return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    """استقبال التنبيهات من منصة قمرة لتحديث الرصيد والطلبات"""
    try:
        data = request.json
        print(f"📡 إشارة قادمة من قمرة: {data}")
        # هنا سيتم لاحقاً إضافة منطق معالجة رصيد الـ MAH
        return {"status": "received"}, 200
    except:
        return {"status": "error"}, 400

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
