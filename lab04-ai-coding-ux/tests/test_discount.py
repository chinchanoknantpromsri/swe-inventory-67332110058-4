import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from discount import calculate_discount

def test_calculate_discount_normal():
    # กรณีคิดส่วนลดปกติทั่วไป (Happy Path)
    assert calculate_discount(100.0, 10.0) == 90.0
    assert calculate_discount(200.0, 25.0) == 150.0


def test_calculate_discount_zero_discount():
    # กรณีไม่มีส่วนลด (0%)
    assert calculate_discount(150.0, 0.0) == 150.0


def test_calculate_discount_full_discount():
    # กรณีลด 100% (ของฟรี)
    assert calculate_discount(500.0, 100.0) == 0.0


def test_calculate_discount_floating_precision():
    # กรณีทศนิยมต้องปัดเศษ 2 ตำแหน่ง
    assert calculate_discount(99.99, 15.0) == 84.99


def test_calculate_discount_negative_discount():
    # กรณีส่งเปอร์เซ็นต์ติดลบ ต้อง raise ValueError
    with pytest.raises(ValueError, match="เปอร์เซ็นต์ส่วนลดต้องอยู่ระหว่าง 0 ถึง 100"):
        calculate_discount(100.0, -10.0)


def test_calculate_discount_exceed_hundred():
    # กรณีส่งส่วนลดเกิน 100% ต้อง raise ValueError
    with pytest.raises(ValueError, match="เปอร์เซ็นต์ส่วนลดต้องอยู่ระหว่าง 0 ถึง 100"):
        calculate_discount(100.0, 150.0)


def test_calculate_discount_negative_price():
    # กรณีราคาสินค้าติดลบ ต้อง raise ValueError
    with pytest.raises(ValueError, match="ราคาสินค้าต้องไม่ติดลบ"):
        calculate_discount(-50.0, 10.0)