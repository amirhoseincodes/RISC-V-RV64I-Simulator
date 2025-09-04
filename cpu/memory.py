class Memory:
    def __init__(self):
        # حافظه به صورت دیکشنری: کلید = آدرس، مقدار = داده ۶۴ بیتی
        self.memory = {}

    def load(self, address):
        """خواندن مقدار ۶۴ بیتی از حافظه با آدرس هم‌تراز (alignment)"""

        return self.memory.get(address, 0)  # اگر آدرس موجود نبود، مقدار ۰ بازگردانده می‌شود

    def store(self, address, value):
        """نوشتن مقدار ۶۴ بیتی در حافظه با آدرس هم‌تراز"""

        self.memory[address] = value #& 0xFFFFFFFFFFFFFFFF

    def dump(self):
        """نمایش محتوای کامل حافظه مرتب بر اساس آدرس"""
        for address in sorted(self.memory.keys()):
            print(f"0x{address:016X} : {self.memory[address]}")

