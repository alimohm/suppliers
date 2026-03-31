def calculate_final_price(cost):
    """حسبة ملكية بزيادة 30%"""
    try:
        return round(float(cost) * 1.30, 2)
    except: return 0.0
