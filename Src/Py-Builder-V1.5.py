#!/usr/bin/env python3
"""
PyBuilder Pro - Professional Python to EXE Compiler (Advanced Performance Edition)
Fixed for PyInstaller v6.0+ compatibility
"""

import sys
import os
import subprocess
import threading
import shutil
import json
import tempfile
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    print("PyQt5 is required. Install it using: pip install PyQt5")
    sys.exit(1)

class PerformanceOptimizer:
    """Advanced performance optimization strategies"""
    
    @staticmethod
    def get_pyinstaller_version() -> tuple:
        """Get PyInstaller version for compatibility checks"""
        try:
            result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                                   capture_output=True, text=True)
            version_str = result.stdout.strip()
            parts = version_str.split('.')
            if len(parts) >= 2:
                return (int(parts[0]), int(parts[1]))
        except:
            pass
        return (0, 0)  # Unknown version
    
    @staticmethod
    def analyze_imports(script_path: Path) -> List[str]:
        """Analyze script imports for better dependency management"""
        imports = set()
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import ast
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
        except Exception as e:
            print(f"Import analysis warning: {e}")
        return list(imports)
    
    @staticmethod
    def get_optimized_pyinstaller_args(script_path: Path, options: Dict) -> List[str]:
        """Generate highly optimized PyInstaller arguments (v6.0+ compatible)"""
        args = []
        
        # Core optimizations
        args.extend([
            "--noconfirm",  # Override output directory without asking
            "--clean",      # Clean PyInstaller cache
        ])
        
        # Strip debug symbols (reduces size)
        if options.get('strip', True):
            args.append("--strip")
        
        # UPX compression (optional)
        if options.get('use_upx', True):
            if shutil.which("upx"):
                args.append("--upx-dir=.")
            else:
                print("UPX not found in PATH. Install UPX for smaller executables.")
        
        # Optimization flags
        args.append("--optimize=2")  # Maximum Python optimization
        
        # Collect all imports for better dependency resolution
        if options.get('collect_imports', True):
            imports = PerformanceOptimizer.analyze_imports(script_path)
            for imp in imports:
                if imp not in ['sys', 'os', 're', 'time', 'datetime']:  # Skip builtins
                    args.append(f"--collect-all={imp}")
        
        # Exclude modules (reduce size)
        if options.get('exclude_modules'):
            for module in options['exclude_modules'].split(','):
                if module.strip():
                    args.append(f"--exclude-module={module.strip()}")
        
        return args

