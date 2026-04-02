#!/usr/bin/env python3
"""
Simple Menu Script - Auto Run from Src Directory
"""

import os
import sys
import subprocess
from pathlib import Path

# ============================================
# ASCII BANNER
# ============================================

BANNER = """

                                                              
██████╗   ██╗   ██╗          ██████╗   ██╗   ██╗  ██╗  ██╗       ██████╗   ███████╗  ██████╗   
██╔══██╗  ╚██╗ ██╔╝          ██╔══██╗  ██║   ██║  ██║  ██║       ██╔══██╗  ██╔════╝  ██╔══██╗  
██████╔╝   ╚████╔╝   ██████  ██████╔╝  ██║   ██║  ██║  ██║       ██║  ██║  █████╗    ██████╔╝  
██╔═══╝     ╚██╔╝            ██╔══██╗  ██║   ██║  ██║  ██║       ██║  ██║  ██╔══╝    ██╔══██╗  
██║          ██║             ██████╔╝  ╚██████╔╝  ██║  ███████╗  ██████╔╝  ███████╗  ██║  ██║  
╚═╝          ╚═╝             ╚═════╝    ╚═════╝   ╚═╝  ╚══════╝  ╚═════╝   ╚══════╝  ╚═╝  ╚═╝                 
                                          CREATED BY ATHEX BLACK HAT   
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