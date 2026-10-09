# Code Review: AI-Generated Pull Request - Lab 04

การตรวจทานโค้ด (Code Review) สำหรับ Pull Request ของโมดูล `inventory_service.py` ซึ่งถูกสร้างโดย AI Coding Assistant โดยจำลองสถานการณ์การเป็น Reviewer ในทีมพัฒนาซอฟต์แวร์จริง

---

## ส่วนที่ 1: รายการ Code Review Comments (ตามเกณฑ์ 4 องค์ประกอบ)

เกณฑ์ 4 องค์ประกอบของ Review Comment ที่มีคุณภาพ:
1. **ตำแหน่ง:** ระบุชื่อเมธอดและบรรทัดที่พบ
2. **ปัญหาคืออะไร:** อธิบายพฤติกรรมที่ผิดอย่างชัดเจน ไม่ใช่แค่บอกว่าผิด
3. **กรณีที่ทำให้พัง:** ยกตัวอย่างอินพุตและสถานการณ์ที่ทำให้เกิดความผิดพลาด (Breaking Case)
4. **ข้อเสนอแนะการแก้ไข:** แนะนำแนวทางแก้ไขเชิงสร้างสรรค์ (Constructive Solution)

---

### [Review Comment 1] `sell_batch` - correctness / high (Atomicity Failure)
* **ตำแหน่ง:** เมธอด `sell_batch` (บรรทัดที่ 17-23 ใน `inventory_service.py`)
* **ปัญหา:** ฟังก์ชันทำงานแบบวนลูปตัดสต็อกทีละรายการโดยตรงผ่าน `self._inv.sell(name, amount)` หากรายการลำดับท้ายเกิดข้อผิดพลาด (เช่น สต็อกไม่พอ หรือไม่พบชื่อสินค้า) รายการก่อนหน้านี้ที่ถูกตัดไปแล้วจะไม่มีการย้อนคืนสถานะ (No Rollback) ทำให้ข้อมูลในคลังไม่สอดคล้อง ละเมิดหลักการ **Atomicity (All-or-Nothing)**
* **กรณีที่ทำให้พัง:** 
  * ในคลังมีสินค้า `"ยางปัดน้ำฝน"`: 10 ชิ้น, `"น้ำมันเบรก"`: 2 ชิ้น
  * ลูกค้าสั่งซื้อพร้อมกัน: `{"ยางปัดน้ำฝน": 5, "น้ำมันเบรก": 10}`
  * ระบบตัดยางปัดน้ำฝนสำเร็จ (เหลือ 5) แต่พอน้ำมันเบรกไม่พอ ระบบจะโยน `ValueError` ออกมา ส่งผลให้ยางปัดน้ำฝนถูกตัดไปฟรีๆ โดยที่ออเดอร์ไม่สำเร็จ
* **ข้อเสนอแนะการแก้ไข:** ทำ Pre-validation ตรวจสอบว่าสินค้าทุกรายการมีอยู่จริงและมีสต็อกเพียงพอก่อนที่จะเริ่มตัดสต็อกจริง หรือใช้วิธีหักยอดแบบจำลอง หากสำเร็จครบทุกตัวจึงยืนยันการตัดสต็อก
  ```python
  def sell_batch(self, orders: dict[str, int]) -> dict[str, int]:
      # 1. ตรวจสอบความถูกต้องและสต็อกคงเหลือของทุกรายการก่อน (Pre-check)
      for name, amount in orders.items():
          if name not in self._inv._items:
              raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
          if amount <= 0:
              raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
          if self._inv._items[name].quantity < amount:
              raise ValueError(f"สินค้า '{name}' คงเหลือไม่เพียงพอ")
      
      # 2. ทำการตัดสต็อกจริงเมื่อทุกรายการผ่านเงื่อนไข (Atomic Execution)
      result = {}
      for name, amount in orders.items():
          result[name] = self._inv.sell(name, amount)
      return result
  ```

---

