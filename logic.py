import os, random
from werkzeug.utils import secure_filename
from database import db, User, Wallet, Product, Transaction

def add_new_vendor(brand, user, pwd):
    try:
        new_v = User(username=user, password=pwd, brand_name=brand, role='vendor')
        db.session.add(new_v)
        db.session.flush()
        
        # إنشاء محفظة تلقائياً برصيد افتراضي 100 MAH
        wallet_no = f"MAH-{random.randint(100000, 999999)}"
        db.session.add(Wallet(wallet_number=wallet_no, user_id=new_v.id, balance=100.0))
        
        db.session.commit()
        return True, wallet_no
    except:
        db.session.rollback()
        return False, None

def execute_transfer(sender_id, receiver_wallet_no, amount, note):
    sender_wallet = Wallet.query.filter_by(user_id=sender_id).first()
    receiver_wallet = Wallet.query.filter_by(wallet_number=receiver_wallet_no).first()
    
    if not sender_wallet or not receiver_wallet or sender_wallet.balance < amount:
        return False, "الرصيد غير كافٍ أو رقم المحفظة خاطئ"
    
    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    
    db.session.add(Transaction(wallet_id=sender_wallet.id, tx_type='سحب', amount=-amount, description=f"إلى {receiver_wallet_no}: {note}"))
    db.session.add(Transaction(wallet_id=receiver_wallet.id, tx_type='إيداع', amount=amount, description=f"من {sender_wallet.wallet_number}: {note}"))
    
    db.session.commit()
    return True, "تمت العملية بنجاح"

def add_vendor_product(v_id, name, price, stock, file, upload_folder):
    img_url = '/static/images/default.png'
    if file:
        os.makedirs(upload_folder, exist_ok=True)
        fname = secure_filename(f"v{v_id}_{file.filename}")
        file.save(os.path.join(upload_folder, fname))
        img_url = f'/static/uploads/{fname}'
    
    p = Product(user_id=v_id, name=name, price=float(price), stock=int(stock), image_url=img_url)
    db.session.add(p)
    db.session.commit()
