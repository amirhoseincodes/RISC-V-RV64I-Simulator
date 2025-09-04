# RISC-V RV64I Simulator 🖥️

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![Status](https://img.shields.io/badge/Status-Development-yellow) ![License](https://img.shields.io/badge/License-MIT-green)

**شبیه‌ساز کامل معماری پردازنده ۶۴ بیتی RISC-V با قابلیت اجرای گام‌به‌گام، پایپ‌لاین و GUI تعاملی**

---

## 📌 معرفی پروژه

این پروژه برای درس **ریزپردازنده و اسمبلی** است و هدف آن ساخت **شبیه‌ساز معماری RISC-V RV64I** می‌باشد.



## ⚡ ویژگی‌ها

- شبیه‌سازی مرحله‌ای بدون پایپ‌لاین
    
- اجرای برنامه‌های خط به خط با **حالت دیباگ**
    
- پایپ‌لاین ۵ مرحله‌ای: IF, ID, EX, MEM, WB
    
- مدیریت hazards: data forwarding و stalling، تشخیص control hazard
    
- پشتیبانی از pseudo-instruction‌ها و کش ساده
    
- رابط گرافیکی تعاملی (GUI) برای نمایش مراحل پایپ‌لاین و اجرای برنامه


---

## 🎬 دمو



https://github.com/user-attachments/assets/e8119073-41d7-47ea-8909-725c366d0301



---

## 🗂️ ساختار پروژه

```
riscv_simulator/
├── run_gui.py                  # نقطه ورود برای اجرای شبیه‌ساز با رابط گرافیکی
├── isa/
│   ├── parser.py        # تبدیل کد اسمبلی به آبجکت‌های دستور (سطح بالاتر از باینری)
│   └── decoder.py       # دیکودر دستور: تجزیه باینری به فیلدهای RISC-V (op, rs1, rs2, rd, imm)
├── cpu/
│   ├── registers.py      # رجیستر فایل (۳۲ رجیستر ۶۴ بیتی RISC-V + x0 ثابت)
│   ├── alu.py            # واحد محاسباتی (Arithmetic Logic Unit) شامل توابع
│   ├── memory.py         # حافظه اصلی (load/store word)
│   └── control_unit.py   # واحد کنترل پایپ‌لاین forwarding, stalling, flush
├── pipeline/
│   ├── if_stage.py       # مرحله Instruction Fetch: گرفتن دستور از حافظه برنامه
│   ├── id_stage.py       # مرحله Instruction Decode: دیکود دستور و استخراج فیلدها
│   ├── ex_stage.py       # مرحله Execute: اجرای ALU، محاسبه branch/jump target
│   ├── mem_stage.py      # مرحله Memory: اجرای دستورات load/store
│   ├── wb_stage.py       # مرحله Write Back: نوشتن نتیجه در رجیستر فایل
│   └── pipeline_runner.py # حلقه اصلی اجرای پایپ‌لاین و هماهنگ‌سازی مراحل
├── gui/
│   ├── main_window.py     # پنجره اصلی GUI برای نمایش اجرای پردازنده
│   └── components_view.py # ویجت‌های گرافیکی برای نمایش رجیسترها، ALU، حافظه و پایپ‌لاین
├── examples/
│   ├── program.s          # مثال اسمبلی ساده (افزودن مقادیر ثابت)
│   ├── program2.s         # مثال اسمبلی پیشرفته‌تر
│   ├── program3.s         # مثال اسمبلی با دستورات branch/jump
│   └── program4.s         # (در صورت نیاز) برنامه نمونه دیگر
├── console_tests/
│   ├── main_inline_example.py # اجرای شبیه‌ساز با برنامه تعریف‌شده در کد
│   └── main_run_from_file.py  # اجرای شبیه‌ساز با برنامه اسمبلی از فایل
└── طرح مراحل پروژه.md         # مستند فازهای پروژه و مراحل طراحی/پیاده‌سازی

```

✅ لینک‌های مستقیم به ماژول‌ها:

- [ISA Parser](https://github.com/amirhoseincodes/RISC-V-RV64I-Simulator/blob/main/isa/parser.py)
    
- [Instruction Decoder](https://github.com/amirhoseincodes/RISC-V-RV64I-Simulator/blob/main/isa/decoder.py)
        
- [CPU Components](https://github.com/amirhoseincodes/RISC-V-RV64I-Simulator/tree/main/cpu)
    
- [Pipeline Stages](https://github.com/amirhoseincodes/RISC-V-RV64I-Simulator/tree/main/pipeline)
    
- [GUI](https://github.com/amirhoseincodes/RISC-V-RV64I-Simulator/tree/main/gui)
    

---

## 🚀 نحوه اجرا

1. کلون کردن ریپازیتوری:
    

```bash
git clone https://github.com/amirhoseincodes/RISC-V-RV64I-Simulator.git
cd RISC-V-RV64I-Simulator
```

2. اجرای یک برنامه نمونه:
    

```bash
python run run_gui.py
```


    



---

## 🏗️ فازهای پروژه
| فاز   | شرح                                                                                                                    |
|-------|------------------------------------------------------------------------------------------------------------------------|
| **۰** | انتخاب ISA واقعی                                                                                                       |
| **۱** | شبیه‌سازی مرحله‌ای بدون پایپ‌لاین: رجیستر فایل، حافظه، ALU، دیکدر، اجرای گام‌به‌گام                                  |
| **۲** | اجرای کامل برنامه اسمبلی + حالت دیباگ: بارگذاری از فایل، پشتیبانی از لیبل‌ها، نمایش وضعیت رجیستر و حافظه           |
| **۳** | پیاده‌سازی پایپ‌لاین ۵ مرحله‌ای: IF, ID, EX, MEM, WB، forwarding، stalling، branch hazard                             |
| **۴** | توسعه معماری: کش ساده، وقفه‌ها، pseudo-instruction‌ها                                                                 |
| **۵** | رابط گرافیکی تعاملی: نمایش CPU و پایپ‌لاین، اجرای مرحله‌ای و کامل برنامه                                            |
                