### [Review Comment 2] `reserve` - correctness / high (Inconsistent Logic & Silent Failure)
* **ตำแหน่ง:** เมธอด `reserve` (บรรทัดที่ 26-32 ใน `inventory_service.py`)
* **ปัญหา:** 
  1. หากจำนวนที่ขอจองเกินกว่ายอดที่จองได้ (`amount > item.quantity - already`) เงื่อนไข `if` จะไม่ทำงาน ทำให้ไม่มีการเพิ่มยอดจอง แต่บรรทัดสุดท้ายยังคง `return item.quantity - self._reserved[name]` กลับไป ทำให้ผู้เรียกเข้าใจผิดว่าการจองสำเร็จ ทั้งที่ระบบไม่ได้จองอะไรเลย (Silent Failure)
  2. ไม่มีการตรวจสอบค่า `amount <= 0` 
  3. ไม่มีการดักกรณีไม่พบสินค้าในระบบ ทำให้เกิด `KeyError` ที่ไม่มีข้อความแจ้งเตือนที่ชัดเจน
* **กรณีที่ทำให้พัง:**
  * สินค้ามีในคลัง 5 ชิ้น มียอดจองเดิม 4 ชิ้น (เหลือจองได้ 1 ชิ้น)
  * ผู้ใช้เรียก `reserve("ผ้าเบรก", 3)` -> เงื่อนไขไม่ผ่าน แต่ระบบคืนค่า `5 - 4 = 1` กลับไป ฝั่งเรียกเข้าใจว่าระบบอนุมัติการจองและเหลือ 1 ชิ้น
* **ข้อเสนอแนะการแก้ไข:** ตรวจสอบความถูกต้องของอินพุต และ Raise `ValueError` เมื่อยอดจองเกินกว่าคงเหลือ
  ```python
  def reserve(self, name: str, amount: int) -> int:
      if name not in self._inv._items:
          raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
      if amount <= 0:
          raise ValueError("จำนวนที่จองต้องมากกว่าศูนย์")
      
      item = self._inv._items[name]
      already = self._reserved.get(name, 0)
      available = item.quantity - already
      
      if amount > available:
          raise ValueError(f"สินค้า '{name}' คงเหลือให้จองได้เพียง {available} ชิ้น (ขอจอง {amount} ชิ้น)")
      
      self._reserved[name] = already + amount
      return item.quantity - self._reserved[name]
  ```

---

### [Review Comment 3] `items_in_price_range` - correctness / medium (Off-by-boundary / Exclusive vs Inclusive)
* **ตำแหน่ง:** เมธอด `items_in_price_range` (บรรทัดที่ 35-41 ใน `inventory_service.py`)
* **ปัญหา:** ใน Docstring ระบุชัดเจนว่าคืนรายชื่อสินค้าที่ราคาอยู่ในช่วง `[low, high]` ซึ่งตามสัญกรณ์คณิตศาสตร์ วงเล็บเหลี่ยมหมายถึง **ช่วงปิด (Inclusive Interval)** ที่รวมค่าขอบปลายทั้งสองด้านด้วย แต่ในโค้ดกลับใช้ `low < item.price < high` (ช่วงเปิด - Exclusive) ทำให้สินค้าที่มีราคาเท่ากับ `low` หรือ `high` พอดีตกหล่นไป
* **กรณีที่ทำให้พัง:**
  * มีสินค้า A ราคา 100.0 บาท, สินค้า B ราคา 500.0 บาท
  * ผู้จัดการเรียกดูสินค้าช่วงราคา `items_in_price_range(100.0, 500.0)`
  * ผลลัพธ์ที่ได้คือ `[]` (ไม่พบสินค้าเลย) ทั้งที่สินค้าทั้งสองควรติดในรายงาน
