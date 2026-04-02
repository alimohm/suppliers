import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# ضمان وجود مسار الرفع من الإعدادات
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # إنشاء المجلد تلقائياً إذا لم يوجد

# تهيئة قاعدة البيانات (تفعيل الترقيع الذكي للأعمدة)
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
        flash("❌ خطأ في اسم المستخدم أو كلمة المرور", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    try:
        # عرض منتجات المورد الحالي فقط
        products = Product.query.filter_by(vendor_username=session['username']).all()
        products_count = len(products)
    except Exception as e:
        print(f"⚠️ تنبيه أثناء جلب الإحصائيات: {e}")
        products_count = 0
        products = []
    
    return render_template('dashboard.html', vendor=vendor, products_count=products_count, products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # استقبال البيانات من الحقول الجديدة في النافذة الاحترافية
        p_name = request.form.get('p_name')
        p_price = request.form.get('p_price')
        p_currency = request.form.get('p_currency', 'MAH')
        p_desc = request.form.get('p_desc', '') 
        
        # استقبال الصور المتعددة والفيديو
        p_images = request.files.getlist('p_images')
        p_video = request.files.get('p_video')

        if not p_name or not p_price:
            flash("❌ يرجى إدخال اسم المنتج وسعره.", "danger")
            return redirect(url_for('dashboard'))

        try:
            final_price = float(p_price)
            main_image_filename = None
            
            # تنظيف اسم المنتج لاستخدامه في تسمية الملفات
            safe_product_name = secure_filename(p_name).replace(' ', '_')

            # 1. معالجة الصور مع إعادة التسمية التلقائية باسم المنتج
            for index, img in enumerate(p_images):
                if img and img.filename != '':
                    ext = os.path.splitext(img.filename)[1]
                    # التسمية الجديدة: اسم_المنتج_1.jpg
                    image_filename = f"{safe_product_name}_{index+1}{ext}"
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    
                    if index == 0:
                        main_image_filename = image_filename

            # 2. معالجة الفيديو (اختياري) وإعادة تسميته
            if p_video and p_video.filename != '':
                v_ext = os.path.splitext(p_video.filename)[1]
                video_filename = f"{safe_product_name}_video{v_ext}"
                p_video.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

            # 3. الحفظ المحلي في قاعدة البيانات
            # ندمج العملة في الوصف لضمان ظهورها في كل مكان
            full_desc = f"[{p_currency}] {p_desc}"
            
            new_item = Product(
                name=p_name,
                price=final_price,
                description=full_desc,
                image_file=main_image_filename, 
                vendor_username=session['username']
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # 4. إطلاق المزامنة السيادية عبر GraphQL (إرسال السعر مع العملة)
            try:
                price_str = f"{final_price} {p_currency}"
                status = send_to_qumra_webhook(p_name, price_str, p_desc, main_image_filename)
                if status:
                    flash(f"🚀 تم رفع {p_name} وإعادة تسمية الملفات بنجاح!", "success")
                else:
                    flash(f"✅ تم الحفظ في لوحتك، جاري تحديث المتجر الخارجي.", "info")
            except Exception as sync_err:
                print(f"📡 خطأ مزامنة خارجية: {sync_err}")
                flash(f"⚠️ المنتج متاح في لوحتك، سيتم مزامنته لاحقاً.", "warning")

            return redirect(url_for('dashboard'))

        except ValueError:
            flash("❌ خطأ: السعر يجب أن يكون رقماً.", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ قاعدة بيانات: {e}")
            flash(f"❌ حدث خطأ فني أثناء المعالجة الملكية.", "danger")
            return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))

@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    """استقبال تحديثات الطلبات من قمرة"""
    try:
        data = request.json
        print(f"📡 إشارة قادمة من قمرة: {data}")
        return {"status": "success", "message": "Mahjoub Received"}, 200
    except Exception as e:
        print(f"❌ خطأ ويب هوك: {e}")
        return {"status": "error"}, 400

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    # دعم بورت Railway التلقائي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
