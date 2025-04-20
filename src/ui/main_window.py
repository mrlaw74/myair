import sys
import asyncio
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QTextEdit, QWidget, QTabWidget, QHBoxLayout, QListWidget, QMessageBox
)
from PyQt5.QtGui import QScreen
from PyQt5.QtCore import QThread, pyqtSignal
from src.tasks.profile_handler import handle_profile
from src.utils.config import API_URL
from src.api.gpm_login_api import GPMLoginApiV3
from src.tasks.fetch_profiles import fetch_profiles


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
        
        # Add the Choosing Profile tab
        self.profile_tab = QWidget()
        self.tabs.addTab(self.profile_tab, "Choosing Profile")
        self.setup_profile_tab()

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

    def setup_profile_tab(self):
        """Set up the Choosing Profile tab layout."""
        layout = QVBoxLayout()

        # Label
        self.profile_label = QLabel("Click 'Fetch Profiles' to load profiles from the API.")
        layout.addWidget(self.profile_label)

        # Fetch Profiles Button
        self.fetch_button = QPushButton("Fetch Profiles")
        self.fetch_button.clicked.connect(lambda: asyncio.run(self.fetch_profiles_from_api()))
        layout.addWidget(self.fetch_button)

        # Profiles List (Multi-Selection Enabled)
        self.profile_list = QListWidget()
        self.profile_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.profile_list)

        # Start Selected Profiles Button
        self.start_selected_button = QPushButton("Start Selected Profiles")
        self.start_selected_button.clicked.connect(self.start_selected_profiles)
        layout.addWidget(self.start_selected_button)

        # Set layout for the tab
        self.profile_tab.setLayout(layout)

    async def fetch_profiles_from_api(self):
        try:
            api_url = "http://127.0.0.1:19995/api/v3/profiles"
            self.profile_label.setText("Fetching profiles from API...")
            
            # Fetch profiles
            profiles = await fetch_profiles(api_url, group_id="1", page=1, per_page=100)
            print(f"Fetched Profiles: {profiles}")  # Debug print

            # Validate response
            if not profiles or not isinstance(profiles, list):
                raise ValueError("Invalid response from API: Expected a list of profiles.")
            
            # Process profiles
            self.profiles = [{"id": p["id"], "win_pos": [0, 0], "win_size": [500, 600]} for p in profiles]

            # Populate the profile list
            self.profile_list.clear()
            for profile in profiles:
                self.profile_list.addItem(f"{profile['id']} - {profile['name']}")

            self.profile_label.setText(f"Loaded {len(self.profiles)} profiles from API.")
        except Exception as e:
            error_message = f"Failed to fetch profiles: {e}"
            QMessageBox.critical(self, "Error", error_message)
            self.profile_label.setText("Error fetching profiles.")
            print(error_message)  # Log the error for debugging

    def start_selected_profiles(self):
        """Start tasks for the selected profiles."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No profiles selected!")
            return

        # Get screen resolution
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Get selected profiles
        selected_profiles = []
        win_size_x, win_size_y = 500, 600  # Default window size
        x_offset = 5  # Horizontal gap between windows
        y_offset = 5  # Vertical gap between rows
        current_x, current_y = 0, 0  # Start at the top-left corner

        for index, item in enumerate(selected_items):
            profile_id = item.text().split(" - ")[0]  # Extract profile ID
            profile = next((p for p in self.profiles if p["id"] == profile_id), None)
            if profile:
                # Calculate adaptive position
                if current_x + win_size_x > screen_width:  # Move to the next row
                    current_x = 0
                    current_y += win_size_y + y_offset

                profile["win_pos"] = [current_x, current_y]
                profile["win_size"] = [win_size_x, win_size_y]
                selected_profiles.append(profile)

                # Update x position for the next profile
                current_x += win_size_x + x_offset

        # Pass selected profiles to the main tab
        self.selected_profiles = selected_profiles
        self.label.setText(f"Selected {len(selected_profiles)} profiles to run.")
        self.start_button.setEnabled(True)

        # Debug print to verify positions
        print(f"Selected Profiles with Positions: {self.selected_profiles}")

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
        if not hasattr(self, 'selected_profiles') or not self.selected_profiles:
            QMessageBox.warning(self, "Warning", "No profiles selected to run!")
            return

        self.log_output.append("Starting tasks...")
        print(f"Profiles to run: {self.selected_profiles}")
        self.worker = WorkerThread(self.selected_profiles)  # Use selected profiles
        self.worker.log_signal.connect(self.log_output.append)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())