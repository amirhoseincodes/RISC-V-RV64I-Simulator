# pipeline_runner.py
# وارد کردن کلاس‌های مراحل pipeline
from pipeline.if_stage import IFStage
from pipeline.id_stage import IDStage
from pipeline.ex_stage import EXStage
from pipeline.mem_stage import MEMStage
from pipeline.wb_stage import WBStage
from cpu.control_unit import ControlUnit

import time

go_step = False


def is_empty(stage):
    """بررسی اینکه آیا مرحله خالی است یا خیر"""
    return not stage or stage.get('op') == 'NOP'


def run_pipeline(program, regs, mem, max_cycles=20, debug=True, initial_state=None):
    """
    اجرای pipeline پردازنده با قابلیت ادامه از حالت قبلی
    
    Args:
        program: برنامه‌ای که باید اجرا شود
        regs: رجیسترهای پردازنده
        mem: حافظه سیستم
        max_cycles: حداکثر تعداد چرخه‌های اجرا
        debug: نمایش اطلاعات دیباگ
        initial_state: حالت اولیه برای ادامه اجرا
    """

    # اگر حالت اولیه داده نشده، مقادیر پیش‌فرض را تنظیم کن
    if initial_state is None:
        pc = [0]  # شمارنده برنامه (Program Counter)
        IF_ID, ID_EX, EX_MEM, MEM_WB = {}, {}, {}, {}  # رجیسترهای pipeline
        cycle = 0
        fetching_done = False  # آیا واکشی دستورات تمام شده؟
        halted = False  # آیا اجرا متوقف شده؟
        log = []  # لاگ عملیات
        cycle = 0
        pc = [0]  # PC قابل تغییر

    else:
        # بازیابی حالت از state قبلی
        pc = initial_state['pc']
        IF_ID = initial_state.get('IF_ID', {})
        ID_EX = initial_state.get('ID_EX', {})
        EX_MEM = initial_state.get('EX_MEM', {})
        MEM_WB = initial_state.get('MEM_WB', {})
        cycle = initial_state.get('cycle', 0)
        fetching_done = initial_state.get('fetching_done', False)
        halted = initial_state.get('halted', False)
        log = initial_state.get('log', [])

    # رجیستر کمکی برای نگهداری حالت قبلی EX_MEM
    EX_MEM_LAST = {}

    # واحد کنترل pipeline
    cu = ControlUnit()

    # ایجاد نمونه از مراحل مختلف pipeline
    if_stage = IFStage(program, pc)      # مرحله واکشی دستور
    id_stage = IDStage(regs)             # مرحله رمزگشایی دستور
    ex_stage = EXStage(regs, control_unit=cu, memory=mem)  # مرحله اجرا
    mem_stage = MEMStage(mem)            # مرحله دسترسی به حافظه
    wb_stage = WBStage(regs)             # مرحله بازنویسی

    # حلقه اصلی اجرای pipeline
    while not halted and cycle < max_cycles:
        cycle += 1
        if debug:
            print(f"\n=== Cycle {cycle} ===")
            log.append(f"\n=== Cycle {cycle} ===")

        # ---------------- مرحله WB (Write Back) ----------------
        # آخرین مرحله: نوشتن نتایج در رجیسترها
        halted = wb_stage.run(MEM_WB, log, debug=debug)

        # ---------------- مرحله MEM (Memory Access) ----------------
        # دسترسی به حافظه و آماده‌سازی داده برای WB
        MEM_WB = mem_stage.run(EX_MEM, log, debug=debug)

        # ---------------- محاسبه سیگنال‌های کنترل و Forwarding ----------------
        # واحد کنترل تشخیص می‌دهد که آیا نیاز به stall، flush یا forwarding هست
        signals = cu.compute_signals(
            IF_ID, ID_EX, EX_MEM, MEM_WB, branch_taken=False)
        if debug:
            print("Control signals: " +
                  ", ".join(f"{k}={v}" for k, v in signals.items()))
            log.append("Control signals: " +
                       ", ".join(f"{k}={v}" for k, v in signals.items()))

        # ---------------- اعمال سیگنال‌های Flush ----------------
        # در صورت branch یا jump، باید مراحل قبلی را پاک کنیم
        if signals.get("flush_if_id", False):
            if debug:
                print(
                    "⚠️ Flush: Clearing IF/ID register (invalid instruction removed)")
                log.append(
                    "⚠️ Flush: Clearing IF/ID register (invalid instruction removed)")
            IF_ID.clear()

        if signals.get("flush_id_ex", False):
            if debug:
                print("⚠️ Flush: Inserting bubble (NOP) into ID/EX stage")
                log.append(
                    "⚠️ Flush: Inserting bubble (NOP) into ID/EX stage")
            ID_EX = {"op": "NOP"}

        # سیگنال‌های forwarding برای حل data hazard
        forwarding_signals = {
            "forwardA": signals["forwardA"],
            "forwardB": signals["forwardB"]
        }

        # ---------------- مرحله EX (Execute) ----------------
        # اجرای دستور و بررسی branch
        EX_MEM, branch_taken, next_pc = ex_stage.run(
            ID_EX,
            log,
            forwarding_signals=forwarding_signals,
            ex_mem_reg=EX_MEM,
            mem_wb_reg=MEM_WB,
            debug=debug
        )

        # ---------------- مدیریت Branch و Jump ----------------
        # اگر branch گرفته شد، باید pipeline را flush کنیم
        if branch_taken:
            if debug:
                print(
                    f"🚀 Branch taken! Flushing pipeline and jumping to PC={next_pc}")
                log.append(
                    f"🚀 Branch taken! Flushing pipeline and jumping to PC={next_pc}")
            pc[0] = next_pc
            if_stage = IFStage(program, pc)
            fetching_done = False
            IF_ID.clear()
            ID_EX = {"op": "NOP"}

        # ---------------- مرحله ID (Instruction Decode) ----------------
        # رمزگشایی دستور و آماده‌سازی operandها
        if signals["bubble_ex"]:
            # وارد کردن bubble (NOP) در صورت نیاز
            ID_EX = {"op": "NOP"}
        elif signals["stall_id"]:
            # نگه‌داشتن مرحله ID در صورت data hazard
            pass
        else:
            # اجرای عادی مرحله ID
            ID_EX = id_stage.run(
                IF_ID, EX_MEM, EX_MEM_LAST, log, debug=debug)

        # نگهداری حالت قبلی EX_MEM برای forwarding
        EX_MEM_LAST = EX_MEM

        # ---------------- مرحله IF (Instruction Fetch) ----------------
        # واکشی دستور جدید از حافظه
        if signals["stall_if"]:
            # نگه‌داشتن PC در صورت data hazard
            pass
        else:
            if not fetching_done:
                # واکشی دستور بعدی
                if_stage.run(IF_ID, log)
                if not IF_ID:
                    # اگر دستوری واکشی نشد، یعنی برنامه تمام شده
                    fetching_done = True
            else:
                # پاک کردن IF_ID اگر واکشی تمام شده
                IF_ID.clear()

        # ---------------- بررسی پایان pipeline ----------------
        # اگر همه مراحل خالی شدند، pipeline تمام شده است
        if fetching_done and all(is_empty(stage) for stage in [IF_ID, ID_EX, EX_MEM, MEM_WB]):
            if debug:
                print("✅ Pipeline drained, stopping.")
                log.append("✅ Pipeline drained, stopping.")
            halted = True

    # ذخیره حالت فعلی برای امکان ادامه اجرا
    state = {
        'pc': pc,
        'IF_ID': IF_ID,
        'ID_EX': ID_EX,
        'EX_MEM': EX_MEM,
        'MEM_WB': MEM_WB,
        'cycle': cycle,
        'fetching_done': fetching_done,
        'halted': halted,
        'log': log
    }
    return state