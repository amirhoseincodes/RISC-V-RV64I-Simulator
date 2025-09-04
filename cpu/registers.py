class RegisterFile:
    def __init__(self):
        # ۳۲ رجیستر ۶۴ بیتی با مقدار اولیه صفر (x0 تا x31)
        self.registers = [0] * 32

    def read(self, index):
        """خواندن مقدار رجیستر مشخص شده توسط ایندکس"""
        if 0 <= index < 32:
            return self.registers[index]
        else:
            raise IndexError("رجیستر نامعتبر")  # اگر ایندکس خارج از محدوده باشد

    def write(self, index, value):
        """نوشتن مقدار در رجیستر مشخص شده (رجیستر x0 تغییر نمی‌کند)"""
        if index == 0:
            return  # رجیستر x0 همیشه مقدار صفر دارد و قابل تغییر نیست
        if 0 <= index < 32:
            # فقط ۶۴ بیت پایین مقدار ذخیره می‌شود
            self.registers[index] = value & 0xFFFFFFFFFFFFFFFF
        else:
            raise IndexError("رجیستر نامعتبر")  # اگر ایندکس خارج از محدوده باشد

    def dump(self):
        """نمایش مقادیر همه رجیسترها برای اهداف دیباگ"""
        for i in range(32):
            print(f"x{i:02} = {self.read(i)}")
