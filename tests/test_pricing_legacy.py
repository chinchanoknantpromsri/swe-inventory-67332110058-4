# tests/test_pricing_legacy.py
# Characterization Tests บันทึกพฤติกรรมจริงของ pricing_legacy.py ครบทุกกลุ่มกรณี
import datetime

import pytest

# ชี้ไปยังโมดูลที่จัดโค้ดใหม่ (pricing.py) เพื่อพิสูจน์ว่าพฤติกรรมไม่เปลี่ยน
import pricing as pricing_legacy


@pytest.fixture(autouse=True)
def reset_legacy_globals():
    """
    ล้างค่าตัวแปร Global (member_points และ LOG) ก่อนเริ่มทุก test
    เพื่อป้องกันไม่ให้ค่าค้างข้ามการเรียกฟังก์ชันแต่ละครั้ง
    ทำให้ test ผ่านครบทั้งตอนรันทีละข้อและตอนรันทั้งไฟล์
    """
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()
    yield
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()


# ==========================================================
# 1. กลุ่มราคาปกติ (Normal Pricing)
# สินค้า 1 รายการ จำนวนน้อย ไม่ใช้สิทธิ์ใดๆ
# ==========================================================
def test_pricing_normal():
    # 10 ชิ้น * 100 บาท = 1,000 + VAT 7% = 1,070.0
    items = [("น้ำมันเครื่อง", 10, 100.0)]
    result = pricing_legacy.calc(items)
    assert result == 1070.0


# ==========================================================
# 2. กลุ่มซื้อจำนวนมาก (Bulk Discount Tiers)
# บันทึกค่าที่จำนวนเท่ากับเกณฑ์แต่ละขั้นพอดี (50 และ 100 ชิ้น)
# ==========================================================
def test_pricing_bulk_tier_50():
    # 50 ชิ้น * 10 บาท = 500 * ลด 5% (0.95) = 475.0 + VAT 7% = 508.25
    items = [("น็อตตัวเมีย", 50, 10.0)]
    result = pricing_legacy.calc(items)
    assert result == 508.25


def test_pricing_bulk_tier_100():
    # 100 ชิ้น * 10 บาท = 1,000 * ลด 10% (0.90) = 900.0 + VAT 7% = 963.0
    items = [("น็อตตัวผู้", 100, 10.0)]
    result = pricing_legacy.calc(items)
    assert result == 963.0


# ==========================================================
# 3. กลุ่มจำนวนเป็นศูนย์ (Zero Quantity)
# สินค้าที่ใส่จำนวน 0 ชิ้น
# ==========================================================
def test_pricing_zero_quantity():
    # จำนวน 0 ชิ้น ฟังก์ชันข้ามการคำนวณ -> ผลรวม 0.0 + VAT = 0.0
    items = [("สินค้าทดสอบ", 0, 100.0)]
    result = pricing_legacy.calc(items)
    assert result == 0.0


# ==========================================================
# 4. กลุ่มสมาชิก (Member Discount & Loyalty Points)
# บันทึกทั้งยอดเงินที่ลด 5% และแต้มที่สมาชิกได้รับ (1 แต้มต่อ 100 บาท)
# ==========================================================
def test_pricing_member_discount_and_points():
    # 10 ชิ้น * 100 บาท = 1,000 * สมาชิกลด 5% (0.95) = 950.0
    # แต้ม: int(950 / 100) = 9 แต้ม
    # ยอดสุทธิ: 950.0 + VAT 7% = 1016.5
    items = [("หัวเทียน", 10, 100.0)]
    result = pricing_legacy.calc(items, member="สมชาย")
    assert result == 1016.5
    assert pricing_legacy.member_points["สมชาย"] == 9


# ==========================================================
# 5. กลุ่มคูปอง (Coupon Codes)
# รหัส SAVE50, HALF, และ NEWYEAR (ทั้งในเดือน ม.ค. และนอกเดือน ม.ค.)
# ==========================================================
def test_pricing_coupon_save50():
    # 10 ชิ้น * 10 บาท = 100.0 - 50 = 50.0 + VAT 7% = 53.5
    items = [("แหวนรอง", 10, 10.0)]
    result = pricing_legacy.calc(items, coupon="SAVE50")
    assert result == 53.5


def test_pricing_coupon_half():
    # 10 ชิ้น * 10 บาท = 100.0 * 0.5 = 50.0 + VAT 7% = 53.5
    items = [("แหวนรอง", 10, 10.0)]
    result = pricing_legacy.calc(items, coupon="HALF")
    assert result == 53.5


def test_pricing_coupon_newyear_in_january():
    # 10 ชิ้น * 10 บาท = 100.0 * ลด 20% (0.8) = 80.0 + VAT 7% = 85.6
    items = [("แหวนรอง", 10, 10.0)]
    january_date = datetime.date(2026, 1, 15)
    result = pricing_legacy.calc(items, coupon="NEWYEAR", today=january_date)
    assert result == 85.6


def test_pricing_coupon_newyear_outside_january():
    # นอกเดือนมกราคม คูปอง NEWYEAR ใช้ไม่ได้: 100.0 + VAT 7% = 107.0
    items = [("แหวนรอง", 10, 10.0)]
    other_date = datetime.date(2026, 8, 20)
    result = pricing_legacy.calc(items, coupon="NEWYEAR", today=other_date)
    assert result == 107.0


# ==========================================================
# 6. กลุ่มยอดติดลบ (Negative Clamping)
# ส่วนลดมากกว่าราคาสินค้า เช่น สินค้า 10 บาท ใช้คูปอง SAVE50
# ==========================================================
def test_pricing_negative_clamping():
    # 1 ชิ้น * 10 บาท = 10.0 - 50 = -40.0 -> ฟังก์ชันปรับเป็น 0.0 + VAT = 0.0
    items = [("สายไฟ", 1, 10.0)]
    result = pricing_legacy.calc(items, coupon="SAVE50")
    assert result == 0.0


# ==========================================================
# 7. กลุ่มค่าที่ฟังก์ชันเก็บไว้ (Internal State / Audit Log)
# บันทึก Tuple (member, total) ลงใน LOG ทุกครั้งที่เรียกใช้
# ==========================================================
def test_pricing_audit_log():
    items = [("กรองอากาศ", 2, 200.0)]
    result = pricing_legacy.calc(items, member="วิชัย")
    assert len(pricing_legacy.LOG) == 1
    assert pricing_legacy.LOG[0] == ("วิชัย", result)
