# Mistral OCR Processor

A command-line tool for processing PDF documents with Mistral OCR and generating accessible HTML output. This tool is adapted from a Google Colab notebook to run locally on your machine.

## Quick Start

Several scripts are provided to help you get started:

- `mistral_ocr.py` - The main script for processing PDFs
- `example.py` - An interactive example that guides you through the options
- `test_local_pdf.py` - A test script for processing a local PDF file
- `test_url_pdf.py` - A test script for processing a PDF from a URL

To run the interactive example:
```
python example.py
```

To test with a local PDF:
```
python test_local_pdf.py
```

To test with a PDF from a URL:
```
python test_url_pdf.py
```

## Features

- Process local PDF files or download from URLs
- OCR processing with Mistral OCR
- Generate accessible alt text for images using Pixtral 12B
- Convert to WCAG-compliant accessible HTML
- Enhance tables with proper accessibility features
- Save output as HTML file
- Option to open result in browser

## Requirements

- Python 3.6+
- Mistral API key
- Required Python packages:
  - mistralai
  - requests

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/mystique920/ai-powered-pdf2html
   cd ai-powered-pdf2html
   ```
2. Ensure you have Python installed
3. Install required packages using pip:
   ```
   pip install -r requirements.txt
   ```
   
   Or install packages individually:
   ```
   pip install mistralai requests
   ```
4. Make the script executable (optional):
   ```
   chmod +x mistral_ocr.py
   ```

## Usage

### Basic Usage

Process a local PDF file:
```
python mistral_ocr.py --file path/to/your/document.pdf
```

Process a PDF from a URL:
```
python mistral_ocr.py --url https://example.com/document.pdf
```

### Command-line Options

- `--file`, `-f`: Path to local PDF file
- `--url`, `-u`: URL to PDF file
- `--api-key`, `-k`: Mistral API key
- `--output`, `-o`: Output HTML file path (default: output.html)
- `--max-images`, `-m`: Maximum number of images to process (default: all)
- `--open-browser`, `-b`: Open the output HTML in browser after processing

### Examples

Process a local file with a custom API key and open in browser:
```
python mistral_ocr.py --file document.pdf --api-key YOUR_API_KEY --open-browser
```

Process a PDF from URL and save to a custom output file:
```
python mistral_ocr.py --url https://example.com/document.pdf --output result.html
```

Process a file but limit image processing to 5 images:
```
python mistral_ocr.py --file document.pdf --max-images 5
```

## API Key Setup

The script requires a valid Mistral API key to function. There are two ways to provide the API key:

1. Create a `.env` file in the same directory as the script with the following content:
   ```
   MISTRAL_API_KEY=your_api_key_here
   ```

2. Provide the API key directly using the `--api-key` command-line argument:
   ```
   python mistral_ocr.py --file document.pdf --api-key your_api_key_here
   ```

## Notes

- Processing large PDFs may take some time
- Image alt text generation uses the Pixtral 12B model
- The HTML output is designed to be WCAG-compliant for accessibility
- You can limit the number of images processed to save API usage
- The code for this application is based on a public Google Colab notebook
- The original code is from this repository: https://github.com/coldplazma/Accessible-OCR-Mistral-
