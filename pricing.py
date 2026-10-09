"""
pricing.py - โมดูลคำนวณราคาและส่วนลด (ฉบับ Refactored)
แก้ปัญหา Code Smells ครบทุกจุดตาม smells.md:
- แยกฟังก์ชันตามหน้าที่ (Single Responsibility Principle)
- ตั้งชื่อตัวแปรสื่อความหมาย (Clear Variable Naming)
- กำหนดค่าคงที่สำหรับอัตราส่วนลดและภาษี (Named Constants)
- ใช้วิธีเปรียบเทียบตามมาตรฐาน PEP 8 (is not None)
- รักษาพฤติกรรมเดิมไว้ 100% (Behavior Preserved)
"""

import datetime

# ==========================================================
# ค่าคงที่กฎเกณฑ์ทางธุรกิจ (Named Business Constants)
# ==========================================================
TAX_RATE = 0.07
BULK_TIER_LARGE_QTY = 100
BULK_TIER_LARGE_DISCOUNT = 0.10  # ลด 10%
BULK_TIER_MEDIUM_QTY = 50
BULK_TIER_MEDIUM_DISCOUNT = 0.05  # ลด 5%

MEMBER_DISCOUNT_RATE = 0.05       # สมาชิกลด 5%
POINTS_PER_BAHT_RATIO = 100       # 1 แต้มต่อ 100 บาท

COUPON_SAVE50_AMOUNT = 50.0
COUPON_HALF_MULTIPLIER = 0.5
COUPON_NEWYEAR_DISCOUNT = 0.20

# โครงสร้างสำหรับ Audit และแต้มสมาชิก (คงไว้เพื่อ Backward Compatibility)
member_points: dict[str, int] = {}
LOG: list[tuple[str | None, float]] = []


def calculate_subtotal(items: list[tuple[str, int, float]]) -> float:
    """คำนวณยอดรวมสินค้าพร้อมส่วนลดตามปริมาณการสั่งซื้อ (Bulk Tiers)"""
    total = 0.0
    for name, quantity, unit_price in items:
        if quantity <= 0:
            continue
        
        subtotal = quantity * unit_price
        if quantity >= BULK_TIER_LARGE_QTY:
            subtotal *= (1.0 - BULK_TIER_LARGE_DISCOUNT)
        elif quantity >= BULK_TIER_MEDIUM_QTY:
            subtotal *= (1.0 - BULK_TIER_MEDIUM_DISCOUNT)
            
        total += subtotal
    return total


def apply_member_discount_and_points(
    total: float, 
    member: str | None, 
    points_repo: dict[str, int]
) -> float:
    """คำนวณส่วนลดสมาชิก 5% และสะสมแต้ม 1 แต้มต่อ 100 บาท"""
    if member is not None:
        if member not in points_repo:
            points_repo[member] = 0
        total *= (1.0 - MEMBER_DISCOUNT_RATE)
        points_repo[member] += int(total / POINTS_PER_BAHT_RATIO)
    return total


def apply_coupon_discount(
    total: float, 
    coupon: str | None, 
    target_date: datetime.date | None
) -> float:
    """คำนวณส่วนลดจากคูปองโปรโมชัน"""
    if coupon is not None:
        if coupon == "SAVE50":
            total -= COUPON_SAVE50_AMOUNT
        elif coupon == "HALF":
            total *= COUPON_HALF_MULTIPLIER
        elif coupon == "NEWYEAR":
            date_to_check = target_date if target_date is not None else datetime.date.today()
            if date_to_check.month == 1:
                total *= (1.0 - COUPON_NEWYEAR_DISCOUNT)
    return total


def calc(
    items: list[tuple[str, int, float]], 
    member: str | None = None, 
    coupon: str | None = None, 
    today: datetime.date | None = None
) -> float:
    """
    ฟังก์ชันหลักในการคำนวณราคาสุทธิหลังหักส่วนลดและบวกภาษีมูลค่าเพิ่ม
    ขั้นตอนการคำนวณ:
    1. คำนวณยอดรวมและส่วนลดซื้อส่ง (Bulk Discount)
    2. คำนวณส่วนลดสมาชิกและบันทึกแต้ม
    3. คำนวณส่วนลดคูปอง
    4. ป้องกันยอดเงินติดลบ (Clamp at 0)
    5. บวกภาษีมูลค่าเพิ่ม 7% และปัดเศษทศนิยม 2 ตำแหน่ง
    6. บันทึกประวัติการคำนวณลงใน LOG
    """
    # 1. คำนวณ Subtotal และส่วนลดซื้อส่ง
    total = calculate_subtotal(items)

    # 2. คำนวณส่วนลดสมาชิก
    total = apply_member_discount_and_points(total, member, member_points)

    # 3. คำนวณส่วนลดคูปอง
    total = apply_coupon_discount(total, coupon, today)

    # 4. ป้องกันยอดติดลบ
    if total < 0.0:
        total = 0.0

    # 5. บวกภาษีและปัดเศษทศนิยม 2 ตำแหน่ง
    total += total * TAX_RATE
    final_total = round(total, 2)

    # 6. บันทึก Audit Log
    LOG.append((member, final_total))

    return final_total
