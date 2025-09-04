# ===========================================================================
# اجرا کننده برنامه اسمبلی

# تبدیل نام رجیستر به شماره رجیستر (مثلاً "x5" → 5)
def parse_register(reg):
    if reg.startswith("x"):
        return int(reg[1:])  # جدا کردن عدد بعد از x و تبدیل به عدد صحیح
    else:
        raise ValueError(f"Invalid register name: {reg}")  # اگر فرمت نامعتبر باشد

# خواندن خطوط برنامه و تشخیص لیبل‌ها
def parse_program_with_labels(text):
    labels = {}      # دیکشنری برای نگهداری نام لیبل و آدرس آن
    raw_lines = []   # خطوط برنامه بدون لیبل‌ها

    for idx, line in enumerate(text.strip().split("\n")):
        line = line.strip().split("#")[0]  # حذف کامنت‌ها
        if not line:
            continue  # خط خالی را نادیده بگیر
        if ":" in line:
            label, code = line.split(":", 1)  # جدا کردن لیبل از کد
            labels[label.strip()] = len(raw_lines)  # ثبت آدرس لیبل (بر اساس تعداد خطوط فعلی)
            line = code.strip()  # ادامه خط بعد از لیبل
        if line:
            raw_lines.append(line)  # افزودن خط برنامه بدون لیبل

    return raw_lines, labels  # بازگشت خطوط برنامه و لیبل‌ها

# تبدیل هر خط برنامه به دستورالعمل دیکشنری با توجه به لیبل‌ها و PC جاری
def parse_line_with_labels(line, labels, current_pc):
    parts = line.replace(",", " ").split()  # جدا کردن قسمت‌ها و حذف کاما
    op = parts[0].upper()  # عملیات به حروف بزرگ

    if op == "ADDI":
        # دستور ADDI: rd, rs1, imm
        return {"op": op, "rd": parse_register(parts[1]), "rs1": parse_register(parts[2]), "imm": int(parts[3], 0)}

    elif op in ["ADD", "SUB", "AND", "OR", "XOR"]:
        # دستورات سه‌رجیستری: rd, rs1, rs2
        return {"op": op, "rd": parse_register(parts[1]), "rs1": parse_register(parts[2]), "rs2": parse_register(parts[3])}

    elif op in ["BEQ", "BNE"]:
        # دستورات شرطی شاخه‌ای: rs1, rs2, label
        rs1 = parse_register(parts[1])
        rs2 = parse_register(parts[2])
        label = parts[3]
        target_pc = labels[label]  # پیدا کردن آدرس لیبل مقصد
        offset = target_pc - current_pc  # محاسبه آفست نسبت به PC فعلی
        return {"op": op, "rs1": rs1, "rs2": rs2, "imm": offset}

    elif op in ["LOAD", "LW"]:
        # دستور بارگذاری: rd, offset(rs1)
        # مثال: LOAD x1, 4(x2) یا LW x1, 4(x2)
        rd = parse_register(parts[1])
        offset, rs1 = parse_memory_address(parts[2])
        return {"op": "LOAD", "rd": rd, "rs1": rs1, "imm": offset}

    elif op in ["STORE", "SW"]:
        # دستور ذخیره: rs2, offset(rs1)
        # مثال: STORE x1, 4(x2) یا SW x1, 4(x2)
        rs2 = parse_register(parts[1])  # رجیستر حاوی داده برای ذخیره
        offset, rs1 = parse_memory_address(parts[2])  # آدرس مقصد
        return {"op": "STORE", "rs1": rs1, "rs2": rs2, "imm": offset}

    else:
        raise NotImplementedError(f"Unsupported op: {op}")  # اگر دستور پشتیبانی نشده باشد


# پارس کردن آدرس دهی برای دستورات LOAD و STORE
def parse_memory_address(address_part):
    """
    پارس کردن آدرس دهی به فرمت offset(base_register)
    مثال: "4(x1)" → offset=4, base_register=1
    مثال: "(x2)" → offset=0, base_register=2
    مثال: "100(x3)" → offset=100, base_register=3
    """
    address_part = address_part.strip()
    
    if "(" in address_part and ")" in address_part:
        # فرمت offset(register)
        offset_part, reg_part = address_part.split("(", 1)
        reg_part = reg_part.rstrip(")")
        
        if offset_part:
            offset = int(offset_part, 0)  # پشتیبانی از hex و decimal
        else:
            offset = 0
            
        base_register = parse_register(reg_part)
        return offset, base_register
    else:
        raise ValueError(f"Invalid memory address format: {address_part}")



# تبدیل خطوط خام برنامه به لیست دستورالعمل‌ها
def parse_final_program(raw_lines, labels):
    program = []
    for i, line in enumerate(raw_lines):
        instr = parse_line_with_labels(line, labels, i)  # دیکد هر خط
        if instr:
            program.append(instr)  # اضافه کردن به برنامه نهایی
    return program

# خواندن برنامه اسمبلی از فایل متنی با پسوند .s
def load_assembly_file(filename):
    with open(filename, 'r') as f:
        asm_text = f.read()  # خواندن کل متن فایل
    raw_lines, labels = parse_program_with_labels(asm_text)  # جدا کردن خطوط و لیبل‌ها
    program = parse_final_program(raw_lines, labels)         # ساخت برنامه به صورت دیکشنری‌ها
    return program, labels  # بازگشت برنامه و لیبل‌ها
