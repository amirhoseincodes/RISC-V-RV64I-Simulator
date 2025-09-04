# pipeline/wb_stage.py
from cpu.registers import RegisterFile

class WBStage:
    """مرحله Write Back - نوشتن نتایج در رجیستر"""
    
    def __init__(self, registers):
        """
        سازنده کلاس WB Stage
        
        Args:
            registers: فایل رجیستر برای نوشتن نتایج
        """
        self.registers = registers

    def run(self, mem_wb, log=None, debug=False):
        """
        اجرای مرحله نوشتن نتیجه در رجیستر
        
        Args:
            mem_wb: اطلاعات دستورالعمل از مرحله Memory
            log: لیست لاگ برای ثبت عملیات
            debug: فعال‌سازی حالت دیباگ
            
        Returns:
            dict: دیکشنری خالی (پایان pipeline)
        """
        # بررسی وجود دستورالعمل
        if not mem_wb:
            if debug:
                print("WB: No instruction")
                log.append("WB: No instruction") if log is not None else None
            return {}

        # استخراج اطلاعات دستورالعمل
        op = mem_wb.get("op")  # نوع عملیات
        rd = mem_wb.get("rd")  # رجیستر مقصد

        # پردازش دستورالعملات محاسباتی و منطقی
        if op in ["ADD", "ADDI", "SUB", "AND", "OR", "XOR", "LUI", "AUIPC", "JAL", "JALR"]:
            # دریافت نتیجه ALU یا نتیجه محاسبه شده
            value = mem_wb.get("alu_result", mem_wb.get("result"))
            
            # بررسی وجود مقدار معتبر
            if value is None:
                raise ValueError(f"WB: trying to write None (alu result) to x{rd}")

            # نوشتن مقدار در رجیستر مقصد
            self.registers.write(rd, value)

            if debug:
                print(f"WB: Wrote {value} to x{rd}")
                log.append(f"WB: Wrote {value} to x{rd}") if log is not None else None

        # پردازش دستورالعملات بارگذاری از حافظه
        elif op == "LOAD":
            # دریافت داده خوانده شده از حافظه
            value = mem_wb.get("mem_data")
           
            # بررسی وجود مقدار معتبر
            if value is None:
                raise ValueError(f"WB: trying to write None (mem data) to x{rd}")
            
            # نوشتن داده در رجیستر مقصد
            self.registers.write(rd, value)            
            
            if debug:
                print(f"WB: Loaded {value} to x{rd}")
                log.append(f"WB: Loaded {value} to x{rd}") if log is not None else None
        
        # سایر دستورالعملات که نیازی به نوشتن در رجیستر ندارند        
        else:
            if debug:
                print(f"WB: No write for op={op}")
                log.append(f"WB: No write for op={op}") if log is not None else None
                
        # بازگشت دیکشنری خالی (پایان pipeline)
        return {}