from flask_sqlalchemy import SQLAlchemy

# تعريف الكائن بدون استيراد موديلات هنا
db = SQLAlchemy()

def init_db(app):
    """تهيئة القاعدة وربطها بالتطبيق"""
    db.init_app(app)
    with app.app_context():
        # هذا السطر يحل مشكلة (column vendor.status does not exist)
        # سيقوم بإنشاء أي أعمدة مفقودة في Railway
        db.create_all() 
        print("🚀 قاعدة بيانات 'سوقك الذكي' متصلة ومحدثة.")
