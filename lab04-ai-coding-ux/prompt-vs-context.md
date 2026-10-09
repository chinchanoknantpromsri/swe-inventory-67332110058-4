# Prompt vs. Context Engineering Analysis - Lab 04

การทดลองและเปรียบเทียบผลลัพธ์ระหว่างการสั่งงาน AI ด้วย Prompt ธรรมดา (Naive Prompt) กับการป้อนบริบทเชิงลึก (Context Engineering) ในระบบ Inventory Management

---

## 1. การทดลองสั่งงานรอบที่ 1: Prompt ธรรมดา (ไม่มี Context)

### คำสั่ง Prompt (รอบที่ 1):
```text
เขียนฟังก์ชัน sell_many ใน Python ให้หน่อย รับสต็อกสินค้ากับรายการที่ลูกค้าจะซื้อ ตัดสต็อกแล้วบอกว่าขายได้ไหม

```

### ผลลัพธ์โค้ดที่ AI สร้างขึ้น (รอบที่ 1):

```python
def sell_many(inventory, items_to_sell):
    """
    ลด stock สินค้าหลายรายการ
    items_to_sell: dict ของ {item_name: quantity}
    """
    for item, qty in items_to_sell.items():
        if item in inventory:
            if inventory[item] >= qty:
                inventory[item] -= qty
            else:
                return f"Error: สินค้า {item} มีไม่พอ"
        else:
            return f"Error: ไม่พบสินค้า {item}"
    return "ขายสำเร็จทั้งหมด"

```

### การประเมินผลลัพธ์รอบที่ 1:

1. **เข้ากับโค้ดเดิมไม่ได้ (Interface Mismatch):** AI สันนิษฐานว่า `inventory` คือ `dict[str, int]` ธรรมดา ไม่ได้เรียกใช้คลาส `Inventory` หรือออบเจกต์ `InventoryItem` ที่มีอยู่ในโปรเจกต์จริง
2. **ละเมิดหลัก Atomicity อย่างร้ายแรง:** มีการหักยอดสินค้าชิ้นแรก ๆ ไปแล้ว (`inventory[item] -= qty`) ก่อนที่จะพบว่าสินค้าชิ้นถัดไปสต็อกไม่พอ ทำให้ข้อมูลสินค้าชิ้นแรกถูกหักไปฟรี ๆ โดยไม่มีการย้อนคืน (Rollback)
3. **การจัดการ Exception ผิดหลักวิศวกรรม:** ส่งคืนข้อความ `str` แทนที่จะ Raise Exception ตามมาตรฐานของระบบ (เช่น `KeyError`, `ValueError`)
4. **ไม่มีการตรวจสอบความถูกต้อง (Input Validation):** ไม่เช็กจำนวนติดลบหรือสต็อกที่เป็นศูนย์

---

## 2. การทดลองสั่งงานรอบที่ 2: Prompt ที่มี Context ครบถ้วน (Context Engineering)

### บริบทที่ป้อนให้ AI (Context Provided):

* **โครงสร้างคลาสเดิม:** อิงจาก `InventoryItem(id, name, price, quantity, is_digital)` และเมธอด `sell()` ใน `inventory.py`
* **กฎทางธุรกิจ (Business Rules):**
* การขายหลายรายการต้องทำงานแบบ **All-or-Nothing (Atomic)** หากชิ้นใดชิ้นหนึ่งไม่พอ ต้องไม่หักสินค้าใด ๆ เลย
* ต้องตรวจสอบว่าจำนวนที่ขอซื้อ (`qty`) ต้องเป็นจำนวนเต็มบวก (`int > 0`)
* หากสินค้าไม่พอหรือไม่มีสินค้า ต้องโยน `ValueError` หรือ `KeyError` ไม่ใช้การ return ข้อความสตริง



### คำสั่ง Prompt (รอบที่ 2):

