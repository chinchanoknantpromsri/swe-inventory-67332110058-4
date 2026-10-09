def calculate_discount(price: float, discount_percent: float) -> float:
    """
    คำนวณราคาหลังหักส่วนลด
    - price ต้อง >= 0
    - discount_percent ต้องอยู่ในช่วง 0 ถึง 100
    - คืนค่าทศนิยม 2 ตำแหน่ง
    """
    if price < 0:
        raise ValueError("ราคาสินค้าต้องไม่ติดลบ")
    if not (0 <= discount_percent <= 100):
        raise ValueError("เปอร์เซ็นต์ส่วนลดต้องอยู่ระหว่าง 0 ถึง 100")
    
    discount_amount = price * (discount_percent / 100.0)
    final_price = price - discount_amount
    return round(final_price, 2)