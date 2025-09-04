# gui/main_window.py

from pipeline.pipeline_runner import run_pipeline
from gui.components_view import RegistersView, MemoryView
from cpu.memory import Memory
from cpu.registers import RegisterFile
from isa.parser import parse_program_with_labels, parse_final_program, load_assembly_file
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QLabel, QMessageBox
)
sys.path.append('..')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # تنظیم عنوان و اندازه پنجره
        self.setWindowTitle("RISC-V RV64I Pipeline Simulator")
        self.setGeometry(100, 100, 1200, 800)

        # متغیرهای بک‌اند
        self.program = None
        self.regs = RegisterFile()
        self.mem = Memory()
        self.cycle = 0
        self.pipeline_state = None
        self.labels = {}

        # ویجت مرکزی و لی‌اوت اصلی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # پنل کنترل سمت چپ (کد اسمبلی، دکمه‌ها، لاگ)
        control_panel = QVBoxLayout()

        # پنل کد اسمبلی
        self.asm_text = QTextEdit()
        self.asm_text.setPlaceholderText("Enter assembly code here...")
        self.asm_text.setMaximumHeight(150)
        control_panel.addWidget(QLabel("Assembly Code:"))
        control_panel.addWidget(self.asm_text)

        # دکمه‌های کنترل
        button_layout = QHBoxLayout()
        self.load_file_btn = QPushButton("Load File")
        self.load_file_btn.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_file_btn)

        self.load_text_btn = QPushButton("Load Text")
        self.load_text_btn.clicked.connect(self.load_text)
        button_layout.addWidget(self.load_text_btn)

        self.step_btn = QPushButton("Step")
        self.step_btn.clicked.connect(self.step_execution)
        button_layout.addWidget(self.step_btn)

        self.run_btn = QPushButton("Run Full")
        self.run_btn.clicked.connect(self.run_full)
        button_layout.addWidget(self.run_btn)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)
        button_layout.addWidget(self.reset_btn)

        control_panel.addLayout(button_layout)

        # لاگ
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        control_panel.addWidget(QLabel("Debug Log:"))
        control_panel.addWidget(self.log_text)

        left_widget = QWidget()
        left_widget.setLayout(control_panel)
        main_layout.addWidget(left_widget)

        # پنل‌های نمایش
        views_panel = QVBoxLayout()
        self.registers_view = RegistersView(self.regs)
        views_panel.addWidget(self.registers_view)

        self.memory_view = MemoryView(self.mem)
        views_panel.addWidget(self.memory_view)

        self.schematic_view = QLabel("Schematic View (TBD)")
        views_panel.addWidget(self.schematic_view)

        self.pipeline_view = QLabel("Pipeline Stages View (TBD)")
        views_panel.addWidget(self.pipeline_view)

        views_widget = QWidget()
        views_widget.setLayout(views_panel)
        main_layout.addWidget(views_widget)

    def load_file(self):
        # لود فایل اسمبلی
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open Assembly File", "", "Assembly Files (*.s)")
            if file_name:
                self.program, self.labels = load_assembly_file(file_name)
                self.asm_text.setText(open(file_name).read())
                self.log_text.append(
                    f"Loaded program: {len(self.program)} instructions")
                self.reset()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load file: {str(e)}")

    def load_text(self):
        # لود کد اسمبلی از متن
        try:
            asm_code = self.asm_text.toPlainText()
            raw_lines, self.labels = parse_program_with_labels(asm_code)
            self.program = parse_final_program(raw_lines, self.labels)
            self.log_text.append(
                f"Loaded program: {len(self.program)} instructions")
            self.reset()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load text: {str(e)}")

    def step_execution(self):
        # اجرای یک سیکل
        if not self.program:
            self.log_text.append("No program loaded!")
            return
        try:
            current_cycle = self.pipeline_state.get(
                'cycle', 0) if self.pipeline_state else 0
            target_cycles = current_cycle + 1

            self.pipeline_state = run_pipeline(
                self.program, self.regs, self.mem,
                max_cycles=target_cycles,
                debug=True,
                initial_state=self.pipeline_state
            )

            self.cycle = self.pipeline_state.get('cycle', 0)
            self.update_views()
            # نمایش لاگ‌های سیکل جاری و نگه داشتن لاگ‌های قبلی
            self.log_text.clear()

            logs = self.pipeline_state.get('log', [])
            if logs:
                for log_line in logs:
                    self.log_text.append(log_line)
            else:
                self.log_text.append(f"No logs for Cycle {self.cycle}")

            if self.pipeline_state.get('halted', False):
                self.log_text.append("✅ Program execution completed.")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Step execution failed: {str(e)}")

    def run_full(self):
        # اجرای کامل
        if not self.program:
            self.log_text.append("No program loaded!")
            return
        try:
            self.pipeline_state = run_pipeline(
                self.program, self.regs, self.mem, max_cycles=1000,
                debug=True, initial_state=self.pipeline_state
            )
            self.cycle = self.pipeline_state.get('cycle', 0)
            self.update_views()
            # نمایش تمام لاگ‌ها
            self.log_text.clear()  # پاک کردن لاگ قبلی
            for log_line in self.pipeline_state.get('log', []):
                self.log_text.append(log_line)
            if self.pipeline_state.get('halted', False):
                self.log_text.append("✅ Program execution completed.")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Full execution failed: {str(e)}")

    def reset(self):
        # ریست سیستم
        self.regs = RegisterFile()
        self.mem = Memory()
        self.cycle = 0
        self.pipeline_state = None
        self.registers_view.register_file = self.regs
        self.memory_view.memory = self.mem
        self.update_views()
        self.log_text.clear()
        self.log_text.append("System reset.")

    def update_views(self):
        # آپدیت ویجت‌ها
        self.registers_view.update()
        self.memory_view.update()
        self.log_text.moveCursor(
            self.log_text.textCursor().End)  # اسکرول به انتها



# در صورت کار نکردن نسخه کامنت شده را استفاده کنید و نسخه قبل را کامنت کنید

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