```text
บริบทระบบ: เรามีคลาส InventoryItem เก็บ attributes: name, price, quantity และมีคลาส Inventory เก็บ self.items: dict[str, InventoryItem]
โดยใน InventoryItem มีเมธอด sell(amount: int) ซึ่งจะ raise ValueError หากจำนวนไม่พอหรือ amount <= 0

โจทย์: จงเขียนเมธอด sell_many(self, items_to_sell: dict[str, int]) เพิ่มลงในคลาส Inventory
ข้อกำหนด:
1. ปฏิบัติตามหลัก Atomicity: ต้องตรวจสอบว่าสินค้าทุกรายการมีของพอขาย "ก่อน" เริ่มหักสต็อกจริง หากชิ้นใดไม่พอ ห้ามหักสต็อกรายการอื่น
2. Input Validation: qty ต้องเป็นจำนวนเต็มบวก (> 0)
3. Error Handling: หากไม่พบสินค้าให้ raise KeyError, หากสต็อกไม่พอให้ raise ValueError

```

### ผลลัพธ์โค้ดที่ AI สร้างขึ้น (รอบที่ 2):

```python
def sell_many(self, items_to_sell: dict[str, int]) -> dict[str, int]:
    # 1. Validation & Pre-check (ตรวจสอบทุกรายการก่อนตัดสต็อกจริง)
    for name, qty in items_to_sell.items():
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError(f"จำนวนที่ต้องการซื้อของ '{name}' ต้องเป็นจำนวนเต็มบวก")
        if name not in self.items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบคลัง")
        if self.items[name].quantity < qty:
            raise ValueError(
                f"สต็อกไม่เพียงพอสำหรับ '{name}' (คงเหลือ {self.items[name].quantity}, ต้องการ {qty})"
            )

    # 2. Execution (หักสต็อกเมื่อผ่านเงื่อนไขครบทุกรายการ - Atomicity)
    sold_summary = {}
    for name, qty in items_to_sell.items():
        self.items[name].sell(qty)
        sold_summary[name] = qty

    return sold_summary

```

---

## 3. ตารางสรุปเปรียบเทียบผลลัพธ์ (Summary Matrix)

| ประเด็นเปรียบเทียบ | รอบที่ 1: Naive Prompt | รอบที่ 2: Context Engineering |
| --- | --- | --- |
| **ความเข้ากันได้กับระบบ (Compatibility)** | ❌ ใช้งานไม่ได้ ต้องเขียนใหม่ทั้งหมด | ✅ นำไปใส่ในคลาส `Inventory` ได้ทันที |
| **ความปลอดภัยของข้อมูล (Atomicity)** | ❌ ข้อมูลพัง สินค้าหายหากเกิด error กลางทาง | ✅ ตรวจสอบล่วงหน้าครบก่อนหักสต็อกจริง |
| **การจัดการข้อผิดพลาด (Error Handling)** | ❌ คืนสตริงข้อความธรรมดา (Silent Failure) | ✅ โยน Exception ชัดเจนตามประเภทข้อผิดพลาด |
| **Input Validation** | ❌ ไม่มีการดักค่าติดลบหรือทศนิยม | ✅ ดักจับ `int <= 0` ครบถ้วน |

---

## 4. ข้อสรุปและบทเรียน (Key Takeaways)

1. **Context มีผลต่อคุณภาพมากกว่า Prompt Syntax:** AI ไม่สามารถเดาสถาปัตยกรรมเดิมของโปรเจกต์ได้ การให้ Context ของคลาสและ Business Rules ช่วยลดข้อผิดพลาดด้าน Logic ได้อย่างมหาศาล
2. **AI มักมองข้ามความสมบูรณ์ของธุรกรรม (Transaction Integrity):** หากไม่เน้นย้ำเรื่อง Atomicity หรือ Rollback โค้ดที่สร้างโดย AI มักจะประมวลผลไปข้างหน้าทีละรายการโดยไม่คำนึงถึงผลข้างเคียงเมื่อเกิดข้อผิดพลาด
