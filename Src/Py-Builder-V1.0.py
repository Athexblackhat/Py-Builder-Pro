#!/usr/bin/env python3

"""
PyBuilder Pro - Professional Python to EXE Compiler
A modern GUI tool for building standalone executables from Python scripts
"""

import sys
import os
import subprocess
import threading
import shutil
from pathlib import Path
from datetime import datetime

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    print("PyQt5 is required. Install it using: pip install PyQt5")
    sys.exit(1)

class BuildWorker(QThread):
    """Worker thread for building the executable"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, script_path, output_dir, options):
        super().__init__()
        self.script_path = script_path
        self.output_dir = output_dir
        self.options = options
        
    def run(self):
        try:
            self.log_signal.emit("🚀 Starting build process...")
            
            # Prepare PyInstaller command
            cmd = [sys.executable, "-m", "PyInstaller"]
            
            # Add options
            if self.options.get('onefile', True):
                cmd.append("--onefile")
            else:
                cmd.append("--onedir")
                
            if self.options.get('console', False):
                cmd.append("--console")
            else:
                cmd.append("--noconsole")
                
            if self.options.get('icon') and os.path.exists(self.options['icon']):
                cmd.append(f"--icon={self.options['icon']}")
                
            if self.options.get('name'):
                cmd.append(f"--name={self.options['name']}")
                
            # Add hidden imports
            if self.options.get('hidden_imports'):
                for imp in self.options['hidden_imports'].split(','):
                    if imp.strip():
                        cmd.append(f"--hidden-import={imp.strip()}")
            
            # Add additional files
            if self.options.get('add_data'):
                for data in self.options['add_data'].split(','):
                    if data.strip():
                        cmd.append(f"--add-data={data.strip()}")
            
            # Add optimization
            cmd.append("--optimize=2")
            
            # Add upx compression if available
            if shutil.which("upx"):
                cmd.append("--upx-dir=.")
                self.log_signal.emit("✅ UPX compression found - will compress executable")
            
            # Add the script
            cmd.append(str(self.script_path))
            
            # Set working directory
            work_dir = self.output_dir / "build_temp"
            work_dir.mkdir(exist_ok=True)
            
            self.log_signal.emit(f"📦 Running PyInstaller...")
            self.log_signal.emit(f"Command: {' '.join(cmd)}")
            
            # Run PyInstaller
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(work_dir),
                bufsize=1
            )
            
            # Read output in real-time
            for line in iter(process.stdout.readline, ''):
                self.log_signal.emit(line.strip())
                if "INFO:" in line:
                    self.progress_signal.emit(50)
                elif "Building EXE" in line:
                    self.progress_signal.emit(75)
                    
            process.wait()
            
            if process.returncode == 0:
                # Move the built executable to output directory
                build_output = work_dir / "dist"
                if build_output.exists():
                    for item in build_output.iterdir():
                        dest = self.output_dir / item.name
                        if dest.exists():
                            shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
                        shutil.move(str(item), str(dest))
                
                self.progress_signal.emit(100)
                self.log_signal.emit("✅ Build completed successfully!")
                self.finished_signal.emit(True, f"Executable created in: {self.output_dir}")
            else:
                self.log_signal.emit("❌ Build failed with errors")
                self.finished_signal.emit(False, "Build failed. Check the logs for details.")
                
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {str(e)}")
            self.finished_signal.emit(False, str(e))

class PyBuilderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_path = None
        self.build_worker = None
        self.init_ui()
        self.check_dependencies()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("PyBuilder Pro - Python to EXE Compiler")
        self.setGeometry(100, 100, 900, 700)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
            QGroupBox {
                color: white;
                border: 2px solid #5a5a5a;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                color: white;
            }
            QTabWidget::pane {
                background-color: #2b2b2b;
                border: 1px solid #5a5a5a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: white;
                padding: 8px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
            }
            QProgressBar {
                border: 1px solid #5a5a5a;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 5px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("🚀 PyBuilder Pro - Professional Python to EXE Compiler")
        header_font = QFont("Arial", 16, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #4caf50; padding: 10px;")
        main_layout.addWidget(header_label)
        
        # Tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Build tab
        build_tab = QWidget()
        tabs.addTab(build_tab, "📦 Build")
        
        # Settings tab
        settings_tab = QWidget()
        tabs.addTab(settings_tab, "⚙️ Settings")
        
        # About tab
        about_tab = QWidget()
        tabs.addTab(about_tab, "ℹ️ About")
        
        # Setup build tab
        self.setup_build_tab(build_tab)
        
        # Setup settings tab
        self.setup_settings_tab(settings_tab)
        
        # Setup about tab
        self.setup_about_tab(about_tab)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def setup_build_tab(self, tab):
        """Setup the build tab interface"""
        layout = QVBoxLayout(tab)
        
        # File selection group
        file_group = QGroupBox("📁 Python Script Selection")
        file_layout = QVBoxLayout()
        
        # Script selection
        script_layout = QHBoxLayout()
        self.script_path_edit = QLineEdit()
        self.script_path_edit.setPlaceholderText("Select Python script to compile...")
        script_layout.addWidget(self.script_path_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_script)
        script_layout.addWidget(browse_btn)
        file_layout.addLayout(script_layout)
        
        # Output directory
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Output directory...")
        self.output_edit.setText(str(Path.home() / "Desktop"))
        output_layout.addWidget(self.output_edit)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(browse_output_btn)
        file_layout.addLayout(output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Build options
        options_group = QGroupBox("⚙️ Build Options")
        options_layout = QGridLayout()
        
        self.onefile_check = QCheckBox("Single File Executable (--onefile)")
        self.onefile_check.setChecked(True)
        options_layout.addWidget(self.onefile_check, 0, 0)
        
        self.console_check = QCheckBox("Show Console Window")
        self.console_check.setChecked(False)
        options_layout.addWidget(self.console_check, 0, 1)
        
        options_layout.addWidget(QLabel("Executable Name:"), 1, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Leave empty for auto-name")
        options_layout.addWidget(self.name_edit, 1, 1)
        
        options_layout.addWidget(QLabel("Icon File (.ico):"), 2, 0)
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit()
        icon_layout.addWidget(self.icon_edit)
        icon_browse_btn = QPushButton("Browse")
        icon_browse_btn.clicked.connect(self.browse_icon)
        icon_layout.addWidget(icon_browse_btn)
        options_layout.addLayout(icon_layout, 2, 1)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Build button
        self.build_btn = QPushButton("🔨 BUILD EXECUTABLE")
        self.build_btn.setMinimumHeight(50)
        self.build_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.build_btn.clicked.connect(self.start_build)
        layout.addWidget(self.build_btn)
        
        # Log output
        log_group = QGroupBox("📋 Build Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 10))
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_log_btn)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def setup_settings_tab(self, tab):
        """Setup the settings tab"""
        layout = QVBoxLayout(tab)
        
        # Advanced options
        advanced_group = QGroupBox("🔧 Advanced Options")
        advanced_layout = QGridLayout()
        
        advanced_layout.addWidget(QLabel("Hidden Imports (comma-separated):"), 0, 0)
        self.hidden_imports_edit = QLineEdit()
        self.hidden_imports_edit.setPlaceholderText("e.g., numpy, pandas, tkinter")
        advanced_layout.addWidget(self.hidden_imports_edit, 0, 1)
        
        advanced_layout.addWidget(QLabel("Additional Data Files:"), 1, 0)
        self.add_data_edit = QLineEdit()
        self.add_data_edit.setPlaceholderText("e.g., data.txt;., images/*.png;.")
        advanced_layout.addWidget(self.add_data_edit, 1, 1)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Tips group
        tips_group = QGroupBox("💡 Tips")
        tips_text = QTextEdit()
        tips_text.setReadOnly(True)
        tips_text.setHtml("""
            <h3>Optimization Tips:</h3>
            <ul>
                <li>Use --onefile for a single executable (recommended for distribution)</li>
                <li>Use --noconsole for GUI applications to hide the console window</li>
                <li>Add hidden imports if your script uses dynamic imports</li>
                <li>Install UPX (https://upx.github.io/) to compress executables</li>
                <li>Use virtual environments to minimize dependencies</li>
                <li>Test your executable on different machines to ensure compatibility</li>
            </ul>
            
            <h3>Common Issues:</h3>
            <ul>
                <li>If the executable is large, consider using --onedir for faster startup</li>
                <li>Add missing DLLs or data files using --add-data</li>
                <li>Use absolute paths or proper resource handling in your code</li>
            </ul>
        """)
        tips_group.setLayout(QVBoxLayout())
        tips_group.layout().addWidget(tips_text)
        layout.addWidget(tips_group)
        
        layout.addStretch()
        
    def setup_about_tab(self, tab):
        """Setup the about tab"""
        layout = QVBoxLayout(tab)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
            <h1 style="color: #4caf50;">PyBuilder Pro</h1>
            <h3>Version 1.0.0</h3>
            <p>A professional Python to EXE compiler with a modern GUI interface.</p>
            
            <h3>Features:</h3>
            <ul>
                <li>Easy-to-use graphical interface</li>
                <li>Support for single-file and folder-based executables</li>
                <li>Console or GUI mode selection</li>
                <li>Custom icon support</li>
                <li>Advanced options for hidden imports and data files</li>
                <li>Real-time build logging</li>
                <li>UPX compression support</li>
            </ul>
            
            <h3>Requirements:</h3>
            <ul>
                <li>Python 3.6+</li>
                <li>PyInstaller (automatically installed if missing)</li>
                <li>PyQt5 for GUI</li>
            </ul>
            
            <h3>Installation:</h3>
            <code>pip install pyinstaller PyQt5</code>
            
            <h3>License:</h3>
            <p>MIT License - Free for personal and commercial use</p>
            
            <p style="margin-top: 20px;">Made with ❤️ for the Python community</p>
        """)
        layout.addWidget(about_text)
        
    def browse_script(self):
        """Browse for Python script"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Python Script", "",
            "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.script_path_edit.setText(file_path)
            self.script_path = Path(file_path)
            # Auto-generate name
            if not self.name_edit.text():
                self.name_edit.setText(self.script_path.stem)
                
    def browse_output(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory",
            self.output_edit.text()
        )
        if directory:
            self.output_edit.setText(directory)
            
    def browse_icon(self):
        """Browse for icon file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon File", "",
            "Icon Files (*.ico);;All Files (*)"
        )
        if file_path:
            self.icon_edit.setText(file_path)
            
    def check_dependencies(self):
        """Check if PyInstaller is installed"""
        try:
            subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                         capture_output=True, check=True)
            self.status_bar.showMessage("✅ PyInstaller is installed", 3000)
        except:
            reply = QMessageBox.question(
                self, "Missing Dependency",
                "PyInstaller is not installed. Would you like to install it now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.install_pyinstaller()
                
    def install_pyinstaller(self):
        """Install PyInstaller"""
        try:
            self.status_bar.showMessage("Installing PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                         check=True)
            self.status_bar.showMessage("✅ PyInstaller installed successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Installation Failed",
                               f"Failed to install PyInstaller: {str(e)}")
            
    def start_build(self):
        """Start the build process"""
        if not self.script_path_edit.text():
            QMessageBox.warning(self, "No Script", "Please select a Python script to compile.")
            return
            
        if not os.path.exists(self.script_path_edit.text()):
            QMessageBox.warning(self, "Invalid Script", "The selected script does not exist.")
            return
            
        # Disable build button
        self.build_btn.setEnabled(False)
        self.build_btn.setText("⏳ Building...")
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        # Prepare options
        options = {
            'onefile': self.onefile_check.isChecked(),
            'console': self.console_check.isChecked(),
            'icon': self.icon_edit.text(),
            'name': self.name_edit.text(),
            'hidden_imports': self.hidden_imports_edit.text(),
            'add_data': self.add_data_edit.text()
        }
        
        # Create worker thread
        self.build_worker = BuildWorker(
            Path(self.script_path_edit.text()),
            Path(self.output_edit.text()),
            options
        )
        
        # Connect signals
        self.build_worker.log_signal.connect(self.append_log)
        self.build_worker.progress_signal.connect(self.progress_bar.setValue)
        self.build_worker.finished_signal.connect(self.build_finished)
        
        # Start build
        self.build_worker.start()
        
    def append_log(self, text):
        """Append text to log"""
        self.log_text.append(text)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def build_finished(self, success, message):
        """Handle build completion"""
        self.build_btn.setEnabled(True)
        self.build_btn.setText("🔨 BUILD EXECUTABLE")
        
        if success:
            QMessageBox.information(self, "Build Successful", message)
            self.status_bar.showMessage("✅ Build completed successfully!")
        else:
            QMessageBox.critical(self, "Build Failed", message)
            self.status_bar.showMessage("❌ Build failed")
            
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application icon (optional)
    app.setWindowIcon(QIcon())
    
    window = PyBuilderGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()