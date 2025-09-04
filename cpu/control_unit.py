# cpu/control_unit.py
from typing import Dict, Tuple, Optional

try:
    from isa.decoder import decode as decode_instr
except Exception:
    decode_instr = None  # اگر دیکودر موجود نبود، فقط روی ID_EX/EX_MEM/MEM_WB حساب می‌کنیم

def _wb_value(mem_wb: Dict) -> Optional[int]:
    if not mem_wb:
        return None
    op = mem_wb.get("op")
    if op == "LOAD":
        return mem_wb.get("mem_data")  # مقدار بارگذاری شده از حافظه
    return mem_wb.get("alu_result")   # نتیجه ALU

class ControlUnit:
    """
    واحد کنترل با لاگ مفصل و چک‌های امن برای جلوگیری از خطاهای اجرای دستور
    """

    def forwarding_unit(self, id_ex: Dict, ex_mem: Dict, mem_wb: Dict) -> Tuple[int, int]:
        fwdA, fwdB = 0, 0
        if not id_ex:
          #  print("Forwarding: ID/EX خالی، forwarding=0")
            return fwdA, fwdB  # اگر اطلاعات ID/EX موجود نباشد، forwarding انجام نمی‌شود

        rs1, rs2 = id_ex.get("rs1"), id_ex.get("rs2")
        use_rs2 = id_ex.get("imm") is None  # اگر immediate نباشد، rs2 استفاده می‌شود

        # مشخصات رجیستر مقصد در EX/MEM
        exmem_rd = ex_mem.get("rd") if ex_mem else None
        # بررسی اینکه آیا EX/MEM باید داده را بنویسد (غیر از STORE و branch ها)
        exmem_we = bool(ex_mem and exmem_rd not in (None, 0) and ex_mem.get("op") not in ("STORE", "BEQ", "BNE", "JAL", "JALR"))
        # مشخصات رجیستر مقصد در MEM/WB
        memwb_rd = mem_wb.get("rd") if mem_wb else None
        # بررسی اینکه آیا MEM/WB باید داده را بنویسد
        memwb_we = bool(mem_wb and memwb_rd not in (None, 0) and mem_wb.get("op") not in ("STORE", "BEQ", "BNE", "JAL", "JALR"))
        # آیا مقدار برای نوشتن آماده است؟
        memwb_val_ready = _wb_value(mem_wb) is not None

        # Forwarding برای ورودی اول (rs1)
        if exmem_we and rs1 is not None and rs1 == exmem_rd:
            fwdA = 1  # استفاده از داده EX/MEM
        elif memwb_we and rs1 is not None and rs1 == memwb_rd and memwb_val_ready:
            fwdA = 2  # استفاده از داده MEM/WB

        # Forwarding برای ورودی دوم (rs2) فقط وقتی استفاده می‌شود که immediate نباشد
        if use_rs2 and rs2 is not None:
            if exmem_we and rs2 == exmem_rd:
                fwdB = 1  # استفاده از داده EX/MEM
            elif memwb_we and rs2 == memwb_rd and memwb_val_ready:
                fwdB = 2  # استفاده از داده MEM/WB

        print(f"Forwarding: rs1={rs1}, rs2={rs2}, fwdA={fwdA}, fwdB={fwdB}")
        return fwdA, fwdB

    def hazard_detection_unit(self, if_id: Dict, id_ex: Dict, ex_mem: Dict) -> Tuple[bool, bool, bool]:
        stall_if = stall_id = bubble_ex = False
        # اگر دستور EXLOAD موجود نباشد یا رجیستر مقصد نامعتبر باشد، استال لازم نیست
        if not id_ex or id_ex.get("op") != "LOAD" or id_ex.get("rd") in (None, 0):
          #  print("Hazard: هیچ LOAD در EX یا rd=0، stall=False")
            return stall_if, stall_id, bubble_ex

        ex_rd = id_ex.get("rd")
        rs1_if = rs2_if = None

        # اگر اطلاعات دستور IF/ID موجود باشد و دیکودر قابل دسترس باشد، rs1 و rs2 را استخراج کن
        if if_id and "instr" in if_id and decode_instr:
            try:
                decoded = decode_instr(if_id["instr"])
                rs1_if = decoded.get("rs1")
                rs2_if = decoded.get("rs2")
            except Exception:
                print("Hazard: decode_instr خطا داد، fallback rs1/rs2=None")

        # بررسی وجود hazard (تداخل داده) واقعی با رجیستر LOAD در EX
        if (rs1_if == ex_rd) or (rs2_if == ex_rd):
            stall_if = stall_id = bubble_ex = True  # نیاز به استال و حباب در EX

        print(f"Hazard: EX_LOAD rd={ex_rd}, IF_ID rs1={rs1_if}, rs2={rs2_if}, stall_if={stall_if}")
        return stall_if, stall_id, bubble_ex

    def branch_flush_unit(self, branch_taken: bool) -> Tuple[bool, bool]:
        # اگر شاخه گرفته شود، باید pipeline را flush کنیم
        flush_if_id = flush_id_ex = branch_taken
        if branch_taken:
            print("Branch Flush: branch_taken=True → flush IF/ID و ID/EX")
        return flush_if_id, flush_id_ex

    def compute_signals(self, IF_ID: Dict, ID_EX: Dict, EX_MEM: Dict, MEM_WB: Dict, branch_taken: bool=False) -> Dict:
        # محاسبه سیگنال‌های کنترل برای forwarding، استال و flush
        forwardA, forwardB = self.forwarding_unit(ID_EX, EX_MEM, MEM_WB)
        stall_if, stall_id, bubble_ex = self.hazard_detection_unit(IF_ID, ID_EX, EX_MEM)
        flush_if_id, flush_id_ex = self.branch_flush_unit(branch_taken)

        signals = {
            "forwardA": forwardA,
            "forwardB": forwardB,
            "stall_if": stall_if,
            "stall_id": stall_id,
            "bubble_ex": bubble_ex,
            "flush_if_id": flush_if_id,
            "flush_id_ex": flush_id_ex,
        }
      #  print(f"Compute Signals: {signals}")
        return signals
