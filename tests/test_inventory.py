# tests/test_inventory.py
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from inventory import Inventory, InventoryItem


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
