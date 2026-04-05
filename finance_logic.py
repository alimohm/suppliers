from models import Wallet, Transaction
from database import db
from datetime import datetime

def transfer_mah(sender_wallet_id, receiver_wallet_no, amount, note="تحويل تجاري"):
    """
    محرك التحويل السيادي (MAH Transfer Engine)
    الربط: يربط بين محفظتين ويسجل العملية في جدول Transactions
    """
    try:
        # 1. جلب محفظة المرسل والتحقق من الرصيد
        sender = Wallet.query.get(sender_wallet_id)
        if not sender or sender.balance < amount:
            return False, "عذراً يا عظيم، الرصيد غير كافٍ لإتمام العملية."

        # 2. جلب محفظة المستقبل عبر رقم المحفظة (MAH-XXXXXX)
        receiver = Wallet.query.filter_by(wallet_number=receiver_wallet_no).first()
        if not receiver:
            return False, "رقم المحفظة المستلمة غير موجود في النظام."

        # 3. تنفيذ العملية الحسابية (الخصم والإيداع)
        sender.balance -= amount
        receiver.balance += amount

        # 4. توثيق العملية للمرسل (خصم)
        tx_sender = Transaction(
            wallet_id=sender.id,
            tx_type='سحب/تحويل',
            amount=-amount,
            description=f"تحويل إلى {receiver.wallet_number} - {note}"
        )

        # 5. توثيق العملية للمستقبل (إيداع)
        tx_receiver = Transaction(
            wallet_id=receiver.id,
            tx_type='إيداع/تحويل',
            amount=amount,
            description=f"استلام من {sender.wallet_number} - {note}"
        )

        db.session.add(tx_sender)
        db.session.add(tx_receiver)
        
        # 6. الحفظ النهائي (Commit) لضمان عدم ضياع أي طرف
        db.session.commit()
        return True, f"تم تحويل {amount} MAH بنجاح."

    except Exception as e:
        db.session.rollback()
        return False, f"خطأ تقني في الشبكة المالية: {str(e)}"
