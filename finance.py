def calculate_final_price(cost):
    """إضافة نسبة الربح 30%"""
    try:
        return round(float(cost) * 1.30, 2)
    except: return 0.0
