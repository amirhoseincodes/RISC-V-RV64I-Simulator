# isa/decoder.py
def decode(instr):
    """
    دیکد کردن دستور
    ورودی: دیکشنری مثل {'op': 'ADD', 'rd': 3, 'rs1': 1, 'rs2': 2, 'imm': None}
    خروجی: دیکشنری کامل شده با کلیدهای op, rd, rs1, rs2, imm
    """
    return {
        'op': instr.get('op'),       # نوع عملیات (مثلاً ADD, SUB, ...)
        'rd': instr.get('rd'),       # رجیستر مقصد
        'rs1': instr.get('rs1'),     # رجیستر اول منبع
        'rs2': instr.get('rs2'),     # رجیستر دوم منبع
        'imm': instr.get('imm', None)  # مقدار immediate (اگر وجود داشته باشد)
    }
