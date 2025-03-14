#!/usr/bin/env python3
"""
Example script demonstrating how to use the mistral_ocr.py script programmatically.
This is an alternative to using the command-line interface.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_example():
    """Run an example OCR processing job."""
    print("Mistral OCR Example Script")
    print("=========================")
    
    # Check if mistral_ocr.py exists
    if not Path("mistral_ocr.py").exists():
        print("❌ Error: mistral_ocr.py not found in the current directory")
        sys.exit(1)
    
    # Ask for PDF file path or URL
    print("\nChoose an option:")
    print("1. Process a local PDF file")
    print("2. Process a PDF from a URL")
    choice = input("Enter your choice (1 or 2): ")
    
    # Build the command
    cmd = ["python", "mistral_ocr.py"]
    
    if choice == "1":
        file_path = input("Enter the path to your PDF file: ")
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)
        cmd.extend(["--file", file_path])
    elif choice == "2":
        url = input("Enter the URL of the PDF file: ")
        cmd.extend(["--url", url])
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    # API key is expected to be in the .env file as MISTRAL_API_KEY
    
    # Ask for output file name (optional)
    custom_output = input("Do you want to specify a custom output file name? (y/n): ").lower()
    if custom_output == "y":
        output_file = input("Enter the output file name (e.g., result.html): ")
        cmd.extend(["--output", output_file])
    
    # Ask for max images (optional)
    limit_images = input("Do you want to limit the number of images processed? (y/n): ").lower()
    if limit_images == "y":
        try:
            max_images = int(input("Enter the maximum number of images to process: "))
            cmd.extend(["--max-images", str(max_images)])
        except ValueError:
            print("❌ Invalid number, not limiting images")
    
    # Ask to open in browser
    open_browser = input("Open the result in browser after processing? (y/n): ").lower()
    if open_browser == "y":
        cmd.append("--open-browser")
    
    # Print the command
    print("\nRunning command:")
    print(" ".join(cmd))
    print("\n")
    
    # Run the command
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ Error running command: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_example()
