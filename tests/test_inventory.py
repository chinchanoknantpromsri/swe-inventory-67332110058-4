# tests/test_inventory.py
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from inventory import Inventory

# ==========================================
# ชุดทดสอบพื้นฐานของ Inventory
# ==========================================

def test_add_item_success():
    inv = Inventory()
    item = inv.add_item("น้ำมันเครื่อง", 10, 250.0)
    assert item.name == "น้ำมันเครื่อง"
    assert item.quantity == 10
    assert item.price == 250.0


def test_add_item_duplicate_name():
    inv = Inventory()
    inv.add_item("น้ำมันเครื่อง", 10, 250.0)
    with pytest.raises(ValueError, match="มีอยู่ในระบบแล้ว"):
        inv.add_item("น้ำมันเครื่อง", 5, 250.0)


def test_restock_success():
    inv = Inventory()
    inv.add_item("กรองน้ำมัน", 5, 120.0)
    new_qty = inv.restock("กรองน้ำมัน", 10)
    assert new_qty == 15


def test_sell_success():
    inv = Inventory()
    inv.add_item("ผ้าเบรก", 8, 500.0)
    remaining = inv.sell("ผ้าเบรก", 3)
    assert remaining == 5


# ==========================================
# ขั้นที่ 4: ชุดทดสอบเสริมสำหรับ sell()
# ครอบคลุมทั้ง 4 กลุ่ม: ค่าขอบ, ค่าที่ไม่ควรรับ, เส้นทาง error, ชนิดข้อมูล
# ==========================================

def test_sell_exact_inventory_to_zero():
    # 1. กลุ่มค่าขอบ: ขายหมดพอดีเท่ากับจำนวนคงเหลือทั้งหมด -> สต็อกต้องเหลือ 0
    inv = Inventory()
    inv.add_item("ยางปัดน้ำฝน", 5, 150.0)
    remaining = inv.sell("ยางปัดน้ำฝน", 5)
    assert remaining == 0


def test_sell_zero_amount():
    # 2. กลุ่มค่าที่ไม่ควรรับ: ขายจำนวน 0 ชิ้น -> ต้อง raise ValueError
    inv = Inventory()
    inv.add_item("หัวเทียน", 10, 80.0)
    with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
        inv.sell("หัวเทียน", 0)


def test_sell_negative_amount():
    # 2. กลุ่มค่าที่ไม่ควรรับ: ขายจำนวนติดลบ -> ต้อง raise ValueError
    inv = Inventory()
    inv.add_item("หัวเทียน", 10, 80.0)
    with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
        inv.sell("หัวเทียน", -4)


def test_sell_exceeding_inventory():
    # 2. กลุ่มค่าที่ไม่ควรรับ: ขายเกินจำนวนคงเหลือ -> ต้อง raise ValueError และสต็อกไม่ลด
    inv = Inventory()
    inv.add_item("แบตเตอรี่", 3, 2200.0)
    with pytest.raises(ValueError, match="ไม่เพียงพอสำหรับการขาย"):
        inv.sell("แบตเตอรี่", 4)
    # ยืนยันว่าสต็อกต้องไม่ถูกหัก
    assert inv._items["แบตเตอรี่"].quantity == 3


def test_sell_non_existent_item():
    # 3. กลุ่มเส้นทาง Error: ขายสินค้าที่ไม่มีในคลัง -> ต้อง raise KeyError พร้อมชื่อสินค้า
    inv = Inventory()
    inv.add_item("สายพาน", 5, 300.0)
    with pytest.raises(KeyError, match="ไม่พบสินค้า 'ล้อแม็ก' ในระบบ"):
        inv.sell("ล้อแม็ก", 1)


def test_sell_invalid_type_string():
    # 4. กลุ่มชนิดข้อมูล: ใส่จำนวนเป็นข้อความ -> ต้อง raise TypeError
    inv = Inventory()
    inv.add_item("หลอดไฟ", 10, 50.0)
    with pytest.raises(TypeError):
        inv.sell("หลอดไฟ", "สอง")



