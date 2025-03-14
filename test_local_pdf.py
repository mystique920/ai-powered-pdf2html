#!/usr/bin/env python3
"""
Test script to process a local PDF file with Mistral OCR.
This script demonstrates how to use the mistral_ocr.py script with a specific PDF file.
"""

import os
import subprocess
import sys

def main():
    """Process a local PDF file with Mistral OCR."""
    # Define the PDF file to process
    pdf_file = "ChapterMarijuanaEmpathyandSevereCasesofAutism.pdf"
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_file):
        print(f"❌ Error: PDF file not found: {pdf_file}")
        print("Please place the PDF file in the same directory as this script.")
        sys.exit(1)
    
    # Define the output file
    output_file = "output.html"
    
    # Build the command
    cmd = [
        "python", "mistral_ocr.py",
        "--file", pdf_file,
        "--output", output_file,
        "--max-images", "3",  # Limit to 3 images to save API usage
        "--open-browser"  # Open the result in browser
    ]
    
    # Print the command
    print("Running command:")
    print(" ".join(cmd))
    print()
    
    # Run the command
    try:
        subprocess.run(cmd)
        print(f"\n✅ Test completed. Output saved to {output_file}")
    except Exception as e:
        print(f"❌ Error running command: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
