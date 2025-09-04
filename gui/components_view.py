# gui/components_view.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # اضافه کردن مسیر والد برای دسترسی به ماژول‌های cpu
from cpu.registers import RegisterFile  # وارد کردن کلاس RegisterFile برای مدیریت رجیسترها
from cpu.memory import Memory  # وارد کردن کلاس Memory برای مدیریت حافظه

class RegistersView(QWidget):
    def __init__(self, register_file: RegisterFile):
        super().__init__()  # فراخوانی سازنده کلاس والد QWidget
        self.register_file = register_file  # اتصال به رجیسترهای پردازنده
        
        # تنظیم چیدمان و برچسب
        layout = QVBoxLayout(self)  # ایجاد چیدمان عمودی برای ویجت
        label = QLabel("Registers")  # ایجاد برچسب برای جدول رجیسترها
        label.setAlignment(Qt.AlignCenter)  # وسط‌چین کردن برچسب
        layout.addWidget(label)  # افزودن برچسب به چیدمان
        
        # ساخت جدول برای نمایش رجیسترها
        self.table = QTableWidget()  # ایجاد جدول
        self.table.setRowCount(32)  # تنظیم 32 ردیف برای رجیسترهای x0 تا x31
        self.table.setColumnCount(3)  # تنظیم 3 ستون: نام رجیستر، مقدار هگز، مقدار دسیمال
        self.table.setHorizontalHeaderLabels(["Reg", "Hex", "Decimal"])  # تنظیم عنوان ستون‌ها
        
        # تنظیم فونت کوچک‌تر برای جدول
        self.table.setFont(QFont("Arial", 6))  # تنظیم فونت Arial با اندازه 6 برای فشردگی
        
        # تنظیم اندازه ستون‌ها برای فشرده‌تر شدن
        header = self.table.horizontalHeader()  # گرفتن هدر جدول
        self.table.setColumnWidth(0, 50)  # عرض ستون Reg (باریک‌تر)
        self.table.setColumnWidth(1, 80)  # عرض ستون Hex
        self.table.setColumnWidth(2, 80)  # عرض ستون Decimal
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(32):
            self.table.setRowHeight(i, 12)  # ارتفاع هر ردیف 12 پیکسل برای فشردگی بیشتر
            reg_item = QTableWidgetItem(f"x{i}")  # ایجاد آیتم برای نام رجیستر
            reg_item.setFlags(Qt.ItemIsEnabled)  # غیرفعال کردن ویرایش
            self.table.setItem(i, 0, reg_item)  # قرار دادن آیتم در جدول
        
        # غیرفعال کردن اسکرول عمودی
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # خاموش کردن اسکرول عمودی
        
        # تنظیم ارتفاع جدول برای نمایش همه ردیف‌ها
        self.table.setFixedHeight(32 * 12 + self.table.horizontalHeader().height() + 2+350)  # 32 ردیف * 12 پیکسل + هدر + حاشیه
        
        layout.addWidget(self.table)  # افزودن جدول به چیدمان
        self.update()  # آپدیت اولیه جدول
        
    def update(self):
        # آپدیت مقادیر جدول رجیسترها
        print(f"Updating RegistersView... x1={self.register_file.read(1)}, x2={self.register_file.read(2)}, x3={self.register_file.read(3)}")  # لاگ دیباگ
        try:
            for i in range(32):
                value = self.register_file.read(i)  # خواندن مقدار رجیستر
                hex_item = QTableWidgetItem(hex(value))  # مقدار به صورت هگز
                dec_item = QTableWidgetItem(str(value))  # مقدار به صورت دسیمال
                hex_item.setFlags(Qt.ItemIsEnabled)  # غیرفعال کردن ویرایش
                dec_item.setFlags(Qt.ItemIsEnabled)  # غیرفعال کردن ویرایش
                self.table.setItem(i, 1, hex_item)  # قرار دادن مقدار هگز
                self.table.setItem(i, 2, dec_item)  # قرار دادن مقدار دسیمال
            self.table.repaint()  # رفرش گرافیکی جدول
        except Exception as e:
            print(f"Error in RegistersView.update: {e}")  # لاگ خطا

class MemoryView(QWidget):
    def __init__(self, memory: Memory):
        super().__init__()  # فراخوانی سازنده کلاس والد QWidget
        self.memory = memory  # اتصال به حافظه پردازنده
        
        # تنظیم چیدمان و برچسب
        layout = QVBoxLayout(self)  # ایجاد چیدمان عمودی برای ویجت
        label = QLabel("Memory")  # ایجاد برچسب برای جدول حافظه
        label.setAlignment(Qt.AlignCenter)  # وسط‌چین کردن برچسب
        layout.addWidget(label)  # افزودن برچسب به چیدمان
        
        # ساخت جدول برای نمایش حافظه
        self.table = QTableWidget()  # ایجاد جدول
        self.table.setColumnCount(2)  # تنظیم 2 ستون: آدرس و مقدار
        self.table.setHorizontalHeaderLabels(["Address (Hex)", "Value (Hex)"])  # تنظیم عنوان ستون‌ها
        
        # تنظیم فونت کوچک‌تر برای جدول
        self.table.setFont(QFont("Arial", 6))  # تنظیم فونت Arial با اندازه 6 برای فشردگی
        
        # تنظیم اندازه ستون‌ها
        header = self.table.horizontalHeader()  # گرفتن هدر جدول
        self.table.setColumnWidth(0, 60)  # عرض ستون Address (باریک‌تر)
        self.table.setColumnWidth(1, 60)  # عرض ستون Value (باریک‌تر)
        
        # تنظیم ارتفاع ردیف‌ها
        self.table.setRowHeight(0, 12)  # ارتفاع ردیف‌ها 12 پیکسل برای فشردگی
        
        layout.addWidget(self.table)  # افزودن جدول به چیدمان
        self.update()  # آپدیت اولیه جدول
        
    def update(self):
        # آپدیت مقادیر جدول حافظه
        print(f"Updating MemoryView... memory={self.memory.memory}")  # لاگ دیباگ
        try:
            self.table.setRowCount(0)  # پاک کردن ردیف‌های قبلی
            for address in sorted(self.memory.memory.keys()):  # حلقه روی آدرس‌های حافظه
                row = self.table.rowCount()  # گرفتن شماره ردیف جدید
                self.table.insertRow(row)  # افزودن ردیف جدید
                self.table.setRowHeight(row, 12)  # ارتفاع ردیف 12 پیکسل
                addr_item = QTableWidgetItem(hex(address))  # آدرس به صورت هگز
                value = self.memory.memory.get(address, 0)  # گرفتن مقدار یا 0
                value_item = QTableWidgetItem(hex(value) if isinstance(value, int) else "Invalid")  # مقدار به صورت هگز
                addr_item.setFlags(Qt.ItemIsEnabled)  # غیرفعال کردن ویرایش
                value_item.setFlags(Qt.ItemIsEnabled)  # غیرفعال کردن ویرایش
                self.table.setItem(row, 0, addr_item)  # قرار دادن آدرس
                self.table.setItem(row, 1, value_item)  # قرار دادن مقدار
            self.table.repaint()  # رفرش گرافیکی جدول
        except Exception as e:
            print(f"Error in MemoryView.update: {e}")  # لاگ خطا