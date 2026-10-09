class InventoryItem:
    def __init__(self, item_id: str, name: str, price: float, quantity: int, is_digital: bool = False):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.is_digital = is_digital

    def restock(self, amount: int) -> int:
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("จำนวนที่เพิ่มเข้าสต็อกต้องเป็นจำนวนเต็มบวก")
        self.quantity += amount
        return self.quantity

    def sell(self, amount: int) -> int:
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("จำนวนที่ขายต้องเป็นจำนวนเต็มบวก")
        if self.quantity < amount:
            raise ValueError(f"สินค้าคงเหลือ {self.quantity} ชิ้น ไม่เพียงพอสำหรับการขาย {amount} ชิ้น")
        self.quantity -= amount
        return self.quantity


class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}

    def add_item(self, item: InventoryItem):
        self._items[item.name] = item

    def get_item(self, name: str) -> InventoryItem:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        return self._items[name]

    def restock(self, name: str, amount: int) -> int:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        return self._items[name].restock(amount)

    def sell(self, name: str, amount: int) -> int:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        return self._items[name].sell(amount)

    def get_total_value(self) -> float:
        return sum(
            item.quantity * item.price for item in self._items.values()
        )

    def sell_many(self, items_to_sell: dict[str, int]) -> dict[str, int]:
        """
        ตัดสต็อกสินค้าหลายรายการพร้อมกันตามหลัก Atomicity
        - ตรวจสอบความถูกต้องและสต็อกคงเหลือของทุกรายการก่อนตัดจริง
        - หากมีข้อผิดพลาดให้ raise Exception และห้ามตัดสินค้าใดๆ ทั้งสิ้น
        """
        # 1. Validation & Pre-check (ตรวจสอบก่อนทุกรายการ)
        for name, qty in items_to_sell.items():
            if not isinstance(qty, int) or qty <= 0:
                raise ValueError(f"จำนวนที่ต้องการซื้อของ '{name}' ต้องเป็นจำนวนเต็มบวก")
            if name not in self._items:
                raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
            if self._items[name].quantity < qty:
                raise ValueError(
                    f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น ไม่เพียงพอสำหรับการขาย {qty} ชิ้น"
                )

        # 2. Execution (ตัดสต็อกจริงเมื่อทุกรายการผ่านเงื่อนไขครบถ้วน)
        sold_summary = {}
        for name, qty in items_to_sell.items():
            self._items[name].quantity -= qty
            sold_summary[name] = qty

        return sold_summary