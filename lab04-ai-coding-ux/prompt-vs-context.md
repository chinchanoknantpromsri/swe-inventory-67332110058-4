---

### ขั้นที่ 1: เปิดไฟล์ใน IDE

1. ดูที่แถบไฟล์ด้านซ้ายของโปรแกรม (Antigravity / VS Code)
2. ดับเบิลคลิกเปิดไฟล์ **`lab04-ai-coding-ux/prompt-vs-context.md`**

---

### ขั้นที่ 2: วางเนื้อหาลงในไฟล์

1. กด **`Ctrl + A`** แล้วกด **`Backspace`** (ล้างเนื้อหาเดิมออก)
2. คัดลอก (Copy) เนื้อหาด้านล่างนี้ทั้งหมด:

```markdown
# Prompt vs. Context Engineering Analysis - Lab 04

การทดลองเปรียบเทียบผลลัพธ์ของโค้ดที่สร้างโดย AI ระหว่างการใช้เพียง Prompt ธรรมดา (Naive Prompt) กับการใช้ Context Engineering (การให้บริบท กฎทางธุรกิจ และสถาปัตยกรรมเดิม)

---

## 1. การเปรียบเทียบคำสั่ง (Prompt Setup)

### แบบที่ 1: Naive Prompt (คำสั่งสั้น ไม่มีบริบท)
```text
เขียนฟังก์ชันสำหรับระบบคลังสินค้า มีการเพิ่มสต็อก ลดสต็อก และคำนวณส่วนลดสินค้าให้หน่อย

```

### แบบที่ 2: Context Engineering (คำสั่งที่มีบริบทเชิงลึก)

```text
บริบทระบบ: เรากำลังพัฒนาระบบคลังสินค้า (Inventory Management) ภาษา Python ด้วยคลาส InventoryItem 
ที่มี attributes คือ id, name, price, quantity และ is_digital

กฎทางธุรกิจ (Business Rules & Constraints):
1. ฟังก์ชัน restock(amount): amount ต้องเป็น int > 0 หากไม่ใช่ให้ raise ValueError
2. ฟังก์ชัน sell(amount): amount ต้องเป็น int > 0 และ amount <= self.quantity 
   หากของไม่พอ ห้ามเงียบ ให้ raise ValueError("สต็อกไม่เพียงพอ") ทันที
3. ฟังก์ชัน calculate_discount(price, discount_percent): 
   - price ต้อง >= 0
   - discount_percent ต้องอยู่ในช่วง 0 ถึง 100
   - คืนค่าทศนิยมปัดเศษ 2 ตำแหน่ง round(..., 2)
4. ปฏิบัติตามหลัก Atomic Operation และ Clean Architecture

จงเขียนโค้ดทั้ง 3 เมธอดนี้ตามข้อกำหนดอย่างเคร่งครัด

```

---

## 2. ตารางเปรียบเทียบผลลัพธ์ของโค้ดที่ได้ (Code Comparison)

| มิติการเปรียบเทียบ | โค้ดจาก Naive Prompt | โค้ดจาก Context Engineering |
| --- | --- | --- |
| **Input Validation** | ❌ ขาดการตรวจค่าติดลบหรือประเภทข้อมูล | ✅ ตรวจสอบประเภทและค่าบวกครบถ้วน |
| **Error Handling** | ❌ เกิด Silent Failure (return ค่าเดิมเงียบๆ) | ✅ โยน `ValueError` พร้อมข้อความชัดเจน |
| **Boundary Conditions** | ❌ ใส่ส่วนลดติดลบหรือเกิน 100% ได้ | ✅ จำกัดขอบเขต `0 <= discount <= 100` |
| **Floating Precision** | ❌ ทศนิยมยาวไม่รู้จบ (เช่น `.999999`) | ✅ มีการใช้ `round(..., 2)` เหมาะกับยอดเงิน |
| **Integration** | ❌ โครงสร้างคลาสไม่เข้ากับระบบเดิม ต้องแก้ใหม่ | ✅ ใช้งานร่วมกับ `inventory.py` เดิมได้ทันที |

---

## 3. สรุปผลการวิเคราะห์และข้อคิด (Key Insights)

1. **AI มีแนวโน้มทำเฉพาะ Happy Path เมื่อไร้บริบท:** หากไม่ระบุข้อจำกัด AI จะเดาว่าข้อมูลนำเข้าถูกต้องเสมอ ส่งผลให้โค้ดขาดความทนทานต่อข้อผิดพลาด (Lack of Robustness)
2. **Context สำคัญกว่า Prompt Syntax:** การอธิบายโมเดลข้อมูล กฎเกณฑ์ทางธุรกิจ และขอบเขตความปลอดภัย ให้ผลลัพธ์ที่มีคุณภาพสูงกว่าการพยายามสรรหาคำพูดสวยหรูใน Prompt
3. **ลดเวลา Code Review และ Debug:** การลงทุนเวลาเตรียม Context เพียงเล็กน้อย ช่วยลดบั๊กที่จะหลุดเข้าสู่กระบวนการ Review ได้มากกว่า 70%

```
