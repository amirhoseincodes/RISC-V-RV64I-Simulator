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
    
    # program 1 

    rf.__init__()
    mem.__init__()

    program ,lables = load_assembly_file("examples/program.s")

    print("=== ALU/Immediate Test from .s file ===")
    run_pipeline(program, rf, mem, debug=True)
    rf.dump()

    # program 2 

    rf.__init__()
    mem.__init__()

    program ,lables = load_assembly_file("examples/program2.s")

    print("=== ALU/Immediate Test from .s file ===")
    run_pipeline(program, rf, mem, debug=True)
    rf.dump()

    # program 3 
    
    rf.__init__()
    mem.__init__()

    program ,lables = load_assembly_file("examples/program3.s")

    print("=== ALU/Immediate Test from .s file ===")
    run_pipeline(program, rf, mem, debug=True)
    rf.dump()


    # program 4

    rf.__init__()
    mem.__init__()
    rf.write(1, 100)  # مقداردهی رجیستر x1

    program, lables = load_assembly_file("examples/program4.s")

    print("=== Load/Store Test from .s file ===")
    run_pipeline(program, rf, mem, debug=True)
    rf.dump()