* **ข้อเสนอแนะการแก้ไข:** ปรับเงื่อนไขให้รวมค่าปลายทั้งสองด้านตาม Spec:
  ```python
  def items_in_price_range(self, low: float, high: float) -> list:
      if low < 0 or high < 0 or low > high:
          raise ValueError("ช่วงราคาไม่ถูกต้อง")
      return [
          name for name, item in self._inv._items.items()
          if low <= item.price <= high
      ]
  ```

---

### [Review Comment 4] `low_stock_report` - correctness / medium (Off-by-boundary Condition)
* **ตำแหน่ง:** เมธอด `low_stock_report` (บรรทัดที่ 44-50 ใน `inventory_service.py`)
* **ปัญหา:** Docstring ระบุว่า "คืนรายชื่อสินค้าที่ stock **ต่ำกว่าหรือเท่ากับเกณฑ์**" แต่โค้ดใช้เงื่อนไข `if item.quantity < self.LOW_STOCK_THRESHOLD:` ซึ่งเป็นการตรวจสอบเฉพาะค่าน้อยกว่าอย่างเคร่งครัด (Strictly less than) ทำให้สินค้าที่มีสต็อกเท่ากับ 5 พอดีไม่ถูกแจ้งเตือน
* **กรณีที่ทำให้พัง:**
  * สินค้า `"หัวเทียน"` มีสต็อกเหลือ 5 ชิ้น (`LOW_STOCK_THRESHOLD = 5`)
  * ผู้ใช้เปิดรายงานแจ้งเตือนสต็อกต่ำ คาดหวังว่าหัวเทียนจะแสดงเพื่อสั่งซื้อเพิ่ม แต่หัวเทียนไม่ปรากฏในรายงาน ทำให้ของหมดคลังโดยไม่มีการเตือนล่วงหน้า
* **ข้อเสนอแนะการแก้ไข:** เปลี่ยนตัวดำเนินการเปรียบเทียบเป็น `<=`:
  ```python
  def low_stock_report(self) -> list:
      return [
          name for name, item in self._inv._items.items()
          if item.quantity <= self.LOW_STOCK_THRESHOLD
      ]
  ```

---

### [Review Comment 5] `concurrent_restock` - concurrency / critical (Race Condition / Lost Update)
* **ตำแหน่ง:** เมธอด `concurrent_restock` (บรรทัดที่ 53-59 ใน `inventory_service.py`)
* **ปัญหา:** เกิดปัญหา **Lost Update (Race Condition)** เนื่องจากมีการอ่านค่าตัวแปร `current = self._inv._items[name].quantity` ไว้นอกบล็อก `with self._lock:` ก่อนที่จะเข้าสู่การล็อก เมื่อมี 2 เธรดทำงานพร้อมกัน เธรดที่สองอาจอ่านค่าสต็อกเดิมก่อนที่เธรดแรกจะบวกและเขียนค่าใหม่ ส่งผลให้ยอดการเติมสต็อกของเธรดแรกถูกเขียนทับและสูญหายไป
* **กรณีที่ทำให้พัง:**
  * สต็อกเริ่มต้นของ `"กรองน้ำมันเครื่อง"` มี 10 ชิ้น
  * เธรด A สั่งเติม 5 ชิ้น, เธรด B สั่งเติม 3 ชิ้น เรียกพร้อมกัน
  * เธรด A อ่าน `current = 10`
  * เธรด B อ่าน `current = 10` (อ่านก่อนเธรด A จะเขียน)
  * เธรด A เข้าล็อก -> บันทึก `10 + 5 = 15`
  * เธรด B เข้าล็อก -> บันทึก `10 + 3 = 13` (เขียนทับค่า 15)
  * ยอดสต็อกสุดท้ายกลายเป็น 13 แทนที่จะเป็น 18 ชิ้น (ของหายไป 5 ชิ้น)
