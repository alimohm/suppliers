from models import Wallet, Transaction
from database import db

def transfer_mah(sender_wallet_id, receiver_wallet_no, amount, note):
    sender = Wallet.query.get(sender_wallet_id)
    if not sender or sender.balance < amount:
        return False, "رصيد غير كافٍ"
    
    receiver = Wallet.query.filter_by(wallet_number=receiver_wallet_no).first()
    if not receiver:
        return False, "المحفظة المستلمة غير موجودة"

    sender.balance -= amount
    receiver.balance += amount
    
    tx1 = Transaction(wallet_id=sender.id, tx_type='سحب', amount=-amount, description=f"إلى {receiver.wallet_number}: {note}")
    tx2 = Transaction(wallet_id=receiver.id, tx_type='إيداع', amount=amount, description=f"من {sender.wallet_number}: {note}")
    
    db.session.add_all([tx1, tx2])
    db.session.commit()
    return True, "تم التحويل بنجاح"
