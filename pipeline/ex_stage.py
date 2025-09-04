# pipeline/ex_stage.py
from cpu.alu import ALU
from cpu.control_unit import ControlUnit


class EXStage:
    """
    مرحله اجرا (Execute Stage) در پایپ‌لاین پردازنده
    این مرحله مسئول اجرای عملیات محاسباتی و تشخیص شاخه‌ها است
    """
    
    def __init__(self, registers, control_unit: ControlUnit, memory=None):
        """
        سازنده کلاس مرحله اجرا
        
        Args:
            registers: فایل رجیسترها
            control_unit: واحد کنترل پردازنده
            memory: حافظه (اختیاری)
        """
        self.registers = registers
        self.alu = ALU(registers, memory)  # واحد محاسبات منطقی و حسابی
        self.cu = control_unit  # از همان instance واحد کنترل استفاده می‌کنیم

    def run(self, id_ex_reg, log=None, forwarding_signals=None, ex_mem_reg=None, mem_wb_reg=None, debug=True):
        """
        اجرای یک دستور در مرحله EX
        
        Args:
            id_ex_reg: رجیستر بین مراحل ID و EX حاوی اطلاعات دستور
            log: لیست لاگ برای ثبت عملیات‌ها
            forwarding_signals: سیگنال‌های forwarding برای حل data hazard
            ex_mem_reg: رجیستر بین مراحل EX و MEM
            mem_wb_reg: رجیستر بین مراحل MEM و WB
            debug: نمایش پیام‌های دیباگ
            
        Returns:
            tuple: (EX_MEM register, branch_taken, next_pc)
        """
        
        # بررسی وجود دستور معتبر
        if not id_ex_reg or id_ex_reg.get("op") == "NOP":
            if debug:
                print("EX: No instruction")
                log.append("EX: No instruction") if log is not None else None

            return {}, False, None

        # استخراج اطلاعات دستور
        op = id_ex_reg['op']           # نوع عملیات
        rd = id_ex_reg.get('rd', 0)    # رجیستر مقصد
        imm = id_ex_reg.get('imm')     # مقدار فوری (immediate)
        pc = id_ex_reg.get('pc', 0)    # شمارنده برنامه

        # -----------------------------------------
        # دریافت مقادیر رجیسترهای منبع (rs1_val و rs2_val)
        # -----------------------------------------
        if op in ['BEQ', 'BNE']:
            # برای دستورات شاخه: فقط از رجیستر ID/EX استفاده کن
            # (مستقل از forwarding چون مقایسه در ID انجام شده)
            rs1_val = id_ex_reg.get('rs1_val', 0)
            rs2_val = id_ex_reg.get('rs2_val', 0)
        else:
            # برای سایر دستورات: خواندن از فایل رجیستر و اعمال forwarding
            rs1_val = self.registers.read(
                id_ex_reg['rs1']) if id_ex_reg.get('rs1') is not None else 0
            rs2_val = self.registers.read(
                id_ex_reg['rs2']) if id_ex_reg.get('rs2') is not None else 0

            # اعمال forwarding برای حل data hazard
            if forwarding_signals:
                fA = forwarding_signals.get("forwardA", 0)  # forwarding برای rs1
                fB = forwarding_signals.get("forwardB", 0)  # forwarding برای rs2

                # forwarding از مرحله EX/MEM (نتیجه ALU)
                if fA == 1 and ex_mem_reg:
                    rs1_val = ex_mem_reg.get("alu_result", rs1_val)
                # forwarding از مرحله MEM/WB (داده نوشته شده)
                elif fA == 2 and mem_wb_reg:
                    rs1_val = mem_wb_reg.get("write_data", rs1_val)

                # همین کار برای rs2
                if fB == 1 and ex_mem_reg:
                    rs2_val = ex_mem_reg.get("alu_result", rs2_val)
                elif fB == 2 and mem_wb_reg:
                    rs2_val = mem_wb_reg.get("write_data", rs2_val)

        # -----------------------------------------
        # محاسبه ALU و پردازش دستورات شاخه/پرش
        # -----------------------------------------
        branch_taken = False      # آیا شاخه گرفته شده؟
        next_pc = pc + 4         # PC بعدی (پیش‌فرض: دستور بعدی)
        result = None            # نتیجه ALU

        # دسته‌بندی دستورات بر اساس نوع عملیات
        alu_ops = ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'ADDI', 'LUI', 'AUIPC']
        branch_ops = ['BEQ', 'BNE', 'JALR']

        # تنظیم پارامترهای ورودی ALU
        kwargs = {}
        if op in alu_ops + branch_ops:
            if op in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
                # دستورات R-type: دو رجیستر منبع
                kwargs = {'rs1': rs1_val, 'rs2': rs2_val}
            elif op == 'ADDI':
                # دستور I-type: رجیستر + مقدار فوری
                kwargs = {'rs1': rs1_val, 'imm': imm}
            elif op in ['BEQ', 'BNE']:
                # دستورات شاخه: مقایسه دو رجیستر + offset
                kwargs = {'rs1': rs1_val, 'rs2': rs2_val,
                          'imm': imm, 'pc': pc}  # imm = offset شاخه
            elif op == 'JAL':
                # پرش غیرمشروط: PC + offset
                kwargs = {'pc': pc, 'imm': imm}  # imm = offset پرش
            elif op == 'JALR':
                # پرش به آدرس رجیستر + offset
                kwargs = {'rs1': rs1_val, 'imm': imm, 'pc': pc}
            elif op == 'LUI':
                # بارگذاری مقدار فوری در قسمت بالایی
                kwargs = {'imm': imm}
            elif op == 'AUIPC':
                # اضافه کردن مقدار فوری به PC
                kwargs = {'pc': pc, 'imm': imm}

            # اجرای دستورات پرش و شاخه (برمی‌گردانند: result, next_pc, branch_taken)
            if op in ['JAL', 'JALR']:
                result, next_pc, branch_taken = self.alu.execute(op, **kwargs)
            if op in ['BEQ', 'BNE']:
                result, next_pc, branch_taken = self.alu.execute(op, **kwargs)
            else:
                # سایر دستورات فقط نتیجه ALU برمی‌گردانند
                result = self.alu.execute(op, **kwargs)

        elif op == 'STORE':
            # دستور ذخیره در حافظه
            rs1_val = id_ex_reg.get('rs1_val', 0)  # آدرس پایه
            rs2_val = id_ex_reg.get('rs2_val', 0)  # داده برای ذخیره

            address = rs1_val + imm  # محاسبه آدرس نهایی

            # آماده‌سازی اطلاعات برای مرحله MEM
            EX_MEM = {
                'op': op,
                'alu_result': address,       # آدرس حافظه
                'store_data': rs2_val        # داده برای ذخیره
            }

            result = None  # STORE مقداری برنمی‌گرداند

        elif op == 'LOAD':
            # دستور بارگیری از حافظه
            rs1_val = id_ex_reg.get('rs1_val', 0)  # آدرس پایه
            address = rs1_val + imm                # محاسبه آدرس نهایی

            # آماده‌سازی اطلاعات برای مرحله MEM
            EX_MEM = {
                'op': op,
                'rd': rd,                          # رجیستر مقصد
                'alu_result': address              # آدرس برای خواندن
            }

            result = None  # هنوز داده خوانده نشده

        # ساخت رجیستر EX/MEM برای سایر دستورات
        if op not in ['LOAD', 'STORE']:
            EX_MEM = {
                'op': op,                                    # نوع عملیات
                'rd': rd,                                    # رجیستر مقصد
                'alu_result': result if result is not None else 0  # نتیجه ALU
            }

        # نمایش اطلاعات دیباگ
        if debug:
            print(f"EX: op={op}, rs1_val={rs1_val}, rs2_val={rs2_val}, imm={imm} "
                  f"→ result={result}, branch_taken={branch_taken}, next_pc={next_pc}")

            log.append(f"EX: op={op}, rs1_val={rs1_val}, rs2_val={rs2_val}, imm={imm} "
                       f"→ result={result}, branch_taken={branch_taken}, next_pc={next_pc}") if log is not None else None

        # برگرداندن نتایج به پایپ‌لاین
        return EX_MEM, branch_taken, next_pc