* **ข้อเสนอแนะการแก้ไข:** ย้ายการอ่านค่าเข้าไปอยู่ภายใต้การปกป้องของ Lock (Critical Section) เสมอ และตรวจสอบจำนวนที่เติม:
  ```python
  def concurrent_restock(self, name: str, amount: int) -> int:
      if amount <= 0:
          raise ValueError("จำนวนที่เติมต้องมากกว่าศูนย์")
      with self._lock:
          if name not in self._inv._items:
              raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
          current = self._inv._items[name].quantity
          self._inv._items[name].quantity = current + amount
          return self._inv._items[name].quantity
  ```

---

### [Review Comment 6] `average_unit_value` - correctness / high (Wrong Divisor & ZeroDivisionError)
* **ตำแหน่ง:** เมธอด `average_unit_value` (บรรทัดที่ 62-67 ใน `inventory_service.py`)
* **ปัญหา:**
  1. **ความหมายตัวหารผิด (Semantic Error):** Docstring ระบุว่า "มูลค่าเฉลี่ยต่อชิ้น (Unit Value)" แต่โค้ดใช้ตัวหารเป็น `total_items = len(self._inv._items)` ซึ่งเป็นจำนวนชนิดสินค้า (Unique SKUs/Keys) ไม่ใช่จำนวนชิ้นสินค้าทั้งหมดในคลัง (`sum of quantities`)
  2. **ZeroDivisionError Crash:** หากคลังยังไม่มีสินค้า (`_items` ว่างเปล่า) `total_items` จะเป็น 0 ทำให้โปรแกรมแครชทันทีด้วย `ZeroDivisionError`
* **กรณีที่ทำให้พัง:**
  * คลังมีสินค้า A: 10 ชิ้น ชิ้นละ 100 บาท (มูลค่า 1,000 บาท) และสินค้า B: 1 ชิ้น ชิ้นละ 100 บาท (มูลค่า 100 บาท) รวมมูลค่า 1,100 บาท มีของทั้งหมด 11 ชิ้น มูลค่าเฉลี่ยต่อชิ้นต้องเป็น `100.0` บาท
  * แต่โค้ดคำนวณ `1100 / 2` ได้ผลลัพธ์เป็น `550.0` บาท ซึ่งผิดเพี้ยนไปอย่างมาก
  * หากเปิดระบบวันแรก คลังยังว่างเปล่า เรียกฟังก์ชันนี้จะแครชทันที
* **ข้อเสนอแนะการแก้ไข:** ตรวจสอบคลังว่างและใช้ผลรวมจำนวนชิ้นเป็นตัวหาร:
  ```python
  def average_unit_value(self) -> float:
      total_units = sum(item.quantity for item in self._inv._items.values())
      if total_units == 0:
          return 0.0
      total_value = self._inv.get_total_value()
      return total_value / total_units
  ```

---

### [Review Comment 7] สถาปัตยกรรมและการห่อหุ้มข้อมูล (Encapsulation Violation)
* **ตำแหน่ง:** ทั่วทั้งคลาส `InventoryService` (เข้าถึง `self._inv._items`)
* **ปัญหา:** มีการเข้าถึงและแก้ไข Attribute ส่วนตัว (`_items`) ของคลาส `Inventory` โดยตรงข้ามเลเยอร์ ซึ่งขัดต่อหลัก Information Hiding หากในอนาคตคลาส `Inventory` เปลี่ยนโครงสร้างการเก็บข้อมูลภายใน (เช่น เปลี่ยนเป็นฐานข้อมูลหรือ SQLite) คลาสนี้จะพังทั้งหมด
* **ข้อเสนอแนะการแก้ไข:** ควรเรียกผ่าน Public Method ของ `Inventory` หรือเพิ่มเมธอดที่จำเป็นลงใน `Inventory` เช่น `get_item(name)` หรือ `get_all_items()`

---

## ส่วนที่ 2: ตารางจัดหมวดข้อบกพร่อง (Bug Categorization Table)

