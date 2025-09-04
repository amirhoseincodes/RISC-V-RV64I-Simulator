# pipeline/if_stage.py

class IFStage:
    def __init__(self, instr_mem, pc):
        """
        سازنده مرحله واکشی دستورالعمل (Instruction Fetch)
        
        Args:
            instr_mem: حافظه دستورالعمل‌ها (لیست یا دیکشنری)
            pc: شمارنده برنامه (Program Counter) - لیست یا متغیر
        """
        self.instr_mem = instr_mem  # حافظه دستورها (لیست یا دیکشنری)
        self.pc = pc                # شمارنده برنامه (لیست یا متغیر)

    def run(self, if_id_reg, log=None):
        """
        اجرای مرحله واکشی دستورالعمل (IF Stage)
        
        این متد دستورالعمل فعلی را از حافظه واکشی کرده و آن را در رجیستر IF/ID قرار می‌دهد
        
        Args:
            if_id_reg: رجیستر پایپ‌لاین بین مراحل IF و ID
            log: لیست لاگ برای ثبت عملیات
        """
        # بررسی اینکه آیا شمارنده برنامه در محدوده حافظه دستورات است
        if self.pc[0] < len(self.instr_mem):
            # واکشی دستورالعمل از حافظه در موقعیت فعلی PC
            instr = self.instr_mem[self.pc[0]]
            
            # قرار دادن دستورالعمل واکشی شده در رجیستر IF/ID
            if_id_reg['instr'] = instr  # دستورالعمل واکشی شده
            if_id_reg['pc'] = self.pc[0]  # مقدار فعلی شمارنده برنامه
            
            # نمایش اطلاعات دیباگ
            print(f"IF: Fetched instruction {instr} at PC={self.pc[0]}")
            log.append(
                f"IF: Fetched instruction {instr} at PC={self.pc[0]}") if log is not None else None

            # افزایش شمارنده برنامه برای دستورالعمل بعدی
            self.pc[0] += 1
            
        else:
            # پایان برنامه - پایپ‌لاین را خالی کن
            if_id_reg.clear()  # پاک کردن رجیستر پایپ‌لاین
            print("IF: End of program")
            log.append("IF: End of program") if log is not None else None