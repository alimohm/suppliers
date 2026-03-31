from config import Config

def calculate_final_price(raw_price, currency):
    try:
        price = float(raw_price)
        # التحويل للريال إذا كانت العملة دولار
        base_price = price * Config.USD_TO_SAR if currency == "USD" else price
        # إضافة الربح 30%
        return round(base_price * Config.PROFIT_MARGIN, 2)
    except:
        return 0.0