| # | เมธอด / ตำแหน่ง | หมวดหมู่ (Category) | ระดับ (Severity) | สรุปปัญหา | กรณีที่ทำให้พัง (Breaking Scenario) |
| :-: | :--- | :--- | :---: | :--- | :--- |
| **1** | `sell_batch` | Correctness (Atomicity) | **High** | ไม่มีการ Rollback สต็อกเมื่อรายการลำดับหลังเกิดข้อผิดพลาด | สั่งซื้อ 2 รายการ ชิ้นที่ 2 ของไม่พอ แต่ชิ้นแรกถูกหักสต็อกไปแล้ว |
| **2** | `reserve` | Correctness (Logic) | **High** | เงื่อนไขไม่ผ่านแต่คืนค่ายอดสต็อกเสมือนสำเร็จ (Silent Failure) | ขอจองเกินจำนวนที่มี คืนค่ายอดเดิมโดยไม่แจ้งเตือนข้อผิดพลาด |
| **3** | `items_in_price_range` | Correctness (Boundary) | **Medium** | ใช้ `<` แทนที่จะเป็น `<=` ขัดต่อสัญกรณ์ช่วงปิด `[low, high]` | ค้นหาสินค้าช่วง 100-500 บาท สินค้าราคา 100 หรือ 500 บาทไม่ติดในผลลัพธ์ |
| **4** | `low_stock_report` | Correctness (Boundary) | **Medium** | ใช้ `<` แทนที่จะเป็น `<=` ขัดต่อ Docstring "ต่ำกว่าหรือเท่ากับ" | สินค้ามีสต็อกเหลือ 5 ชิ้นเท่ากับเกณฑ์ ไม่ถูกแจ้งเตือนสต็อกต่ำ |
| **5** | `concurrent_restock` | Concurrency (Race Condition) | **Critical** | อ่านค่าไว้นอกล็อก ทำให้เกิด Lost Update เมื่อมีหลายเธรดทำงานพร้อมกัน | เติมของพร้อมกัน 2 เธรด ยอดของเธรดแรกถูกเขียนทับหายไป |
| **6** | `average_unit_value` | Correctness (Arithmetic) | **High** | ตัวหารผิดความหมาย (หารด้วย SKU แทนจำนวนชิ้น) และไม่ดักหารด้วยศูนย์ | คลังว่างเกิด ZeroDivisionError หรือคำนวณมูลค่าเฉลี่ยต่อชิ้นผิดเพี้ยน |
| **7** | ทุกเมธอดในคลาส | Style / Architecture | **Low** | เข้าถึง Private Attribute `_items` ของคลาสอื่นข้ามชั้น | การเปลี่ยนโครงสร้างข้อมูลภายในของ `Inventory` จะส่งผลให้ระบบพัง |

---

## ส่วนที่ 3: เปรียบเทียบกับ AI Reviewer (Human Reviewer vs. AI Reviewer)

การทดลองนำโค้ด `inventory_service.py` ชุดเดียวกันไปให้ AI Coding Assistant ช่วยทำการ Code Review แล้วนำผลมาวิเคราะห์เปรียบเทียบ:

### ตารางเปรียบเทียบผลการตรวจจับ:

