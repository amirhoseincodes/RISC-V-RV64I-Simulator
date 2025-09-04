# pipeline/mem_stage.py

class MEMStage:
    def __init__(self, memory):
        """سازنده مرحله دسترسی به حافظه"""
        self.memory = memory  # ماژول حافظه سیستم

    def run(self, ex_mem, log=None, debug=False):
        """
        اجرای مرحله دسترسی به حافظه
        
        Args:
            ex_mem: داده‌های ورودی از مرحله اجرا
            log: لیست لاگ برای ثبت عملیات
            debug: فلگ حالت دیباگ
            
        Returns:
            dict: داده‌های خروجی برای مرحله بازنویسی
        """
        # بررسی وجود دستورالعمل
        if not ex_mem:
            if debug:
                print("MEM: No instruction")
                log.append("MEM: No instruction") if log is not None else None
                
            return {}

        # استخراج اطلاعات دستورالعمل
        op = ex_mem.get("op")  # نوع عملیات
        addr = ex_mem.get("alu_result")  # آدرس محاسبه شده توسط ALU
        store_data = ex_mem.get("store_data")  # داده برای ذخیره

        # آماده‌سازی داده‌های خروجی برای مرحله بعد
        mem_wb = {
            'op': op,  # نوع عملیات
            'rd': ex_mem.get('rd')  # رجیستر مقصد
        }

        # پردازش عملیات بارگذاری از حافظه
        if op == "LOAD":
            mem_wb["mem_data"] = self.memory.load(addr)  # خواندن از حافظه
            if debug:
                print(f"MEM: Loaded {mem_wb['mem_data']} from address {addr}")
                log.append(f"MEM: Loaded {mem_wb['mem_data']} from address {addr}") if log is not None else None
                
        # پردازش عملیات ذخیره در حافظه
        elif op == "STORE":
            self.memory.store(addr, store_data)  # نوشتن در حافظه
            if debug:
                print(f"MEM: Stored {store_data} to address {addr}")
                log.append(f"MEM: Stored {store_data} to address {addr}") if log is not None else None
                
        # پردازش سایر عملیات (عملیات ALU)
        else:  
            # انتقال نتیجه ALU بدون دسترسی به حافظه
            mem_wb["alu_result"] = addr if addr is not None else 0

            if debug:
                print(f"MEM: No memory access for op={op}")
                log.append(f"MEM: No memory access for op={op}") if log is not None else None

        return mem_wb  # برگرداندن داده‌های پردازش شده