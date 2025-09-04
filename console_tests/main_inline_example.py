# تست pipe line - Inline test

import sys
import os

# مسیر پوشه پدر فایل فعلی
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from cpu.registers import RegisterFile
from cpu.memory import Memory
from pipeline.pipeline_runner import run_pipeline
from isa.parser import load_assembly_file

if __name__ == "__main__":
    

    
    rf = RegisterFile()
    mem = Memory()
    
    # 1️⃣ ALU + Immediate
    program_alu = [
        {"op": "ADDI", "rd": 1, "rs1": 0, "imm": 10},  # x1 = 10
        {"op": "ADDI", "rd": 2, "rs1": 0, "imm": 20},  # x2 = 20
        {"op": "ADD",  "rd": 3, "rs1": 1, "rs2": 2},   # x3 = x1 + x2
        {"op": "SUB",  "rd": 4, "rs1": 2, "rs2": 1},   # x4 = x2 - x1
    ]
    print("=== ALU/Immediate Test ===")
    run_pipeline(program_alu, rf, mem, debug=True)
    rf.dump()

    # 2️⃣ Load / Store
    rf.__init__()
    mem.__init__()
    rf.write(1, 100)  # مقداردهی رجیستر x1
    program_mem = [
        {"op": "ADDI", "rd": 2, "rs1": 0, "imm": 42},       # x2 = 42
        {"op": "STORE", "rs1": 1, "rs2": 2, "imm": 0},      # MEM[x1+0] = x2
        {"op": "LOAD", "rd": 3, "rs1": 1, "imm": 0},        # x3 = MEM[x1+0]
    ]
    print("\n=== Load/Store Test ===")
    run_pipeline(program_mem, rf, mem, debug=True)
    rf.dump()

    # 3️⃣ Branch / Jump
    rf.__init__()
    mem.__init__()
    program_branch = [
        {"op": "ADDI", "rd": 1, "rs1": 0, "imm": 5},        # x1 = 5
        {"op": "ADDI", "rd": 2, "rs1": 0, "imm": 5},        # x2 = 5
        {"op": "BEQ", "rs1": 1, "rs2": 2, "imm": 2},        # branch taken
        {"op": "ADDI", "rd": 3, "rs1": 0, "imm": 1},        # skipped if branch
        {"op": "JAL", "rd": 4, "imm": 1},                  # jump next instruction
    ]
    print("\n=== Branch/Jump Test ===")
    run_pipeline(program_branch, rf, mem, debug=True)
    rf.dump()
    
    