| ประเด็นบั๊กในโค้ด | คนตรวจพบ (Human) | AI Reviewer ตรวจพบ | ข้อสังเกตและพฤติกรรมของ AI |
| :--- | :---: | :---: | :--- |
| 1. `sell_batch` ขาด Atomicity | ✅ พบ | ⚠️ พบเฉพาะรอบที่สั่งย้ำ | AI มองว่าโค้ดวนลูปเรียก `sell` ได้ตามปกติ จนกว่าจะถูกถามเรื่อง Transactional/Atomic |
| 2. `reserve` Silent Failure | ✅ พบ | ❌ มองข้าม | AI มองว่ามีคำสั่ง return คืนค่าตัวเลขได้ จึงคิดว่าเมธอดสมบูรณ์แล้ว |
| 3. `items_in_price_range` ช่วงปิด | ✅ พบ | ❌ มองข้าม | AI ไม่อ่าน Docstring เทียบกับสัญลักษณ์ `<` อย่างละเอียด |
| 4. `low_stock_report` ต่ำกว่าหรือเท่ากับ | ✅ พบ | ❌ มองข้าม | AI ไม่สังเกตคำว่า "หรือเท่ากับ" ในคำอธิบาย |
| 5. `concurrent_restock` Race Condition | ✅ พบ | ❌ มองข้าม | **AI พลาดจุดนี้มากที่สุด:** เห็นว่ามี `with self._lock:` แล้ว จึงเข้าใจว่า Thread-safe แล้ว โดยไม่ดูว่าตัวแปรถูกอ่านนอกล็อก |
| 6. `average_unit_value` หารด้วยศูนย์ | ✅ พบ | ✅ พบ | AI ตรวจจับ `ZeroDivisionError` ได้ดีมากเมื่อลิสต์ว่างเปล่า |
| 7. `average_unit_value` ตัวหารผิดความหมาย | ✅ พบ | ⚠️ ก้ำกึ่ง | AI บางตัวคิดว่า "ชิ้น" คือจำนวนชนิดสินค้า (Item SKUs) |
| 8. Encapsulation (`_items`) | ✅ พบ | ✅ พบ | AI ถนัดเรื่องกฎเกณฑ์ Best Practices และ Linter เป็นอย่างดี |

### ข้อสรุปการแบ่งงานระหว่างคนกับ AI:
1. **AI เหมาะกับ:** การตรวจจับความผิดพลาดทางเทคนิคขั้นพื้นฐาน (Syntax, Exception ทั่วไป เช่น การหารด้วยศูนย์, การละเมิด Linter/Style, Typing Hints)
2. **มนุษย์จำเป็นต้องตรวจ:** 
   - **Business Invariants & Requirements:** ความสอดคล้องระหว่างข้อกำหนดใน Docstring กับตรรกะโค้ดจริง
   - **Concurrency & Race Conditions:** การตรวจสอบจังหวะการทำงานของหลายเธรด โดยเฉพาะการอ่านค่านอก Critical Section ซึ่ง AI มักจะถูกหลอกเมื่อเห็นบล็อก `with lock`
   - **Transactional Integrity:** การตรวจสอบความสมบูรณ์ของธุรกรรม (Rollback / Atomicity)

---

## ส่วนที่ 4: แบบฝึกหัดส่งท้าย (End-of-Lab Exercises)

### 1. วิเคราะห์บั๊กที่รันได้ปกติในกรณีทั่วไป แต่พังเฉพาะใน Edge Case หรือ Concurrency (2 ข้อ)
1. **`concurrent_restock` (Race Condition):** ในกรณีที่รันด้วยเธรดเดียว (Single Thread) ฟังก์ชันนี้จะทำงานได้ถูกต้อง 100% สต็อกจะบวกเพิ่มตามปกติเสมอ แต่จะเกิดความเสียหายอย่างเงียบๆ (Silent Data Loss) เฉพาะเมื่อมีหลายเธรดเรียกใช้พร้อมกันในเสี้ยววินาทีเดียวกัน (Interleaved Execution) Unit Test แบบทั่วไปที่รันตามลำดับขั้นตอนจึงไม่สามารถตรวจพบบั๊กนี้ได้
2. **`sell_batch` (Atomicity Failure):** ในกรณีปกติ (Happy Path) ที่สินค้าทุกชิ้นในคำสั่งซื้อมีสต็อกเพียงพอ ฟังก์ชันจะตัดสต็อกสำเร็จและคืนค่าถูกต้องทุกประการ แต่จะพังเฉพาะเมื่อเกิด Partial Failure (สินค้าบางชิ้นพอ แต่ชิ้นหลังไม่พอ) ทำให้ระบบทิ้ง State ข้อมูลที่ผิดพลาดไว้ในระบบ

