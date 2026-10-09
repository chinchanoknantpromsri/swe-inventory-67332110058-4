# Debugging Log - Lab 04

บันทึกกระบวนการสืบสวนและแก้ไขข้อผิดพลาด (Evidence-Based Debugging Log) ตามระเบียบวิธี 5 ขั้นตอน (Reproduce, Traceback, สมมติฐาน, พิสูจน์ยืนยัน, แก้ไขและ Re-run) สำหรับโมดูล `discount.py` และชุดทดสอบ `tests/test_discount.py`

---

## 1. ขั้นตอนที่ 1: การทำให้เกิดข้อผิดพลาดซ้ำ (Reproduce)

สั่งรันชุดทดสอบก่อนแก้ไขโค้ดจากโฟลเดอร์ `lab04-ai-coding-ux/` ด้วยคำสั่ง:
```bash
python -m pytest tests/test_discount.py -v
```

### ผลลัพธ์ Traceback ก่อนแก้ไข (Initial Test Failure Output):

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: swe-inventory-67332110058-4\lab04-ai-coding-ux
collected 6 items

tests/test_discount.py::test_apply_discount_basic FAILED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total FAILED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty FAILED                  [ 83%]
tests/test_discount.py::test_cheapest_n FAILED                           [100%]

=================================== FAILURES ===================================
__________________________ test_apply_discount_basic ___________________________
    def test_apply_discount_basic():
>       assert apply_discount(100.0, 10) == 90.0
E       assert 99.9 == 90.0
E        +  where 99.9 = apply_discount(100.0, 10)
tests\test_discount.py:12: AssertionError

_______________________________ test_bulk_total ________________________________
    def test_bulk_total():
>       assert bulk_total([100.0, 100.0, 100.0], 10) == 270.0
E       assert 299.9 == 270.0
E        +  where 299.9 = bulk_total([100.0, 100.0, 100.0], 10)
tests\test_discount.py:22: AssertionError

___________________________ test_average_price_empty ___________________________
    def test_average_price_empty():
>       assert average_price([]) == 0.0
discount.py:16: in average_price
    return sum(prices) / len(prices)
E   ZeroDivisionError: division by zero
tests\test_discount.py:32: ZeroDivisionError

_______________________________ test_cheapest_n ________________________________
    def test_cheapest_n():
>       assert cheapest_n([50.0, 10.0, 30.0, 20.0], 2) == [10.0, 20.0]
E       AssertionError: assert [20.0] == [10.0, 20.0]
E         Right contains one more item: 20.0
E         Use -v to get more diff
tests\test_discount.py:37: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_discount.py::test_apply_discount_basic - assert 99.9 == 90.0
FAILED tests/test_discount.py::test_bulk_total - assert 299.9 == 270.0
FAILED tests/test_discount.py::test_average_price_empty - ZeroDivisionError: division by zero
FAILED tests/test_discount.py::test_cheapest_n - AssertionError: assert [20.0] == [10.0, 20.0]
========================= 4 failed, 2 passed in 0.08s ==========================
```

**สรุปสถานะเริ่มต้น:** พบเทสต์ล้มเหลวจำนวน 4 รายการ และผ่านเพียง 2 รายการ

> **กับดักที่ตั้งใจวางไว้ (Trap Analysis):**
> * `test_apply_discount_zero` ผ่าน (`250.0 - 0/100 = 250.0`) ทั้งที่สูตรผิด เพราะเมื่อ `percent = 0` พจน์ลบมีค่าเป็นศูนย์ ทำให้ค่าบังเอิญตรงกัน
> * `test_average_price` ผ่าน เมื่อมีสมาชิกในลิสต์ แต่แครชทันทีเมื่อเป็นลิสต์ว่าง

---

## 2. ขั้นตอนที่ 2-4: วิเคราะห์ Root Cause และพิสูจน์ยืนยันทีละข้อ

### ตารางสรุปการสืบสวนและแก้ไขข้อผิดพลาด (Root Cause Analysis Table)

| Test ที่ไม่ผ่าน | Traceback / Assertion ที่เห็น | สมมติฐาน Root Cause | วิธียืนยันสมมติฐาน | แนวทางการแก้ไขที่ตรงจุด |
| :--- | :--- | :--- | :--- | :--- |
| **`test_apply_discount_basic`** | `AssertionError: assert 99.9 == 90.0` | ฟังก์ชันใช้สูตร `price - percent / 100` ซึ่งแทนที่จะลด `10%` ของราคา กลับกลายเป็นเอา `100 - (10/100) = 100 - 0.1 = 99.9` (สูตรคณิตศาสตร์ผิด) | ทดลองรันใน Python REPL: `100.0 - 10/100` ได้ `99.9` แต่สูตรที่ถูกต้องคือ `100.0 * (1 - 10/100) = 90.0` | แก้ไขสูตรคำนวณเป็น `return price * (1 - percent / 100)` |
| **`test_bulk_total`** | `AssertionError: assert 299.9 == 270.0` | ข้อผิดพลาดสืบเนื่องมาจากฟังก์ชัน `apply_discount` ที่คำนวณส่วนลดผิด ยอดรวม `300.0` ถูกลดไปเพียง `0.1` บาท กลายเป็น `299.9` แทนที่จะเป็น `270.0` | เมื่อแก้ `apply_discount` ในข้อแรก ทดลองเรียก `bulk_total([100, 100, 100], 10)` ผลลัพธ์ได้ `270.0` ทันที | ปรับปรุงฟังก์ชัน `apply_discount` และเขียนรวมราคาให้กระชับด้วย `total = sum(prices)` |
| **`test_average_price_empty`** | `ZeroDivisionError: division by zero` ที่บรรทัด `sum(prices) / len(prices)` | เมื่ออาร์กิวเมนต์ `prices` เป็นลิสต์ว่าง `[]` ขนาด `len(prices)` มีค่าเท่ากับ `0` ทำให้เกิดการหารด้วยศูนย์ | ตรวจสอบประเภทและขนาดของ `prices` ด้วยเงื่อนไข `if not prices:` พบว่าเข้าเงื่อนไขเมื่อเป็นลิสต์ว่าง | เพิ่ม Guard Clause ตรวจสอบลิสต์ว่าง `if not prices: return 0.0` ก่อนทำการหาร |
| **`test_cheapest_n`** | `AssertionError: assert [20.0] == [10.0, 20.0]` | โค้ดใช้ List Slicing ผิดตำแหน่งเป็น `ordered[1:n]` ซึ่งดัชนีใน Python เริ่มที่ `0` ทำให้ข้ามสมาชิกตัวแรกที่ถูกที่สุด (ดัชนี 0) ไป และได้จำนวนสมาชิกเพียง `n-1` ตัว | ข้อมูลเรียงลำดับคือ `[10.0, 20.0, 30.0, 50.0]` การตัด `[1:2]` จะได้เฉพาะ `[20.0]` แต่ถ้าตัด `[:2]` จะได้ `[10.0, 20.0]` | แก้ไข Slicing ให้เริ่มจากดัชนีแรกเป็น `ordered[:n]` หรือ `ordered[0:n]` |

---

## 3. ขั้นตอนที่ 5: การแก้ไขโค้ดจริง (Code Implementation)

โค้ด `discount.py` หลังการแก้ไข Root Cause ครบทุกจุด:

```python
# discount.py -- โมดูลคิดส่วนลดและสรุปยอด (ฉบับแก้ไขบั๊กครบถ้วนตาม Root Cause)

