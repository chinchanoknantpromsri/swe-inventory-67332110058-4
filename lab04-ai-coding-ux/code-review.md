# Code Review: AI-Generated Pull Request - Lab 04

การตรวจทานโค้ด (Code Review) ที่สร้างโดย AI Coding Assistant สำหรับระบบ Inventory Management เพื่อวิเคราะห์ข้อผิดพลาดเชิงตรรกะ สถาปัตยกรรม และความปลอดภัย

---

## 1. ตารางสรุปรายการ Bug และประเด็นที่พบ (Summary of Issues)

| ลำดับ | ตำแหน่ง (Function/Method) | รายละเอียด Bug ที่พบ | ระดับความรุนแรง | แนวทางการแก้ไข (Fix Strategy) |
| :---: | :--- | :--- | :---: | :--- |
| 1 | `restock(amount)` | รับค่าจำนวนติดลบหรือ 0 ได้ ทำให้สต็อกลดลงแทนที่จะเพิ่มขึ้น | **Critical** | เพิ่ม Validation: `amount > 0` และเป็นจำนวนเต็ม หากไม่ใช่ให้ raise `ValueError` |
| 2 | `sell(amount)` | เกิด Silent Failure เมื่อสั่งขายมากกว่าสต็อกที่มี และยอมให้สต็อกติดลบได้ | **Critical** | ตรวจสอบ `amount <= self.quantity` ก่อนตัด หากไม่พอให้ raise `ValueError` ห้ามคืนค่าเงียบๆ |
| 3 | `calculate_discount()` | ยอมรับค่าเปอร์เซ็นต์ส่วนลดติดลบหรือมากกว่า 100% ทำให้ราคาสินค้าเพิ่มขึ้นหรือติดลบ | **High** | จำกัดขอบเขต `0 <= discount <= 100` พร้อม raise `ValueError` |
| 4 | `apply_promo_code()` | ตรวจสอบแบบ Case-Sensitive และไม่ได้เช็กวันหมดอายุของโค้ดโปรโมชัน | **Medium** | แปลงโค้ดเป็น `.upper()` และเพิ่มการตรวจสอบสถานะ/วันหมดอายุ |
| 5 | `export_to_json()` | ขาดการระบุ `encoding='utf-8'` และ `ensure_ascii=False` ทำให้ชื่อภาษาไทยกลายเป็น unicode escape sequence | **Medium** | กำหนดพารามิเตอร์ `open(..., encoding='utf-8')` และ `json.dump(..., ensure_ascii=False)` |
| 6 | `search_items(query)` | เกิด `AttributeError` เมื่อเจอชื่อว่าง/None และไม่รองรับการค้นหาแบบไม่สนตัวพิมพ์เล็ก-ใหญ่ | **Low** | แปลง query และชื่อสินค้าเป็น `.lower()` พร้อมตรวจสอบว่าฟิลด์ไม่เป็น `None` ก่อนค้นหา |

---

## 2. รายละเอียดการวิเคราะห์จุดบกพร่อง (Deep Dive & Code Comparison)

### จุดที่ 1: บั๊กในฟังก์ชัน `restock` (Negative/Zero Restock)
- **โค้ดที่ AI สร้าง:**
  ```python
  def restock(self, amount: int):
      self.quantity += amount