### 2. การออกแบบ Test Case สำหรับ Concurrency Bug ใน `concurrent_restock`
การทดสอบ Race Condition จำเป็นต้องจำลองหลายเธรดทำงานพร้อมกันอย่างแท้จริง โดยใช้ `threading.Thread` และ `Barrier` เพื่อปล่อยเธรดพร้อมกัน:
```python
import threading
import pytest

def test_concurrent_restock_race_condition():
    inv = Inventory()
    inv.add_item("น้ำมันเครื่อง", quantity=10, price=200.0)
    service = InventoryService(inv)
    
    num_threads = 10
    amount_per_thread = 5
    barrier = threading.Barrier(num_threads)
    
    def worker():
        barrier.wait()  # รอให้ทุกเธรดพร้อมแล้วปล่อยให้ทำงานพร้อมกันในเสี้ยววินาที
        service.concurrent_restock("น้ำมันเครื่อง", amount_per_thread)
        
    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    expected_quantity = 10 + (num_threads * amount_per_thread)  # 10 + 50 = 60
    actual_quantity = inv._items["น้ำมันเครื่อง"].quantity
    
    # หากมีบั๊ก Lost Update ยอดที่ได้จะไม่ถึง 60
    assert actual_quantity == expected_quantity, f"เกิด Lost Update: ได้ {actual_quantity} แทนที่จะเป็น {expected_quantity}"
```

### 3. การประเมิน AI Reviewer และการแบ่งงานอย่างปลอดภัย
* **สิ่งที่ AI ทำได้ดี:** ตรวจจับ Syntax, แนะนำ Typing Hint, ตรวจสอบการลืมปิด Resource, และเตือน `ZeroDivisionError`
* **สิ่งที่ AI พลาดบ่อย:** มัก "มองข้ามตรรกะเชิงลึก" เช่น การเข้าใจผิดว่าโค้ด Thread-safe เพียงเพราะเห็นคำสั่ง Lock หรือไม่เข้าใจว่า Business Logic ต้องการ Atomicity
* **การแบ่งงานที่ปลอดภัยที่สุด (Hybrid Review Pipeline):** ใช้ AI ทำหน้าที่เป็น Pre-commit Bot ตรวจสอบ Lint, Security เบื้องต้น และ Boundary ตัวเลข จากนั้นให้ Senior Engineer หรือ Peer Reviewer ตรวจสอบ Business Rules, Concurrency, และ Data Integrity ก่อนทำการ Merge เสมอ

### 4. การสะท้อนคิด (Reflection: 100-150 คำ)
"จากการทำ Lab 4 ทำให้เห็นอย่างชัดเจนว่าทักษะการตรวจสอบโค้ดที่ AI สร้างขึ้นมีความสำคัญมากกว่าการพิมพ์โค้ดเองอย่างมาก แม้ AI Coding Assistant จะสามารถสร้างโค้ดที่มีโครงสร้างสวยงาม มี Docstring และรันผ่านได้ในเวลาอันรวดเร็ว แต่โค้ดเหล่านั้นมักแฝงไปด้วยข้อบกพร่องร้ายแรงที่มองไม่เห็นในกรณีปกติ เช่น การละเมิดหลัก Atomicity ใน `sell_batch` หรือ Race Condition ใน `concurrent_restock` ซึ่งหากวิศวกรซอฟต์แวร์ขาดความเข้าใจในหลักการทำงานเชิงลึก และยอมรับโค้ดที่ AI แนะนำโดยไม่ตรวจสอบอย่างถี่ถ้วน ย่อมส่งผลให้เกิดความเสียหายร้ายแรงต่อระบบและข้อมูลทางธุรกิจ ทักษะที่แท้จริงของวิศวกรในยุค AI จึงไม่ใช่ความเร็วในการเขียนโค้ด แต่เป็นความสามารถในการกำกับ สั่งงานอย่างมีบริบท และการตรวจจับข้อบกพร่องที่ซ่อนอยู่เพื่อความถูกต้องและปลอดภัยสูงสุดของระบบ"