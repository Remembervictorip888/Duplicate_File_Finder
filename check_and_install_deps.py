#!/usr/bin/env python3
"""
Dependency Management Script for Duplicate File Finder

This script checks for installed packages and installs/updates only the ones
that are missing or outdated according to requirements.txt
"""

import sys
import subprocess
import pkg_resources
from pathlib import Path


def read_requirements(requirements_path):
    """
    Read requirements from a file and return a list of requirements
    """
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.strip().startswith('#')
        ]
    return requirements


def parse_requirement(req):
    """
    Parse a requirement string to extract package name and version spec
    """
    # Handle special characters and comments
    req = req.strip()
    if '#' in req:
        req = req.split('#')[0].strip()
    
    # Extract package name (before comparison operators)
    for op in ['==', '>=', '<=', '>', '<', '!=', '~=']:
        if op in req:
            name = req.split(op)[0]
            return name.strip(), req.strip()
    
    return req.strip(), req.strip()


def check_installed_packages(requirements):
    """
    Check which packages are already installed with correct versions
    """
    missing_or_outdated = []
    
    for req in requirements:
        if not req or req.startswith('#'):
            continue
            
        try:
            # Try to parse and find the requirement
            pkg_name, full_req = parse_requirement(req)
            
            # This will raise DistributionNotFound if package is not installed
            # or VersionConflict if version doesn't meet requirements
            pkg_resources.require(full_req)
            print(f"✓ {full_req} is already satisfied")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            print(f"✗ {full_req} needs to be installed/updated")
            missing_or_outdated.append(req)
        except Exception as e:
            print(f"⚠ Error checking {req}: {e}")
            missing_or_outdated.append(req)
    
    return missing_or_outdated


def install_packages(packages):
    """
    Install the specified packages using pip
    """
    if not packages:
        print("No packages to install.")
        return
    
    print(f"Installing {len(packages)} packages...")
    
    # Create a temporary requirements file for installation
    with open('.temp_requirements.txt', 'w', encoding='utf-8') as temp_file:
        for package in packages:
            temp_file.write(package + '\n')
    
    try:
        # Install packages from the temporary requirements file
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', '.temp_requirements.txt'
        ], check=True, capture_output=True, text=True)
        
        print("Installation completed successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        print(e.stderr)
        return False
    finally:
        # Clean up the temporary file
        Path('.temp_requirements.txt').unlink(missing_ok=True)
    
    return True


def main():
    """
    Main function to check and install dependencies
    """
    requirements_file = 'requirements.txt'
    
    if not Path(requirements_file).exists():
        print(f"Error: {requirements_file} not found in the current directory.")
        sys.exit(1)
    
    print("Checking project dependencies...")
    requirements = read_requirements(requirements_file)
    
    print(f"Found {len(requirements)} requirements in {requirements_file}")
    
    missing_or_outdated = check_installed_packages(requirements)
    
    if not missing_or_outdated:
        print("\nAll requirements are already satisfied!")
        return 0
    else:
        print(f"\nFound {len(missing_or_outdated)} packages that need installation or update:")
        for pkg in missing_or_outdated:
            print(f"  - {pkg}")
        
        # Install missing or outdated packages
        success = install_packages(missing_or_outdated)
        if success:
            print("\nAll dependencies are now up to date!")
            return 0
        else:
            print("\nFailed to install some dependencies.")
            return 1


if __name__ == "__main__":
    sys.exit(main())