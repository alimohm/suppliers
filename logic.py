import os, random
from werkzeug.utils import secure_filename
from database import db, Vendor, Wallet, Product, Transaction

def add_vendor_with_wallet(brand, user, pwd):
    try:
        v = Vendor(brand_name=brand, username=user, password=pwd)
        db.session.add(v)
        db.session.flush()
        w_no = f"MAH-{random.randint(100000, 999999)}"
        db.session.add(Wallet(wallet_number=w_no, vendor_id=v.id, balance=0.0))
        db.session.commit()
        return True, w_no
    except:
        db.session.rollback()
        return False, None

def process_transfer(s_wallet_id, r_wallet_no, amount, note):
    sender = Wallet.query.get(s_wallet_id)
    receiver = Wallet.query.filter_by(wallet_number=r_wallet_no).first()
    if not sender or sender.balance < amount or not receiver:
        return False, "فشل: رصيد غير كافٍ أو محفظة خاطئة"
    
    sender.balance -= amount
    receiver.balance += amount
    db.session.add(Transaction(wallet_id=sender.id, tx_type='سحب', amount=-amount, description=f"إلى {r_wallet_no}: {note}"))
    db.session.add(Transaction(wallet_id=receiver.id, tx_type='إيداع', amount=amount, description=f"من {sender.wallet_number}: {note}"))
    db.session.commit()
    return True, "تم التحويل بنجاح"

def save_product(v_id, name, price, stock, file):
    url = '/static/images/default.png'
    if file:
        os.makedirs('static/uploads', exist_ok=True)
        fname = secure_filename(f"v{v_id}_{file.filename}")
        file.save(os.path.join('static/uploads', fname))
        url = f'/static/uploads/{fname}'
    db.session.add(Product(vendor_id=v_id, name=name, price=float(price), stock=int(stock), image_url=url))
    db.session.commit()
