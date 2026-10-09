# Debugging Log - Lab 04

บันทึกกระบวนการตรวจจับข้อผิดพลาด (Bugs), การวิเคราะห์สาเหตุ (Root Cause Analysis), การแก้ไขโค้ดจริง และผลการรันชุดทดสอบ (Automated Tests)

---

## 1. รายการบั๊กและการแก้ไข (Defect Resolution Table)

| ID | ฟังก์ชัน / ตำแหน่ง | ประเภทปัญหา | สาเหตุของบั๊ก (Root Cause) | แนวทางแก้ไข (Fix Strategy) | ผลลัพธ์หลังแก้ |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **BUG-01** | `inventory.py` -> `restock` | Correctness / Validation | ไม่มีการตรวจค่า `amount <= 0` ทำให้ค่าติดลบไปลดสต็อก | เพิ่ม `if not isinstance(amount, int) or amount <= 0:` ให้โยน `ValueError` | ผ่าน ✅ |
| **BUG-02** | `inventory.py` -> `sell` | Silent Failure | เมื่อของไม่พอ ฟังก์ชันข้ามการตัดของและคืนค่าเดิมเงียบๆ | เพิ่มเงื่อนไขโยน `ValueError("สต็อกไม่เพียงพอ")` เมื่อ `amount > self.quantity` | ผ่าน ✅ |
| **BUG-03** | `discount.py` -> `calculate_discount` | Boundary Condition | ไม่จำกัดช่วงเปอร์เซ็นต์ส่วนลด ทำให้ส่งค่าติดลบหรือเกิน 100 ได้ | ตรวจสอบช่วง `0 <= discount_percent <= 100` หากหลุดช่วงให้โยน `ValueError` | ผ่าน ✅ |
| **BUG-04** | `discount.py` -> `calculate_discount` | Precision | ปัญหาเลขทศนิยมไม่รู้จบ (Floating Point) ในภาษา Python | ใช้ฟังก์ชัน `round(..., 2)` เพื่อคืนค่ายอดเงินทศนิยม 2 ตำแหน่ง | ผ่าน ✅ |
| **BUG-05** | `inventory.py` -> `sell_many` | Atomicity Failure | มีการหักของชิ้นแรกไปก่อน เมื่อชิ้นหลังไม่พอ ของหายฟรี | ทำ Pre-validation เช็กสต็อกทุกรายการให้ครบก่อนเริ่มหักจริง | ผ่าน ✅ |

---

## 2. ตัวอย่างการทดสอบและผลลัพธ์ (Test Execution Log)

### การทดสอบ `calculate_discount`:
- **Test Case 1 (Happy Path):** ราคา 100 บาท ส่วนลด 10% -> คืนค่า `90.0` บาท
- **Test Case 2 (Negative Discount):** ราคา 100 บาท ส่วนลด -10% -> เกิด `ValueError` ถูกต้อง
- **Test Case 3 (Over 100% Discount):** ราคา 100 บาท ส่วนลด 150% -> เกิด `ValueError` ถูกต้อง
- **Test Case 4 (Float Precision):** ราคา 99.99 บาท ส่วนลด 15% -> คืนค่า `84.99` บาท (ไม่เกิดเลขทศนิยมยาว)

### การทดสอบ `restock` และ `sell`:
- **Test Case 5 (Negative Restock):** ส่ง `restock(-5)` -> เกิด `ValueError` สต็อกคงเดิม
- **Test Case 6 (Over Sell):** สต็อกมี 2 ชิ้น สั่ง `sell(5)` -> เกิด `ValueError` สต็อกคงเดิม ไม่ลดลง

---

## 3. สรุปผลการรัน Test Suite

```text
============================= test session starts =============================
platform win32 -- Python 3.x, pytest-x.x.x
rootdir: swe-inventory-67332110058-4
collected 12 items

tests/test_inventory.py ......                                           [ 50%]
tests/test_discount.py ......                                            [100%]

============================== 12 passed in 0.15s ==============================