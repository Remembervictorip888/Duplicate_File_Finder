#!/usr/bin/env python3
"""
Setup and Run Automation Script for Duplicate File Finder

This script automates the entire process:
1. Checks and installs Python dependencies as needed
2. Sets up necessary environment
3. Runs the appropriate program based on user choice
"""

import sys
import os
import subprocess
from pathlib import Path
import platform
import argparse
import re


def read_requirements(requirements_path):
    """Read requirements from a file and return a list of requirements"""
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.strip().startswith('#')
        ]
    return requirements


def check_installed_packages(requirements):
    """Check which packages are already installed with correct versions"""
    missing_or_outdated = []
    
    for req in requirements:
        if not req or req.startswith('#'):
            continue
            
        try:
            # Try to install package in dry-run mode to check if it's available
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--dry-run', req
            ], capture_output=True, text=True)
            
            # If return code is not 0, or if the dry run shows it would install something,
            # then the package is missing or outdated
            if result.returncode != 0 or "Would install" in result.stdout or "Would update" in result.stderr:
                print(f"✗ {req} needs to be installed/updated")
                missing_or_outdated.append(req)
            else:
                print(f"✓ {req} is already satisfied")
        except Exception as e:
            print(f"⚠ Error checking {req}: {e}")
            missing_or_outdated.append(req)
    
    return missing_or_outdated


def install_packages(packages):
    """Install the specified packages using pip"""
    if not packages:
        print("No packages to install.")
        return True
    
    print(f"Installing {len(packages)} packages...")
    
    # Create a temporary requirements file for installation
    with open('.temp_requirements.txt', 'w', encoding='utf-8') as temp_file:
        for package in packages:
            temp_file.write(package + '\n')
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', '.temp_requirements.txt'
        ], check=True, capture_output=True, text=True)
        
        print("Installation completed successfully!")
        if result.stdout:
            print(result.stdout[-500:])  # Print last 500 chars of output
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        print(e.stderr)
        return False
    finally:
        # Clean up the temporary file
        Path('.temp_requirements.txt').unlink(missing_ok=True)
    
    return True


def check_and_install_python_deps():
    """Check and install Python dependencies if needed"""
    requirements_file = 'requirements.txt'
    
    if not Path(requirements_file).exists():
        print(f"Error: {requirements_file} not found in the current directory.")
        return False
    
    print("Checking Python dependencies...")
    requirements = read_requirements(requirements_file)
    
    print(f"Found {len(requirements)} requirements in {requirements_file}")
    
    missing_or_outdated = check_installed_packages(requirements)
    
    if not missing_or_outdated:
        print("\nAll Python requirements are already satisfied!")
        return True
    else:
        print(f"\nFound {len(missing_or_outdated)} packages that need installation or update:")
        for pkg in missing_or_outdated:
            print(f"  - {pkg}")
        
        success = install_packages(missing_or_outdated)
        if success:
            print("\nAll Python dependencies are now up to date!")
            return True
        else:
            print("\nFailed to install some Python dependencies.")
            return False


def check_node_environment():
    """Check if Node.js and npm are available"""
    node_available = False
    npm_available = False
    
    try:
        node_result = subprocess.run(['node', '--version'], 
                                    capture_output=True, text=True, check=True)
        print(f"✓ Node.js version: {node_result.stdout.strip()}")
        node_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Node.js not found in PATH")
        return False  # If Node.js is not available, we can't proceed
    
    try:
        npm_result = subprocess.run(['npm', '--version'], 
                                    capture_output=True, text=True, check=True)
        print(f"✓ npm version: {npm_result.stdout.strip()}")
        npm_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ npm not found in PATH")
        npm_available = False
    
    # We need both Node.js and npm for the GUI to work properly
    return node_available and npm_available


def install_node_deps():
    """Install Node.js dependencies using npm"""
    try:
        print("Installing Node.js dependencies...")
        result = subprocess.run(['npm', 'install'], 
                                capture_output=True, text=True, check=True)
        print("Node.js dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Node.js dependencies: {e}")
        print("This might be because 'npm install' requires a package.json file.")
        print("Make sure you're running this script from the project root directory.")
        return False


def setup_environment():
    """Set up the necessary environment"""
    print("Setting up environment...")
    
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        print("[OK] Created logs directory")
    else:
        print("[OK] Logs directory already exists")
    
    # Check and install Python dependencies
    python_success = check_and_install_python_deps()
    if not python_success:
        print("Failed to install Python dependencies.")
        return False
    
    # Check Node.js environment
    node_available = check_node_environment()
    if node_available:
        # Install Node.js dependencies if needed
        node_success = install_node_deps()
        if not node_success:
            print("Failed to install Node.js dependencies, but continuing...")
    else:
        print("Node.js or npm not found in PATH. GUI mode will not work, but you can use CLI mode.")
    
    print("Environment setup completed!")
    return True


