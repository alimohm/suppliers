import random, string
from database import db, User, Wallet, Product

def add_new_vendor(brand, user, pwd):
    wallet_no = "MAH-" + ''.join(random.choices(string.digits, k=8))
    new_user = User(username=user, password=pwd, role='vendor', brand_name=brand)
    db.session.add(new_user)
    db.session.flush() # للحصول على ID المستخدم الجديد
    
    new_wallet = Wallet(user_id=new_user.id, wallet_number=wallet_no, balance=0.0)
    db.session.add(new_wallet)
    db.session.commit()
    return True, wallet_no

def execute_transfer(sender_id, target_wallet_no, amount, note):
    sender_wallet = Wallet.query.filter_by(user_id=sender_id).first()
    receiver_wallet = Wallet.query.filter_by(wallet_number=target_wallet_no).first()
    
    if not receiver_wallet or sender_wallet.balance < amount:
        return False, "فشل التحويل: رصيد غير كافٍ أو محفظة خاطئة"
    
    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    db.session.commit()
    return True, "تم التحويل بنجاح"