def apply_discount(price: float, percent: float) -> float:
    """ลดราคาตาม percent (0-100) คืนราคาหลังลด"""
    if price < 0:
        raise ValueError("ราคาต้องไม่ติดลบ")
    if not (0 <= percent <= 100):
        raise ValueError("เปอร์เซ็นต์ส่วนลดต้องอยู่ระหว่าง 0 ถึง 100")
    return price * (1 - percent / 100)


def bulk_total(prices: list, discount_percent: float) -> float:
    """รวมราคาหลายรายการแล้วลดส่วนลดรวมทีเดียว"""
    total = sum(prices)
    return apply_discount(total, discount_percent)


def average_price(prices: list) -> float:
    """คืนราคาเฉลี่ยของรายการสินค้า (หากคลังว่างคืน 0.0 ไม่แครช)"""
    if not prices:
        return 0.0
    return sum(prices) / len(prices)


def cheapest_n(prices: list, n: int) -> list:
    """คืน n รายการที่ราคาถูกที่สุด เรียงจากถูกไปแพง (เริ่มจากดัชนี 0)"""
    ordered = sorted(prices)
    return ordered[:n]
```

---

## 4. ผลการรัน Test Suite หลังการแก้ไข (Final Verification)

รันคำสั่งทดสอบอีกครั้งเพื่อยืนยันว่าการแก้ไขผ่านครบทุกข้อและไม่กระทบฟังก์ชันอื่น:

```bash
python -m pytest tests/test_discount.py -v
```

### ผลลัพธ์ใน Terminal:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: swe-inventory-67332110058-4\lab04-ai-coding-ux
collected 6 items

tests/test_discount.py::test_apply_discount_basic PASSED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total PASSED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty PASSED                  [ 83%]
tests/test_discount.py::test_cheapest_n PASSED                           [100%]

============================== 6 passed in 0.05s ==============================
```

✅ **ผลลัพธ์:** ชุดทดสอบทั้ง 6 รายการผ่านครบถ้วนสมบูรณ์ 100%

---

## 5. บันทึกข้อความ Commit ที่สื่อความหมาย (Meaningful Commits)

ตัวอย่างข้อความ Git Commit ที่ระบุ Root Cause ตามข้อกำหนดของแล็บ:

1. `fix(discount): แก้ไขสูตรคำนวณส่วนลดเปอร์เซ็นต์ใน apply_discount จากการลบตรงๆ เป็นการคูณสัดส่วน`
2. `fix(discount): เพิ่ม Guard Clause ใน average_price คืนค่า 0.0 เมื่อคลังว่าง ป้องกัน ZeroDivisionError`
3. `fix(discount): ปรับปรุง list slicing ใน cheapest_n ให้เริ่มต้นจากดัชนี 0 ([:n]) เพื่อไม่ให้ข้ามสินค้าที่ถูกที่สุด`