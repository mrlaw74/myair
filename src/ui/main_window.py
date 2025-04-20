import sys
import asyncio
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QTextEdit, QWidget, QTabWidget, QHBoxLayout
)
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
        self.setGeometry(100, 100, 800, 600)

        # Create the main layout
        self.layout = QVBoxLayout()

        # Create the tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Add the main tab
        self.main_tab = QWidget()
        self.tabs.addTab(self.main_tab, "Main Tab")
        self.setup_main_tab()

        # Add another tab named "tab1"
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Tab1")
        self.setup_tab1()

        # Set the central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def setup_main_tab(self):
        """Set up the main tab layout."""
        layout = QVBoxLayout()

        # Label
        self.label = QLabel("Load a profiles.json file to start.")
        layout.addWidget(self.label)

        # Load Profiles Button
        self.load_button = QPushButton("Load Profiles")
        self.load_button.clicked.connect(self.load_profiles)
        layout.addWidget(self.load_button)

        # Start Tasks Button
        self.start_button = QPushButton("Start Tasks")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_tasks)
        layout.addWidget(self.start_button)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.main_tab.setLayout(layout)

    def setup_tab1(self):
        """Set up the layout for Tab1."""
        layout = QVBoxLayout()

        # Add a label and a button to Tab1
        label = QLabel("This is Tab1. Add your custom functionality here.")
        layout.addWidget(label)

        button = QPushButton("Click Me")
        button.clicked.connect(self.on_tab1_button_click)
        layout.addWidget(button)

        self.tab1.setLayout(layout)

    def on_tab1_button_click(self):
        """Handle button click in Tab1."""
        print("Button in Tab1 clicked!")

    def load_profiles(self):
        """Load profiles from a JSON file."""
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
        """Start the automation tasks."""
        self.log_output.append("Starting tasks...")
        self.worker = WorkerThread(self.profiles)
        self.worker.log_signal.connect(self.log_output.append)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())