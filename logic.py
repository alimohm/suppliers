import random
import string
from database import db, User, Wallet

def add_new_vendor(brand, user_name, password):
    try:
        # 1. التأكد من أن المستخدم غير موجود مسبقاً
        if User.query.filter_by(username=user_name).first():
            return False, "اليوزر موجود مسبقاً"

        # 2. إنشاء رقم محفظة (حافظ) فريد للسوق
        wallet_no = "MAH-" + ''.join(random.choices(string.digits, k=8))

        # 3. إنشاء سجل المورد الجديد
        new_vendor = User(
            username=user_name, 
            password=password, 
            role='vendor', 
            brand_name=brand
        )
        db.session.add(new_vendor)
        db.session.flush() # للحصول على ID المستخدم قبل الحفظ النهائي

        # 4. إنشاء المحفظة المالية المرتبطة به
        new_wallet = Wallet(
            user_id=new_vendor.id, 
            wallet_number=wallet_no, 
            balance=0.0
        )
        db.session.add(new_wallet)

        # 5. الحفظ النهائي (هذا هو السطر الذي يجعله يظهر في الكشوفات)
        db.session.commit() 
        return True, wallet_no

    except Exception as e:
        db.session.rollback() # تراجع عن العملية في حال حدوث خطأ
        print(f"Error saving to DB: {e}")
        return False, str(e)
