#!/usr/bin/env python3
"""
Test script to process a PDF from a URL with Mistral OCR.
This script demonstrates how to use the mistral_ocr.py script with a PDF URL.
"""

import subprocess
import sys

def main():
    """Process a PDF from a URL with Mistral OCR."""
    # Define the PDF URL to process
    # This is a sample PDF URL - replace with a valid PDF URL if needed
    pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    
    # Define the output file
    output_file = "url_output.html"
    
    # Build the command
    cmd = [
        "python", "mistral_ocr.py",
        "--url", pdf_url,
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
