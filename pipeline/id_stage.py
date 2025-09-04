# pipeline/id_stage.py

class IDStage:
    """
    مرحله رمزگشایی دستور (Instruction Decode Stage)
    این کلاس مسئول تجزیه و تحلیل دستورات واکشی شده و آماده‌سازی داده‌ها برای مرحله اجرا است
    """
    
    def __init__(self, registers):
        """
        سازنده کلاس ID Stage
        
        Args:
            registers: مرجع به فایل رجیسترهای پردازنده
        """
        self.registers = registers

    def run(self, if_id_reg, ex_mem_reg, ex_mem_reg_last, log=None, debug=True):
        """
        اجرای مرحله رمزگشایی دستور
        
        Args:
            if_id_reg: رجیستر میانی IF/ID حاوی دستور واکشی شده
            ex_mem_reg: رجیستر میانی EX/MEM فعلی برای تشخیص وابستگی‌های داده
            ex_mem_reg_last: رجیستر میانی EX/MEM قبلی برای تشخیص وابستگی‌های داده
            log: لیست لاگ‌ها (اختیاری)
            debug: فعال‌سازی حالت دیباگ
            
        Returns:
            dict: رجیستر میانی ID/EX آماده شده برای مرحله اجرا
        """
        
        # بررسی وجود دستور معتبر در رجیستر IF/ID
        if not if_id_reg or 'instr' not in if_id_reg:
            if debug:
                print("ID: No instruction")
                log.append("ID: No instruction") if log is not None else None

            # برگرداندن دستور NOP در صورت عدم وجود دستور معتبر
            return {"op": "NOP"}

        # استخراج اجزای دستور از رجیستر IF/ID
        instr = if_id_reg['instr']
        op = instr.get('op')          # نوع عملیات (opcode)
        rd = instr.get('rd')          # رجیستر مقصد
        rs1 = instr.get('rs1')        # اولین رجیستر مبدا
        rs2 = instr.get('rs2')        # دومین رجیستر مبدا
        imm = instr.get('imm')        # مقدار فوری (immediate)
        pc = if_id_reg.get('pc', 0)   # شمارنده برنامه

        # تنظیم مقادیر پیش‌فرض برای رجیسترهای مبدا
        if rs1 is None:
            rs1 = 0
        if rs2 is None:
            rs2 = 0

        # خواندن مقادیر رجیسترهای مبدا با در نظر گیری وابستگی‌های داده
        # در صورت وجود وابستگی، از رجیسترهای میانی مقدار خوانده می‌شود
        
        # بررسی وابستگی برای رجیستر اول (rs1)
        if rs1 == ex_mem_reg.get("rd"):
            # اگر رجیستر مبدا با رجیستر مقصد مرحله EX/MEM فعلی برابر باشد
            rs1_val = ex_mem_reg.get("alu_result")
        elif rs1 == ex_mem_reg_last.get("rd"):
            # اگر رجیستر مبدا با رجیستر مقصد مرحله EX/MEM قبلی برابر باشد
            rs1_val = ex_mem_reg_last.get("alu_result")
        else:
            # در غیر این صورت، مقدار را از فایل رجیستر بخوان
            rs1_val = self.registers.read(rs1) if rs1 is not None else 0

        # بررسی وابستگی برای رجیستر دوم (rs2)
        if rs2 == ex_mem_reg.get("rd"):
            # اگر رجیستر مبدا با رجیستر مقصد مرحله EX/MEM فعلی برابر باشد
            rs2_val = ex_mem_reg.get("alu_result")
        elif rs2 == ex_mem_reg_last.get("rd"):
            # اگر رجیستر مبدا با رجیستر مقصد مرحله EX/MEM قبلی برابر باشد
            rs2_val = ex_mem_reg_last.get("alu_result")
        else:
            # در غیر این صورت، مقدار را از فایل رجیستر بخوان
            rs2_val = self.registers.read(rs2) if rs2 is not None else 0

        # آماده‌سازی رجیستر میانی ID/EX برای ارسال به مرحله اجرا
        id_ex_reg = {
            'op': op,                 # نوع عملیات
            'rd': rd,                 # رجیستر مقصد
            'rs1': rs1,               # شماره رجیستر اول
            'rs2': rs2,               # شماره رجیستر دوم
            'imm': imm,               # مقدار فوری
            'pc': pc,                 # شمارنده برنامه
            'rs1_val': rs1_val,       # مقدار رجیستر اول
            'rs2_val': rs2_val        # مقدار رجیستر دوم
        }

        # چاپ اطلاعات دیباگ در صورت فعال بودن
        if debug:
            # تهیه نمایش قابل خواندن برای رجیسترها
            rs1_disp = f"{rs1}({rs1_val})" if rs1 is not None else "None"
            rs2_disp = f"{rs2}({rs2_val})" if rs2 is not None else "None"
            
            # چاپ اطلاعات رمزگشایی شده
            print(f"ID: Decoded {op} | rs1={rs1_disp}, rs2={rs2_disp}, imm={imm}")
            
            # اضافه کردن به لاگ در صورت وجود
            if log is not None:
                log.append(f"ID: Decoded {op} | rs1={rs1_disp}, rs2={rs2_disp}, imm={imm}")

        # برگرداندن رجیستر میانی آماده شده
        return id_ex_reg