class BuildWorker(QThread):
    """Enhanced worker thread with performance monitoring"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    perf_signal = pyqtSignal(dict)
    
    def __init__(self, script_path, output_dir, options):
        super().__init__()
        self.script_path = script_path
        self.output_dir = output_dir
        self.options = options
        self.start_time = None
        
    def run(self):
        self.start_time = datetime.now()
        perf_data = {}
        
        try:
            self.log_signal.emit("⚡ Advanced optimization build started...")
            self.progress_signal.emit(5)
            
            # Check PyInstaller version
            pyinstaller_version = PerformanceOptimizer.get_pyinstaller_version()
            self.log_signal.emit(f"📦 PyInstaller version: {pyinstaller_version[0]}.{pyinstaller_version[1]}")
            
            # Create optimized build environment
            build_dir = self.output_dir / f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            build_dir.mkdir(exist_ok=True)
            
            # Prepare PyInstaller command (v6.0+ compatible)
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--workpath", str(build_dir / "build"),
                "--distpath", str(self.output_dir),
                "--specpath", str(build_dir),
            ]
            
            # Add performance optimizations
            cmd.extend(PerformanceOptimizer.get_optimized_pyinstaller_args(
                self.script_path, self.options
            ))
            
            # Add user options
            if self.options.get('onefile', True):
                cmd.append("--onefile")
            else:
                cmd.append("--onedir")
                
            if not self.options.get('console', False):
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
            
            # Add data files
            if self.options.get('add_data'):
                for data in self.options['add_data'].split(','):
                    if data.strip():
                        cmd.append(f"--add-data={data.strip()}")
            
            # Windows-specific optimizations (v6.0+ compatible)
            if platform.system() == "Windows" and self.options.get('uac_admin', False):
                cmd.append("--uac-admin")
            
            # Add the script
            cmd.append(str(self.script_path))
            
            self.log_signal.emit(f"🚀 Running optimized PyInstaller...")
            self.log_signal.emit(f"Command: {' '.join(cmd[:5])}... (truncated)")
            self.progress_signal.emit(20)
            
            # Run PyInstaller with performance monitoring
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.output_dir),
                bufsize=1,
                env=self.get_optimized_env()
            )
            
            # Monitor progress with better accuracy
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    # Show important messages
                    if any(keyword in line for keyword in ['INFO:', 'WARNING:', 'ERROR:']):
                        self.log_signal.emit(line)
                    
                    # Update progress based on keywords
                    if "Building EXE" in line:
                        self.progress_signal.emit(60)
                    elif "Building COLLECT" in line:
                        self.progress_signal.emit(80)
                    elif "completed successfully" in line:
                        self.progress_signal.emit(95)
                    
            process.wait()
            
            perf_data['build_time'] = (datetime.now() - self.start_time).total_seconds()
            
            if process.returncode == 0:
                # Find the generated executable
                exe_name = self.options.get('name', self.script_path.stem)
                if platform.system() == "Windows" and not exe_name.endswith('.exe'):
                    exe_name += '.exe'
                
                exe_path = self.output_dir / exe_name
                
                if exe_path.exists():
                    # Get file size for performance report
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    self.log_signal.emit(f"✅ Executable size: {size_mb:.2f} MB")
                    
                    # Post-build optimization tips
                    self.post_build_optimization_tips(exe_path)
                
                self.progress_signal.emit(100)
                self.log_signal.emit(f"✅ Build completed in {perf_data['build_time']:.2f} seconds!")
                
                # Show performance report
                self.perf_signal.emit(perf_data)
                self.finished_signal.emit(True, 
                    f"Executable created: {exe_path}\nBuild time: {perf_data['build_time']:.2f} seconds")
            else:
                self.log_signal.emit("❌ Build failed with errors")
                self.finished_signal.emit(False, "Build failed. Check the logs for details.")
                
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {str(e)}")
            self.finished_signal.emit(False, str(e))
        finally:
            # Cleanup build directory if option enabled
            if self.options.get('cleanup_build', True) and build_dir.exists():
                try:
                    shutil.rmtree(build_dir, ignore_errors=True)
                    self.log_signal.emit("🧹 Build files cleaned up")
                except:
                    pass
    
    def get_optimized_env(self) -> dict:
        """Get optimized environment variables"""
        env = os.environ.copy()
        
        # Performance optimizations
        env['PYTHONOPTIMIZE'] = '2'
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        
        # Reduce memory usage for large builds
        env['PYTHONHASHSEED'] = '0'
        
        # Windows-specific optimizations
        if platform.system() == "Windows":
            env['PYTHONLEGACYWINDOWSFSENCODING'] = '1'
        
        return env
    
    def post_build_optimization_tips(self, exe_path: Path):
        """Provide post-build optimization tips"""
        tips = []
        
        # Check if UPX was used
        if not self.options.get('use_upx', True):
            tips.append("💡 Tip: Install UPX (https://upx.github.io/) to reduce executable size by 30-50%")
        
        # Check executable size
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            tips.append("⚠️  Large executable detected. Consider excluding unused modules using 'Exclude Modules' option")
        
        # Startup speed tip
        if self.options.get('onefile', True):
            tips.append("💡 For faster startup, consider using 'onedir' mode instead of 'onefile'")
        
        for tip in tips:
            self.log_signal.emit(tip)

class PyBuilderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_path = None
        self.build_worker = None
        self.init_ui()
        self.check_dependencies()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("PyBuilder Pro - Performance Edition (v6.0+ Compatible)")
        self.setGeometry(100, 100, 1000, 750)
        
        # Set enhanced dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #d4d4d4;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0a4d75;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 5px;
                color: #d4d4d4;
                font-family: 'Consolas', monospace;
            }
            QGroupBox {
                color: #d4d4d4;
                border: 2px solid #3e3e3e;
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
                color: #d4d4d4;
            }
            QTabWidget::pane {
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #d4d4d4;
                padding: 8px 16px;
            }
            QTabBar::tab:selected {
                background-color: #0e639c;
            }
            QProgressBar {
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                text-align: center;
                color: white;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #0e639c;
                border-radius: 3px;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #0e639c;
                border-radius: 6px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header with performance badge
        header_layout = QHBoxLayout()
        header_label = QLabel("🚀 PyBuilder Pro - Performance Edition")
        header_font = QFont("Segoe UI", 16, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #0e639c;")
        header_layout.addWidget(header_label)
        
        perf_badge = QLabel("⚡ FAST EXE BUILDER")
        perf_badge.setStyleSheet("""
            background-color: #0e639c;
            color: white;
            padding: 5px 10px;
            border-radius: 10px;
            font-weight: bold;
        """)
        header_layout.addWidget(perf_badge)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Build tab
        build_tab = QWidget()
        tabs.addTab(build_tab, "📦 Build")
        
        # Performance tab
        perf_tab = QWidget()
        tabs.addTab(perf_tab, "⚡ Performance")
        
        # About tab
        about_tab = QWidget()
        tabs.addTab(about_tab, "ℹ️ About")
        
        # Setup tabs
        self.setup_build_tab(build_tab)
        self.setup_performance_tab(perf_tab)
        self.setup_about_tab(about_tab)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready for high-performance builds")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def setup_build_tab(self, tab):
        """Setup the build tab interface"""
        layout = QVBoxLayout(tab)
        
        # File selection
        file_group = QGroupBox("📁 Python Script Selection")
        file_layout = QVBoxLayout()
        
        script_layout = QHBoxLayout()
        self.script_path_edit = QLineEdit()
        self.script_path_edit.setPlaceholderText("Select Python script to compile...")
        script_layout.addWidget(self.script_path_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_script)
        script_layout.addWidget(browse_btn)
        file_layout.addLayout(script_layout)
        
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
        
        self.onefile_check = QCheckBox("Single File Executable (Easier distribution)")
        self.onefile_check.setChecked(True)
        options_layout.addWidget(self.onefile_check, 0, 0)
        
        self.console_check = QCheckBox("Show Console Window")
        self.console_check.setChecked(False)
        options_layout.addWidget(self.console_check, 0, 1)
        
        self.upx_check = QCheckBox("Use UPX Compression (Smaller EXE, optional)")
        self.upx_check.setChecked(False)  # Disabled by default for faster startup
        options_layout.addWidget(self.upx_check, 1, 0)
        
        self.strip_check = QCheckBox("Strip Debug Symbols (Smaller EXE)")
        self.strip_check.setChecked(True)
        options_layout.addWidget(self.strip_check, 1, 1)
        
        options_layout.addWidget(QLabel("Executable Name:"), 2, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Leave empty for auto-name")
        options_layout.addWidget(self.name_edit, 2, 1)
        
        options_layout.addWidget(QLabel("Icon File (.ico):"), 3, 0)
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit()
        icon_layout.addWidget(self.icon_edit)
        icon_browse_btn = QPushButton("Browse")
        icon_browse_btn.clicked.connect(self.browse_icon)
        icon_layout.addWidget(icon_browse_btn)
        options_layout.addLayout(icon_layout, 3, 1)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Build button
        self.build_btn = QPushButton("⚡ BUILD OPTIMIZED EXECUTABLE")
        self.build_btn.setMinimumHeight(50)
        self.build_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.build_btn.clicked.connect(self.start_build)
        layout.addWidget(self.build_btn)
        
        # Log output
        log_group = QGroupBox("📋 Build Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_log_btn)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def setup_performance_tab(self, tab):
        """Setup performance optimization settings"""
        layout = QVBoxLayout(tab)
        
        # Performance settings
        perf_group = QGroupBox("🎯 Advanced Optimizations")
        perf_layout = QGridLayout()
        
        perf_layout.addWidget(QLabel("Exclude Modules (comma-separated):"), 0, 0)
        self.exclude_modules_edit = QLineEdit()
        self.exclude_modules_edit.setPlaceholderText("e.g., tkinter, unittest, test, distutils, email, html")
        self.exclude_modules_edit.setText("tkinter, unittest, test, distutils, email, html, http, xml, curses, pdb")
        perf_layout.addWidget(self.exclude_modules_edit, 0, 1)
        
        perf_layout.addWidget(QLabel("Hidden Imports (comma-separated):"), 1, 0)
        self.hidden_imports_edit = QLineEdit()
        self.hidden_imports_edit.setPlaceholderText("e.g., numpy._core, pandas._libs, PyQt5.sip")
        perf_layout.addWidget(self.hidden_imports_edit, 1, 1)
        
        perf_layout.addWidget(QLabel("Additional Data Files:"), 2, 0)
        self.add_data_edit = QLineEdit()
        self.add_data_edit.setPlaceholderText("e.g., data/*.json;., config.yml;.")
        perf_layout.addWidget(self.add_data_edit, 2, 1)
        
        self.auto_import_check = QCheckBox("Auto-detect and collect all imports (Better compatibility)")
        self.auto_import_check.setChecked(True)
        perf_layout.addWidget(self.auto_import_check, 3, 0, 1, 2)
        
        self.cleanup_check = QCheckBox("Clean up build files after completion")
        self.cleanup_check.setChecked(True)
        perf_layout.addWidget(self.cleanup_check, 4, 0, 1, 2)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Optimization tips
        tips_group = QGroupBox("💡 Performance Optimization Tips")
        tips_text = QTextEdit()
        tips_text.setReadOnly(True)
        tips_text.setHtml("""
            <h3 style="color: #0e639c;">⚡ Startup Speed Optimizations:</h3>
            <ul>
                <li><b>--onefile vs --onedir:</b> Onefile extracts to temp folder (slower startup). Use --onedir for fastest startup (2-3x faster).</li>
                <li><b>UPX Compression:</b> Reduces EXE size by 30-50% but increases startup time by 20-30%. Disable for maximum speed.</li>
                <li><b>Exclude unused modules:</b> Smaller EXE = faster loading. Exclude tkinter, unittest, email, html if not needed.</li>
                <li><b>Strip debug symbols:</b> Reduces size without affecting startup speed. Always enable this.</li>
            </ul>
            
            <h3 style="color: #0e639c;">🚀 Recommended Settings by Use Case:</h3>
            <ul>
                <li><b>Maximum Startup Speed:</b> --onedir, no UPX, strip enabled, exclude heavy modules</li>
                <li><b>Smallest File Size:</b> --onefile, UPX enabled, strip enabled, exclude all possible modules</li>
                <li><b>Best Balance:</b> --onefile, no UPX, strip enabled, exclude common unused modules</li>
                <li><b>GUI Applications:</b> --onefile, noconsole, exclude tkinter (if using PyQt/PySide)</li>
            </ul>
            
            <h3 style="color: #0e639c;">📊 Performance Comparison:</h3>
            <ul>
                <li><b>Onefile + UPX:</b> Slowest startup, smallest size</li>
                <li><b>Onefile + No UPX:</b> Medium startup, medium size</li>
                <li><b>Onedir + No UPX:</b> Fastest startup, larger folder size</li>
            </ul>
            
            <h3 style="color: #0e639c;">🔧 Troubleshooting:</h3>
            <ul>
                <li>If executable crashes, disable 'Auto-detect imports' and manually specify hidden imports</li>
                <li>If missing DLLs, use 'Additional Data Files' to include them</li>
                <li>For PyQt5 apps, add 'PyQt5.sip' to hidden imports</li>
            </ul>
        """)
        tips_group.setLayout(QVBoxLayout())
        tips_group.layout().addWidget(tips_text)
        layout.addWidget(tips_group)
        
        # Add stretch
        layout.addStretch()
        
    def setup_about_tab(self, tab):
        """Setup the about tab"""
        layout = QVBoxLayout(tab)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
            <h1 style="color: #0e639c;">PyBuilder Pro - Performance Edition</h1>
            <h3>Version 2.1.0 (PyInstaller v6.0+ Compatible)</h3>
            <p>Professional Python to EXE compiler with advanced performance optimizations.</p>
            
            <h3 style="color: #0e639c;">⚡ Performance Features:</h3>
            <ul>
                <li>Automatic import analysis for better dependency management</li>
                <li>Intelligent module exclusion for smaller EXE size</li>
                <li>Optimized PyInstaller flags for faster startup</li>
                <li>Strip debug symbols to reduce executable size</li>
                <li>Compatible with PyInstaller v6.0 and newer</li>
                <li>Build cache management for faster rebuilds</li>
            </ul>
            
            <h3 style="color: #0e639c;">📈 Performance Tips:</h3>
            <ul>
                <li><b>For maximum speed:</b> Use --onedir mode (not onefile)</li>
                <li><b>For smallest size:</b> Use --onefile with UPX compression</li>
                <li><b>Disable UPX</b> if startup speed is critical</li>
                <li><b>Exclude tkinter, unittest, email, html</b> if your app doesn't need them</li>
            </ul>
            
            <h3>Requirements:</h3>
            <ul>
                <li>Python 3.7+</li>
                <li>PyInstaller 5.0+ (v6.0+ recommended)</li>
                <li>PyQt5 for GUI</li>
                <li>UPX (optional, for compression)</li>
            </ul>
            
            <h3>Installation:</h3>
            <code>pip install pyinstaller PyQt5</code>
            
            <p style="margin-top: 20px;">Made with ❤️ for high-performance Python applications</p>
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
            result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                                   capture_output=True, text=True)
            version = result.stdout.strip()
            self.status_bar.showMessage(f"✅ PyInstaller {version} detected", 3000)
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
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"],
                         check=True)
            self.status_bar.showMessage("✅ PyInstaller installed successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Installation Failed",
                               f"Failed to install PyInstaller: {str(e)}")
            
    def start_build(self):
        """Start the build process with optimizations"""
        if not self.script_path_edit.text():
            QMessageBox.warning(self, "No Script", "Please select a Python script to compile.")
            return
            
        if not os.path.exists(self.script_path_edit.text()):
            QMessageBox.warning(self, "Invalid Script", "The selected script does not exist.")
            return
            
        # Disable build button
        self.build_btn.setEnabled(False)
        self.build_btn.setText("⚡ Optimizing and Building...")
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        # Prepare optimized options
        options = {
            'onefile': self.onefile_check.isChecked(),
            'console': self.console_check.isChecked(),
            'use_upx': self.upx_check.isChecked(),
            'strip': self.strip_check.isChecked(),
            'collect_imports': self.auto_import_check.isChecked(),
            'icon': self.icon_edit.text(),
            'name': self.name_edit.text() if self.name_edit.text() else None,
            'hidden_imports': self.hidden_imports_edit.text(),
            'add_data': self.add_data_edit.text(),
            'exclude_modules': self.exclude_modules_edit.text(),
            'cleanup_build': self.cleanup_check.isChecked(),
            'uac_admin': False,  # Optional: request admin privileges
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
        self.build_worker.perf_signal.connect(self.show_performance_report)
        
        # Start build
        self.build_worker.start()
        
    def append_log(self, text):
        """Append text to log"""
        self.log_text.append(text)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def show_performance_report(self, perf_data):
        """Show performance report"""
        report = f"\n{'='*50}\n⚡ PERFORMANCE REPORT:\n{'='*50}\n"
        report += f"• Build Time: {perf_data.get('build_time', 0):.2f} seconds\n"
        report += f"{'='*50}\n"
        self.log_text.append(report)
        
    def build_finished(self, success, message):
        """Handle build completion"""
        self.build_btn.setEnabled(True)
        self.build_btn.setText("⚡ BUILD OPTIMIZED EXECUTABLE")
        
        if success:
            QMessageBox.information(self, "Build Successful", 
                f"{message}\n\nPerformance optimizations applied!")
            self.status_bar.showMessage("✅ Build completed successfully!")
        else:
            QMessageBox.critical(self, "Build Failed", message)
            self.status_bar.showMessage("❌ Build failed")
            
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = PyBuilderGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()