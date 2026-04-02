#!/usr/bin/env python3
"""
Auto Installer & Launcher 
Installs all dependencies and launches the main application
"""

import sys
import os
import subprocess
import platform
import time
import shutil
from pathlib import Path

class PyBuilderInstaller:
    """Automatic dependency installer and launcher"""
    
    def __init__(self):
        self.python_exe = sys.executable
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        self.venv_path = Path.cwd() / "pybuilder_env"
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def print_step(self, text):
        """Print step with checkmark"""
        print(f"  📦 {text}...")
    
    def print_success(self, text):
        """Print success message"""
        print(f"  ✅ {text}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"  ❌ {text}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"  ⚠️  {text}")
    
    def check_python_version(self):
        """Check if Python version is sufficient"""
        self.print_step("Checking Python version")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 7:
            self.print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
            return True
        else:
            self.print_error(f"Python 3.7+ required (found {version.major}.{version.minor})")
            return False
    
    def create_virtual_env(self):
        """Create virtual environment"""
        self.print_step("Creating virtual environment")
        
        # Check if venv already exists
        if self.venv_path.exists():
            response = input("  Virtual environment already exists. Recreate? (y/N): ")
            if response.lower() == 'y':
                self.print_step("Removing old virtual environment")
                shutil.rmtree(self.venv_path)
            else:
                self.print_success("Using existing virtual environment")
                return True
        
        try:
            subprocess.run([self.python_exe, "-m", "venv", str(self.venv_path)], 
                         check=True, capture_output=True)
            self.print_success("Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to create virtual environment: {e}")
            return False
    
    def get_pip_path(self):
        """Get pip path inside virtual environment"""
        if self.is_windows:
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def get_python_path(self):
        """Get python path inside virtual environment"""
        if self.is_windows:
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        self.print_step("Upgrading pip")
        pip_path = self.get_pip_path()
        
        try:
            subprocess.run([str(pip_path), "install", "--upgrade", "pip", "setuptools", "wheel"],
                         check=True, capture_output=True, timeout=60)
            self.print_success("Pip upgraded successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.print_warning(f"Pip upgrade failed: {e}")
            return True  # Continue anyway
    
    def install_dependencies(self):
        """Install all required dependencies"""
        dependencies = [
            "nuitka>=4.0.0",
            "PyQt5>=5.15.0",
            "ordered-set",  # For faster imports
            "zstandard",    # For better compression
        ]
        
        # Optional dependencies for better performance
        optional_deps = [
            "ccache",  # For faster C compilation (may fail on Windows)
        ]
        
        self.print_step(f"Installing {len(dependencies)} core dependencies")
        pip_path = self.get_pip_path()
        
        for dep in dependencies:
            try:
                self.print_step(f"  Installing {dep}")
                subprocess.run([str(pip_path), "install", dep], 
                             check=True, capture_output=True, timeout=120)
                self.print_success(f"  {dep} installed")
            except subprocess.CalledProcessError as e:
                self.print_error(f"  Failed to install {dep}: {e}")
                return False
        
        # Try optional dependencies (don't fail if they don't install)
        for dep in optional_deps:
            try:
                self.print_step(f"  Installing optional: {dep}")
                subprocess.run([str(pip_path), "install", dep], 
                             check=True, capture_output=True, timeout=60)
                self.print_success(f"  {dep} installed")
            except:
                self.print_warning(f"  {dep} not available (optional)")
        
        self.print_success("All dependencies installed successfully")
        return True
    
    def check_ccache(self):
        """Check if ccache is available for faster builds"""
        if shutil.which("ccache"):
            self.print_success("ccache detected - builds will be faster!")
            return True
        else:
            self.print_warning("ccache not found - install for 50% faster rebuilds")
            if self.is_windows:
                print("    Install: choco install ccache (requires Chocolatey)")
            elif self.is_mac:
                print("    Install: brew install ccache")
            elif self.is_linux:
                print("    Install: sudo apt install ccache")
            return False
    
    def create_launcher_script(self):
        """Create launcher script for easy execution"""
        launcher_name = "run_py_builder.bat" if self.is_windows else "run_py_builder.sh"
        launcher_path = Path.cwd() / launcher_name
        
        if self.is_windows:
            launcher_content = f"""@echo off
echo Starting Py Builder...
call "{self.venv_path}\\Scripts\\activate.bat"
python main.py
pause
"""
        else:
            launcher_content = f"""#!/bin/bash
echo "Starting Py Builder..."
source "{self.venv_path}/bin/activate"
python main.py
"""
        
        try:
            with open(launcher_path, 'w') as f:
                f.write(launcher_content)
            
            if not self.is_windows:
                os.chmod(launcher_path, 0o755)
            
            self.print_success(f"Launcher created: {launcher_path}")
            return launcher_path
        except Exception as e:
            self.print_warning(f"Could not create launcher: {e}")
            return None
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut (Windows only)"""
        if not self.is_windows:
            return
        
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "Py Builder.lnk"
            
            # Create VBS script to create shortcut
            vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{self.get_python_path()}"
oLink.Arguments = "main.py"
oLink.WorkingDirectory = "{Path.cwd()}"
oLink.Description = "Py Builder"
oLink.Save
'''
            vbs_path = Path.cwd() / "create_shortcut.vbs"
            with open(vbs_path, 'w') as f:
                f.write(vbs_script)
            
            subprocess.run(["cscript", "//nologo", str(vbs_path)], check=True)
            vbs_path.unlink()
            self.print_success(f"Desktop shortcut created: {shortcut_path}")
        except Exception as e:
            self.print_warning(f"Could not create desktop shortcut: {e}")
    
    def run_main_script(self):
        """Run the main Py Builder script"""
        self.print_step("Launching Py Builder")
        
        python_path = self.get_python_path()
        main_script = Path.cwd() / "main.py"
        
        if not main_script.exists():
            self.print_error("main.py not found!")
            return False
        
        try:
            # Run the main script
            process = subprocess.Popen([str(python_path), str(main_script)])
            return True
        except Exception as e:
            self.print_error(f"Failed to launch: {e}")
            return False
    
    def install(self):
        """Main installation process"""
        self.print_header("Py Builder - Auto Installer")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Ask for installation
        print("\nThis will install:")
        print("  • Virtual environment (pybuilder_env/)")
        print("  • Nuitka (Python to EXE compiler)")
        print("  • PyQt5 (GUI framework)")
        print("  • Optional: ccache for faster builds")
        print("\nInstallation size: ~100-200 MB")
        
        response = input("\nContinue with installation? (Y/n): ").strip().lower()
        if response and response != 'y':
            print("Installation cancelled.")
            return False
        
        # Create virtual environment
        if not self.create_virtual_env():
            return False
        
        # Upgrade pip
        self.upgrade_pip()
        
        # Install dependencies
        if not self.install_dependencies():
            print("\n⚠️  Some dependencies failed to install.")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return False
        
        # Check for ccache
        self.check_ccache()
        
        # Create launcher
        launcher = self.create_launcher_script()
        
        # Create desktop shortcut (Windows)
        self.create_desktop_shortcut()
        
        # Installation complete
        self.print_header("Installation Complete!")
        print("\n✅ Py Builder is ready to use!")
        
        if launcher:
            print(f"\n  • Run launcher: {launcher}")
            print(f"  • Or activate manually: source {self.venv_path}/bin/activate (Linux/Mac)")
            print(f"  • Or activate manually: {self.venv_path}\\Scripts\\activate (Windows)")
        
        print("\n  • Then run: python main.py")
        
        # Ask to launch now
        response = input("\nLaunch Py Builder now? (Y/n): ").strip().lower()
        if not response or response == 'y':
            self.run_main_script()
        
        return True

def create_main_script():
    """Create the main Py Builder script if it doesn't exist"""
    main_content = '''#!/usr/bin/env python3
"""
Py Builder - 20-30 Second EXE Builder
"""
#!/usr/bin/env python3
"""
Simple Menu Script - Auto Run from Src Directory
"""

import os
import sys
import subprocess
from pathlib import Path


BANNER = """

                                                              
██████╗   ██╗   ██╗          ██████╗   ██╗   ██╗  ██╗  ██╗       ██████╗   ███████╗  ██████╗   
██╔══██╗  ╚██╗ ██╔╝          ██╔══██╗  ██║   ██║  ██║  ██║       ██╔══██╗  ██╔════╝  ██╔══██╗  
██████╔╝   ╚████╔╝   ██████  ██████╔╝  ██║   ██║  ██║  ██║       ██║  ██║  █████╗    ██████╔╝  
██╔═══╝     ╚██╔╝            ██╔══██╗  ██║   ██║  ██║  ██║       ██║  ██║  ██╔══╝    ██╔══██╗  
██║          ██║             ██████╔╝  ╚██████╔╝  ██║  ███████╗  ██████╔╝  ███████╗  ██║  ██║  
╚═╝          ╚═╝             ╚═════╝    ╚═════╝   ╚═╝  ╚══════╝  ╚═════╝   ╚══════╝  ╚═╝  ╚═╝                 
                                                             

"""

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_scripts():
    """Get all Python scripts from Src directory"""
    src_dir = Path.cwd() / "Src"
    
    if not src_dir.exists():
        src_dir.mkdir()
        print(f"\n Created 'Src' directory at: {src_dir}")
        print(" Please add your .py files to this folder")
        input("\nPress Enter to continue...")
        return []
    
    # Get all .py files
    scripts = sorted([f for f in src_dir.glob("*.py") if f.name != "__init__.py"])
    return scripts

def display_menu(scripts):
    """Display menu with script options"""
    print(BANNER)
    print("\n Select Version & Run:\n")
    
    if not scripts:
        print("     No scripts found in 'Src' directory!")
        print("    Please add .py files to the 'Src' folder\n")
        return False
    
    for idx, script in enumerate(scripts, 1):
        # Get file size
        size = script.stat().st_size
        print(f"   {idx}. {script.name} ({size:,} bytes)")
    
    print(f"\n   0. Exit")
    print("\n" + "="*50)
    return True

def run_script(script_path):
    """Run the selected script"""
    print("\n" + "="*50)
    print(f"🚀 RUNNING: {script_path.name}")
    print("="*50 + "\n")
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "="*50)
            print(" SCRIPT EXECUTED SUCCESSFULLY!")
        else:
            print("\n" + "="*50)
            print(f" SCRIPT FAILED (Exit code: {result.returncode})")
        
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\n  Execution interrupted by user")
    except Exception as e:
        print(f"\n Error: {e}")
    
    input("\nPress Enter to continue...")

def main():
    """Main menu loop"""
    while True:
        clear_screen()
        
        scripts = get_scripts()
        
        if not display_menu(scripts):
            input("\nPress Enter to continue...")
            continue
        
        try:
            choice = input("\n👉 Select option: ").strip()
            
            if choice == '0':
                print("\n Goodbye!\n")
                break
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(scripts):
                    run_script(scripts[idx])
                else:
                    print("\n Invalid option!")
                    input("\nPress Enter to continue...")
            else:
                print("\n Please enter a number!")
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n Error: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()

'''
    
    main_file = Path.cwd() / "main.py"
    if not main_file.exists():
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
        print("✅ Created main.py")
    else:
        print("✅ main.py already exists")

if __name__ == "__main__":
    # Create main.py if it doesn't exist
    create_main_script()
    
    # Run installer
    installer = PyBuilderInstaller()
    success = installer.install()
    
    if not success:
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n🎉 Py Builder is ready!")