def test_get_total_value():
    inv = Inventory()
    inv.add_item("สินค้า A", 2, 100.0)
    inv.add_item("สินค้า B", 3, 200.0)
    assert inv.get_total_value() == 800.0


# ==========================================
# ขั้นที่ 2: TDD Red Phase - low_stock_items
# ครบทั้ง 6 กรณีตามข้อกำหนดของ Lab 5
# ==========================================

def test_low_stock_all_above_threshold():
    # กรณีที่ 1: สินค้าทุกรายการมีจำนวนมากกว่า threshold -> คืน list ว่าง
    inv = Inventory()
    inv.add_item("สินค้า A", 20, 100.0)
    inv.add_item("สินค้า B", 15, 150.0)
    assert inv.low_stock_items(10) == []


def test_low_stock_exact_threshold():
    # กรณีที่ 2: มีสินค้าที่จำนวนเท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย
    inv = Inventory()
    inv.add_item("สินค้า A", 5, 100.0)
    inv.add_item("สินค้า B", 12, 150.0)
    assert inv.low_stock_items(5) == ["สินค้า A"]


def test_low_stock_multiple_sorted_alphabetically():
    # กรณีที่ 3: มีสินค้าเข้าเกณฑ์หลายรายการ -> ผลลัพธ์เรียงตามชื่อ ไม่ใช่ตามลำดับที่เพิ่ม
    inv = Inventory()
    inv.add_item("ส้ม", 2, 50.0)
    inv.add_item("กล้วย", 3, 30.0)
    inv.add_item("มะม่วง", 1, 40.0)
    # เพิ่มตามลำดับ: ส้ม -> กล้วย -> มะม่วง
    # ผลลัพธ์ต้องเรียงตามตัวอักษร: กล้วย -> มะม่วง -> ส้ม
    assert inv.low_stock_items(5) == ["กล้วย", "มะม่วง", "ส้ม"]


def test_low_stock_empty_inventory():
    # กรณีที่ 4: คลังว่าง -> คืน list ว่าง ไม่ใช่ error
    inv = Inventory()
    assert inv.low_stock_items(5) == []


def test_low_stock_zero_threshold():
    # กรณีที่ 5: threshold เป็น 0 -> คืนเฉพาะสินค้าที่เหลือ 0
    inv = Inventory()
    inv.add_item("สินค้าหมด", 0, 100.0)
    inv.add_item("สินค้ามีของ", 3, 100.0)
    assert inv.low_stock_items(0) == ["สินค้าหมด"]


def test_low_stock_negative_threshold():
    # กรณีที่ 6: threshold ติดลบ -> ตัดสินใจคืน list ว่าง เนื่องจากจำนวนสินค้าไม่ติดลบ
    inv = Inventory()
    inv.add_item("สินค้า A", 0, 100.0)
    inv.add_item("สินค้า B", 5, 100.0)
    assert inv.low_stock_items(-1) == []


# ==========================================
# ชุดทดสอบ Validation เพิ่มเติมสำหรับ InventoryItem และ restock
# ==========================================

def test_item_empty_name():
    with pytest.raises(ValueError, match="ชื่อสินค้าต้องไม่ว่างเปล่า"):
        Inventory().add_item("   ", 10, 100.0)


def test_item_negative_quantity():
    with pytest.raises(ValueError, match="จำนวนสินค้าต้องไม่ติดลบ"):
        Inventory().add_item("สินค้า", -1, 100.0)


def test_item_invalid_price():
    with pytest.raises(ValueError, match="ราคาต้องมากกว่าศูนย์"):
        Inventory().add_item("สินค้า", 10, 0.0)


def test_restock_non_existent_item():
    inv = Inventory()
    with pytest.raises(KeyError, match="ไม่พบสินค้า 'ไม่มีจริง' ในระบบ"):
        inv.restock("ไม่มีจริง", 5)


def test_restock_negative_amount():
    inv = Inventory()
    inv.add_item("หัวเทียน", 5, 100.0)
    with pytest.raises(ValueError, match="จำนวนที่เติมต้องมากกว่าศูนย์"):
        inv.restock("หัวเทียน", 0)

