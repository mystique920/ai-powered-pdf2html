# PDF2HTML AI

[![PyPI version](https://badge.fury.io/py/pdf2html-ai.svg)](https://badge.fury.io/py/pdf2html-ai)

A Python package for converting PDF documents to accessible HTML using Mistral OCR and Pixtral 12B. This tool processes PDFs and generates WCAG-compliant HTML output with enhanced accessibility features.

## Features

- Process local PDF files or download from URLs
- OCR processing with Mistral OCR
- Generate accessible alt text for images using Pixtral 12B
- Convert to WCAG-compliant accessible HTML
- Enhance tables with proper accessibility features
- Save output as HTML file
- Option to open result in browser

## Requirements

- Python 3.10+
- Mistral API key
- Required Python packages (automatically installed with pip):
  - mistralai
  - requests
  - python-dotenv
  - PyPDF2

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install pdf2html-ai
```

### Option 2: Install from Repository

1. Clone the repository:
   ```bash
   git clone https://github.com/mystique920/ai-powered-pdf2html
   cd ai-powered-pdf2html
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

After installing the package, you can use it in your Python code or via the command line.

### Using as a Python Package

```python
from pdf2html_ai import process_pdf_with_ocr, convert_ocr_to_accessible_html
from mistralai import Mistral

# Initialize Mistral client
client = Mistral(api_key="your_api_key_here")

# Process a local PDF file
with open("document.pdf", "rb") as f:
    file_content = f.read()
    
ocr_result = process_pdf_with_ocr(client, file_content, "document.pdf")
html_content = convert_ocr_to_accessible_html(client, ocr_result)

# Save the HTML output
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html_content)
```

### Using the Command Line

Process a local PDF file:
```bash
python -m pdf2html_ai.processor --file path/to/your/document.pdf
```

Process a PDF from a URL:
```bash
python -m pdf2html_ai.processor --url https://example.com/document.pdf
```

## Example Scripts

Several example scripts are provided to help you get started:

- `examples/example.py` - An interactive example that guides you through the options
- `tests/test_local_pdf.py` - A test script for processing a local PDF file
- `tests/test_url_pdf.py` - A test script for processing a PDF from a URL

To run the interactive example:
```bash
python examples/example.py
```

## Command-line Options

- `--file`, `-f`: Path to local PDF file
- `--url`, `-u`: URL to PDF file
- `--api-key`, `-k`: Mistral API key
- `--output`, `-o`: Output HTML file path (default: output.html)
- `--max-images`, `-m`: Maximum number of images to process (default: all)
- `--open-browser`, `-b`: Open the output HTML in browser after processing

### Examples

Process a local file with a custom API key and open in browser:
```bash
python -m pdf2html_ai.processor --file document.pdf --api-key YOUR_API_KEY --open-browser
```

Process a PDF from URL and save to a custom output file:
```bash
python -m pdf2html_ai.processor --url https://example.com/document.pdf --output result.html
```

Process a file but limit image processing to 5 images:
```bash
python -m pdf2html_ai.processor --file document.pdf --max-images 5
```

## API Key Setup

The script requires a valid Mistral API key to function. There are two ways to provide the API key:

1. Create a `.env` file in your project directory with the following content:
   ```
   MISTRAL_API_KEY=your_api_key_here
   ```

2. Provide the API key directly using the `--api-key` command-line argument:
   ```bash
   python -m pdf2html_ai.processor --file document.pdf --api-key your_api_key_here
   ```

## Notes

- Processing large PDFs may take some time
- Image alt text generation uses the Pixtral 12B model
- The HTML output is designed to be WCAG-compliant for accessibility
- You can limit the number of images processed to save API usage
- The code for this application is based on a public Google Colab notebook
- The original code is from this repository: https://github.com/coldplazma/Accessible-OCR-Mistral-
- This tool was mostly modified and extended using AI tools. Use this tool at your own risk