def run_cli_app(directory=None, extensions=None, method=None, skip_build_dirs=False):
    """Run the command-line interface version of the app"""
    cmd = [sys.executable, 'main.py']
    
    if directory:
        cmd.append(directory)
    
    if extensions:
        cmd.extend(['--extensions'] + extensions)
    
    if method:
        cmd.extend(['--method', method])
    
    if skip_build_dirs:
        # Create a temporary ignore list file with the correct format
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_ignore_list.txt', delete=False) as f:
            f.write("# Auto-generated ignore list to skip build directories\n")
            f.write("DIR:node_modules\n")      # node_modules directory
            f.write("DIR:.git\n")             # .git directory
            f.write("DIR:.svn\n")             # .svn directory
            f.write("DIR:.hg\n")              # .hg directory
            f.write("DIR:dist\n")             # dist directory
            f.write("DIR:build\n")            # build directory
            f.write("DIR:target\n")           # target directory (Rust/Java)
            f.write("DIR:.vscode\n")          # VSCode settings
            f.write("DIR:.idea\n")            # IntelliJ/PyCharm settings
            f.write("DIR:__pycache__\n")      # Python cache
            f.write("DIR:.pytest_cache\n")    # pytest cache
            f.write("DIR:.next\n")            # Next.js cache
            f.write("DIR:out\n")              # Output directory
            ignore_file = f.name
        
        cmd.extend(['--ignore-list-file', ignore_file])
        
        try:
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Error running the CLI app: {e}")
            return e.returncode
        except FileNotFoundError:
            print("Error: main.py not found in the current directory.")
            return 1
        finally:
            # Clean up the temporary file
            import os
            os.remove(ignore_file)
    else:
        try:
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Error running the CLI app: {e}")
            return e.returncode
        except FileNotFoundError:
            print("Error: main.py not found in the current directory.")
            return 1


def run_electron_app():
    """Run the Electron GUI version of the app"""
    node_available = check_node_environment()
    if not node_available:
        print("GUI mode requires Node.js and npm. Please install Node.js which includes npm and ensure both are in your PATH.")
        print("You can download Node.js from https://nodejs.org/")
        print("After installing, restart your terminal and run this script again.")
        return 1
    
    try:
        print("Starting Electron app (this will start both dev server and Electron)...")
        print("Note: This may take a moment to start up...")
        
        # Run npm start which should start both the dev server and Electron
        result = subprocess.run(['npm', 'start'], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running the Electron app: {e}")
        print("Make sure you have run 'npm install' in the project directory.")
        return e.returncode
    except FileNotFoundError:
        print("Error: npm not found or package.json not in the current directory.")
        print("Please run 'npm install' first to install the required dependencies.")
        return 1


def main():
    parser = argparse.ArgumentParser(description='Setup and run Duplicate File Finder')
    parser.add_argument('--mode', choices=['cli', 'gui'], default='gui',
                        help='Run mode: cli (command line) or gui (Electron app) [default: gui]')
    parser.add_argument('directory', nargs='?', 
                        help='Directory to scan for duplicates (CLI mode only)')
    parser.add_argument('--extensions', nargs='+',
                        help='File extensions to include in scan (CLI mode only)')
    parser.add_argument('--method', choices=['hash', 'size', 'name'],
                        help='Detection method to use (CLI mode only)')
    parser.add_argument('--skip-build-dirs', action='store_true',
                        help='Skip common build directories like node_modules, .git, etc. for faster scanning')
    
    args = parser.parse_args()
    
    print("Duplicate File Finder - Setup and Run Automation")
    print("="*50)
    
    # Setup environment
    if not setup_environment():
        print("Environment setup failed. Exiting.")
        sys.exit(1)
    
    print("\nRunning the application...")
    
    if args.mode == 'cli':
        exit_code = run_cli_app(
            directory=args.directory,
            extensions=args.extensions,
            method=args.method,
            skip_build_dirs=args.skip_build_dirs
        )
    else:  # gui mode (now the default)
        # Check if npm is available before attempting to run the Electron app
        node_available = check_node_environment()
        if node_available:
            # Check if package.json exists and install dependencies if needed
            if not Path('package.json').exists():
                print("package.json not found. GUI mode cannot be started.")
                print("You can run in CLI mode using: python setup_and_run.py --mode cli")
                sys.exit(1)
            
            exit_code = run_electron_app()
        else:
            # npm is not available, try to provide alternatives
            print("\nGUI mode requires both Node.js and npm to be available in your PATH.")
            print("The Electron-based GUI application cannot be started.")
            print("\nHowever, you can still use the Python-based GUI if available.")
            
            # Check if tkinter is available for a simple GUI
            try:
                import tkinter
                from tkinter import filedialog
                
                print("\nPython GUI components are available. Would you like to try the Python-based file selector?")
                print("This will allow you to select a directory for scanning.")
                
                use_python_gui = input("Use Python GUI for directory selection? (y/n): ").lower().strip()
                
                if use_python_gui.startswith('y'):
                    root = tkinter.Tk()
                    root.withdraw()  # Hide the main window
                    
                    directory = filedialog.askdirectory(title="Select Directory to Scan for Duplicates")
                    
                    if directory:
                        print(f"Selected directory: {directory}")
                        exit_code = run_cli_app(
                            directory=directory,
                            extensions=args.extensions,
                            method=args.method,
                            skip_build_dirs=args.skip_build_dirs
                        )
                    else:
                        print("No directory selected. Exiting.")
                        exit_code = 1
                else:
                    print("\nAs an alternative, you can run in CLI mode using:")
                    print("  python setup_and_run.py --mode cli [directory]")
                    print("\nOr install dependencies with: npm install")
                    exit_code = 1
            except ImportError:
                print("\nPython GUI components (tkinter) are not available.")
                print("\nAs an alternative, you can run in CLI mode using:")
                print("  python setup_and_run.py --mode cli [directory]")
                print("\nOr install dependencies with: npm install")
                exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()