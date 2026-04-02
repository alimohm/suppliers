from flask_sqlalchemy import SQLAlchemy

# تعريف الكائن المركزي لقاعدة البيانات
db = SQLAlchemy()

def init_db(app):
    """
    تهيئة قاعدة البيانات، تحديث الهيكل، وإضافة مستخدم الأدمن الأول.
    """
    # استيراد الموديلات من ملف models.py لضمان التعرف على الحقول الجديدة
    from models import Vendor, Product 
    
    # ربط Flask بالكائن db
    db.init_app(app)
    
    with app.app_context():
        try:
            # --- المرحلة 1: تصفير وتحديث الهيكل ---
            # ملاحظة: السطر أدناه يعمل لمرة واحدة فقط لتحديث PostgreSQL في Railway
            db.drop_all() 
            db.create_all()
            
            # --- المرحلة 2: إنشاء حسابك (الأدمن) تلقائياً ---
            # نتحقق أولاً إذا كان المستخدم موجوداً لتجنب التكرار
            if not Vendor.query.filter_by(username="ali").first():
                admin_user = Vendor(
                    username="ali", 
                    password="123", # يمكنك تغيير كلمة المرور لاحقاً من قاعدة البيانات
                    brand_name="محجوب أونلاين",
                    # توليد عنوان محفظة فريد للأدمن
                    wallet_address="MAH-ROYAL-2026-777" 
                )
                db.session.add(admin_user)
                db.session.commit()
                print("👤 تم إنشاء مستخدم الأدمن (ali) بنجاح!")
            
            print("🚀 تم تحديث الجداول في PostgreSQL وجاهزون للانطلاق!")
            
        except Exception as e:
            print(f"❌ حدث خطأ أثناء تهيئة قاعدة البيانات: {e}")

# --- نصيحة المهندس ---
# بعد أن تنجح في تسجيل الدخول بـ (ali) و (123)، قم بوضع علامة # قبل السطر db.drop_all()
# لكي يحافظ السيرفر على بيانات المنتجات الجديدة التي ستضيفها.
