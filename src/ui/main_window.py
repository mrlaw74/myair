import sys
import asyncio
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QWidget
from PyQt5.QtCore import QThread, pyqtSignal
from src.tasks.profile_handler import handle_profile
from src.utils.config import API_URL
from src.api.gpm_login_api import GPMLoginApiV3

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, profiles):
        super().__init__()
        self.profiles = profiles
        self.api = GPMLoginApiV3(API_URL)

    async def run_tasks(self):
        await asyncio.gather(*(handle_profile(
            self.api,
            cfg["id"],
            win_pos=cfg.get("win_pos"),
            win_size=cfg.get("win_size"),
            win_scale=0.7
        ) for cfg in self.profiles))

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_tasks())
        except Exception as e:
            self.log_signal.emit(f"Error: {e}")
        finally:
            loop.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Automation GUI")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        # Label
        self.label = QLabel("Load a profiles.json file to start.")
        self.layout.addWidget(self.label)

        # Load Profiles Button
        self.load_button = QPushButton("Load Profiles")
        self.load_button.clicked.connect(self.load_profiles)
        self.layout.addWidget(self.load_button)

        # Start Tasks Button
        self.start_button = QPushButton("Start Tasks")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_tasks)
        self.layout.addWidget(self.start_button)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.profiles = []

    def load_profiles(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Profiles File", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.profiles = json.load(f)
                self.label.setText(f"Loaded {len(self.profiles)} profiles.")
                self.start_button.setEnabled(True)
            except Exception as e:
                self.log_output.append(f"Error loading profiles: {e}")

    def start_tasks(self):
        self.log_output.append("Starting tasks...")
        self.worker = WorkerThread(self.profiles)
        self.worker.log_signal.connect(self.log_output.append)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())