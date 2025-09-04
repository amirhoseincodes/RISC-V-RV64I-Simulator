# ========== کلاس ALU با استفاده از توابع خارجی ==========

class ALU:
    def __init__(self, rf, memory=None):
        self.rf = rf
        self.memory = memory  # فقط اگر لازم باشه برای load/store

        self.operations = {
            'ADD': execute_add,       # دستور جمع
            'SUB': execute_sub,       # دستور تفریق
            'AND': execute_and,       # دستور AND منطقی
            'OR': execute_or,         # دستور OR منطقی
            'XOR': execute_xor,       # دستور XOR منطقی
            'ADDI': execute_addi,     # دستور جمع با مقدار ثابت
            'BEQ': execute_beq,       # پرش در صورت برابر بودن
            'BNE': execute_bne,       # پرش در صورت نابرابر بودن
            'JAL': execute_jal,       # پرش و لینک
            'JALR': execute_jalr,     # پرش غیر مستقیم و لینک
            'LUI': execute_lui,       # بارگذاری مقدار بالا
            'AUIPC': execute_auipc,   # افزودن مقدار به PC
        }

    def execute(self, op, **kwargs):
        if op not in self.operations:
            # اگر دستور پشتیبانی نشود، خطا می‌دهد
            raise ValueError(f"Unsupported operation: {op}")

        func = self.operations[op]

        # بسته به دستور، پارامترهای لازم رو به تابع پاس میدیم
        if op in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
            # اعمال محاسباتی پایه با دو ثبات
            return func(kwargs['rs1'], kwargs['rs2'])
        elif op == 'ADDI':
            return func(kwargs['rs1'], kwargs['imm'])  # جمع با مقدار ثابت
        elif op in ['BEQ', 'BNE']:
            # پرش شرطی
            return func(kwargs['rs1'], kwargs['rs2'], kwargs['imm'], kwargs['pc'])
        elif op == 'JAL':
            return func(kwargs['pc'], kwargs['imm'])  # پرش و لینک
        elif op == 'JALR':
            # پرش غیر مستقیم
            return func(kwargs['rs1'], kwargs['imm'], kwargs['pc'])
        elif op == 'LUI':
            return func(kwargs['imm'])  # بارگذاری immediate در بخش بالا
        elif op == 'AUIPC':
            return func(kwargs['pc'], kwargs['imm'])  # افزودن مقدار به PC
        else:
            raise ValueError(
                # خطا برای عملیات‌های پیاده‌سازی نشده
                f"Execute method not implemented for operation: {op}")

# ========== توابع اجرایی ALU ==========


def execute_addi(rs1, imm):
    # جمع immediate با مقدار rs1 و بازگرداندن نتیجه ۶۴ بیتی
    val_rs1 = rs1
    result = (val_rs1 + imm) & 0xFFFFFFFFFFFFFFFF
    return result


def execute_add(rs1, rs2):
    # جمع دو ثبات
    result = (rs1 + rs2) & 0xFFFFFFFFFFFFFFFF
    return result


def execute_sub(rs1, rs2):
    # تفریق rs2 از rs1
    result = (rs1 - rs2) & 0xFFFFFFFFFFFFFFFF
    return result


def execute_and(rs1, rs2):
    # AND منطقی بین دو ثبات
    result = rs1 & rs2
    return result


def execute_or(rs1, rs2):
    # OR منطقی بین دو ثبات
    result = rs1 | rs2
    return result


def execute_xor(rs1, rs2):
    # XOR منطقی بین دو ثبات
    result = rs1 ^ rs2
    return result


def execute_beq(rs1, rs2, imm, pc):
    # اگر مقادیر برابر باشند به offset پرش کن، در غیر اینصورت به دستور بعدی برو
    if rs1 == rs2:
        result = pc + imm
        branch_taken = True
        next_pc = result
        return result, next_pc, branch_taken
    else:
        result = pc + 1
        next_pc = result
        branch_taken = False
        return result, next_pc, branch_taken

def execute_bne(rs1, rs2, imm, pc):
    # اگر مقادیر نابرابر باشند به offset پرش کن، در غیر اینصورت به دستور بعدی برو
    if rs1 != rs2:
        result = pc + imm
        branch_taken = True
        next_pc = result
        return result, next_pc, branch_taken
    else:
        result = pc + 1
        next_pc = result
        branch_taken = False
        return result, next_pc, branch_taken


def execute_jal(pc, imm):
    result = pc + 4          # آدرس دستور بعدی (برای ذخیره در rd)
    next_pc = pc + imm     # مقصد jump
    branch_taken = True       # JAL یک branch است
    return result, next_pc, branch_taken


def execute_jalr(pc, rs1_val, imm):
    result = pc + 4                 # آدرس دستور بعدی (برای ذخیره در rd)
    next_pc = (rs1_val + imm) & ~1  # محاسبه مقصد پرش، بیت صفر باید صفر باشد
    branch_taken = True
    return result, next_pc, branch_taken


def execute_lui(imm):
    result = imm << 12  # بارگذاری immediate در بیت‌های بالا
    return result  # WBStage این مقدار را در rd می‌نویسد


def execute_auipc(pc, imm):
    val = (pc * 4) + (imm << 12)  # افزودن مقدار به PC (در واحد آدرس)
    return val
