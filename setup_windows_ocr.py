#!/usr/bin/env python3
"""
Windows OCR Setup Script for DocFlow
This script helps set up the required OCR dependencies on Windows.
"""
import os
import sys
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path
import subprocess

def check_poppler_installed():
    """Check if Poppler is available in PATH."""
    try:
        result = subprocess.run(['pdftoppm', '-h'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def download_poppler():
    """Download and install Poppler for Windows."""
    print("Downloading Poppler for Windows...")
    
    # Poppler download URL (latest release)
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip"
    poppler_zip = "poppler.zip"
    poppler_dir = "C:\\poppler"
    
    try:
        # Download Poppler
        print("Downloading from GitHub...")
        urllib.request.urlretrieve(poppler_url, poppler_zip)
        
        # Extract Poppler
        print("Extracting Poppler...")
        with zipfile.ZipFile(poppler_zip, 'r') as zip_ref:
            zip_ref.extractall("poppler_temp")
        
        # Move to final location
        if os.path.exists(poppler_dir):
            shutil.rmtree(poppler_dir)
        
        shutil.move("poppler_temp/poppler-24.02.0", poppler_dir)
        
        # Clean up
        os.remove(poppler_zip)
        shutil.rmtree("poppler_temp")
        
        print(f"Poppler installed to: {poppler_dir}")
        
        # Add to PATH
        bin_path = os.path.join(poppler_dir, "Library", "bin")
        current_path = os.environ.get('PATH', '')
        
        if bin_path not in current_path:
            print(f"Please add this path to your Windows PATH environment variable:")
            print(f"  {bin_path}")
            print("\nSteps to add to PATH:")
            print("1. Open System Properties > Advanced > Environment Variables")
            print("2. Edit the 'Path' variable in System Variables")
            print("3. Add the path above")
            print("4. Restart your terminal/IDE")
        
        return True
        
    except Exception as e:
        print(f"Error downloading/installing Poppler: {e}")
        return False

def check_tesseract_installed():
    """Check if Tesseract is available."""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_tesseract_info():
    """Provide information on installing Tesseract."""
    print("\nTesseract OCR Installation:")
    print("1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Install the Windows executable")
    print("3. Make sure it's added to your PATH")
    print("4. Install Russian language pack during installation")

def main():
    """Main setup function."""
    print("DocFlow OCR Setup for Windows")
    print("=" * 40)
    
    if platform.system() != "Windows":
        print("This script is designed for Windows only.")
        return
    
    # Check current status
    print("\nChecking current OCR setup...")
    
    poppler_ok = check_poppler_installed()
    tesseract_ok = check_tesseract_installed()
    
    print(f"Poppler (PDF processing): {'✓ Installed' if poppler_ok else '✗ Not found'}")
    print(f"Tesseract (OCR): {'✓ Installed' if tesseract_ok else '✗ Not found'}")
    
    # Install missing components
    if not poppler_ok:
        print(f"\n{'='*40}")
        print("Installing Poppler...")
        if download_poppler():
            print("✓ Poppler installation completed!")
        else:
            print("✗ Poppler installation failed!")
            print("Manual installation:")
            print("1. Download from: https://github.com/oschwartz10612/poppler-windows/releases")
            print("2. Extract to C:\\poppler")
            print("3. Add C:\\poppler\\Library\\bin to PATH")
    
    if not tesseract_ok:
        print(f"\n{'='*40}")
        install_tesseract_info()
    
    print(f"\n{'='*40}")
    if poppler_ok and tesseract_ok:
        print("✓ All OCR dependencies are installed!")
        print("You can now process PDF files in DocFlow.")
    else:
        print("Please complete the installation steps above.")
        print("After installation, restart your terminal and try again.")

if __name__ == "__main__":
    main()