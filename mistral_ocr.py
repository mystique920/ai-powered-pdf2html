#!/usr/bin/env python3
"""
Mistral OCR Processor - Local Version

This script processes PDF documents using Mistral OCR and generates accessible HTML output.
It can accept local file paths or URLs to PDF documents.

Usage:
    python mistral_ocr.py --file path/to/local/file.pdf
    python mistral_ocr.py --url https://example.com/document.pdf
    python mistral_ocr.py --api-key YOUR_API_KEY --file path/to/local/file.pdf
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import traceback
from typing import Dict, List, Optional, Union

# Third-party imports
import requests
from mistralai import Mistral
from mistralai import DocumentURLChunk, TextChunk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process PDF documents with Mistral OCR")
    
    # Input options - either file or URL is required
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", "-f", help="Path to local PDF file")
    input_group.add_argument("--url", "-u", help="URL to PDF file")
    
    # API key option
    parser.add_argument("--api-key", "-k", help="Mistral API key (overrides default)")
    
    # Output options
    parser.add_argument("--output", "-o", help="Output HTML file path (default: output.html)", 
                        default="output.html")
    parser.add_argument("--max-images", "-m", type=int, default=None,
                        help="Maximum number of images to process (default: all)")
    parser.add_argument("--open-browser", "-b", action="store_true",
                        help="Open the output HTML in browser after processing")
    
    return parser.parse_args()

def load_pdf_from_file(file_path: str) -> bytes:
    """Load PDF content from a local file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.lower().endswith('.pdf'):
        print(f"Warning: File {file_path} does not have a .pdf extension")
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        file_size_mb = len(content) / (1024 * 1024)
        print(f"✅ Loaded: {file_path} ({file_size_mb:.2f} MB)")
        return content
    except Exception as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")

def load_pdf_from_url(url: str) -> bytes:
    """Download PDF content from a URL."""
    try:
        print(f"Downloading PDF from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Check if content type is PDF
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
            print(f"Warning: URL content may not be a PDF (Content-Type: {content_type})")
        
        content = response.content
        file_size_mb = len(content) / (1024 * 1024)
        print(f"✅ Downloaded: {url} ({file_size_mb:.2f} MB)")
        return content
    except Exception as e:
        raise IOError(f"Error downloading PDF from {url}: {str(e)}")

def process_pdf_with_ocr(client: Mistral, file_content: bytes, filename: str = "document.pdf") -> Dict:
    """Process PDF content with Mistral OCR."""
    try:
        print("\nStep 1/3: Uploading to Mistral...")
        # Upload to Mistral
        uploaded_file = client.files.upload(
            file={
                "file_name": filename,
                "content": file_content,
            },
            purpose="ocr"
        )
        print(f"✅ File uploaded to Mistral with ID: {uploaded_file.id}")

        print("\nStep 2/3: Getting signed URL...")
        # Get the signed URL
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        print(f"✅ Signed URL obtained")

        print("\nStep 3/3: Processing with OCR...")
        print("This may take a while for large files. Please be patient.")
        start_time = time.time()

        # Process with OCR
        ocr_result = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest",
            include_image_base64=True
        )

        # Calculate processing time
        processing_time = time.time() - start_time
        print(f"✅ OCR processing complete in {processing_time:.2f} seconds!")

        # Display basic info about the results
        image_count = sum(len(page.images) for page in ocr_result.pages)
        print(f"- Total pages: {len(ocr_result.pages)}")
        print(f"- Total images extracted: {image_count}")

        # Print a sample of the first page text (truncated)
        if ocr_result.pages:
            first_page_text = ocr_result.pages[0].markdown[:200]
            print(f"\nSample text from first page:\n{first_page_text}...")
            
        return ocr_result
    except Exception as e:
        print(f"\n❌ Error during OCR processing: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

def generate_alt_text_for_image(client: Mistral, img_base64: str, context: str = "") -> str:
    """Generate WCAG-compliant alt text for an image using Pixtral 12B."""
    try:
        # Use Pixtral 12B model to interpret the image
        prompt = """
        Create a detailed, accessible alt text description for this image following WCAG 2.1 guidelines.

        Consider these requirements:
        1. Be concise but thorough (30-150 words)
        2. Describe the main visual content objectively
        3. Include any text visible in the image
        4. If it's a chart or graph, describe the type, axes, trends, and key insights
        5. Mention colors only when relevant to understanding the content
        6. Do not use phrases like "image of" or "picture of"
        7. Focus on what's important for understanding the document's content

        Context about where this image appears in the document:
        {context}

        Return only the alt text, no other commentary or notes.
        """.format(context=context)

        chat_response = client.chat.complete(
            model="pixtral-12b-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_base64}}
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=300
        )

        # Return the generated alt text
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating alt text: {str(e)}")
        return "Image from document"

def process_tables_for_accessibility(markdown_content: str) -> str:
    """Enhance tables with proper accessibility features."""
    # Identify potential table sections in the markdown
    table_sections = re.findall(r'(\|.+\|\n)+', markdown_content)

    if not table_sections:
        return markdown_content

    enhanced_markdown = markdown_content

    for table_idx, section in enumerate(table_sections):
        # Analyze table structure
        rows = section.strip().split('\n')
        if len(rows) < 2:  # Not a proper table
            continue

        # Identify header row
        has_header = any('---' in row for row in rows)
        header_row_idx = 0  # Default to first row as header

        # Add a table caption before the table
        table_id = f"table-{table_idx+1}"
        table_caption = f"\n\n**Table {table_idx+1}**\n\n"

        # Replace the original table section with enhanced version
        enhanced_markdown = enhanced_markdown.replace(section, table_caption + section)

    return enhanced_markdown

def convert_ocr_to_accessible_html(client: Mistral, ocr_response, max_images: Optional[int] = None) -> str:
    """Convert OCR results to WCAG-compliant accessible HTML."""
    if ocr_response is None:
        return "<p>No OCR results available.</p>"

    # Identify document language (defaulting to English)
    document_language = "en"

    # Start with an HTML5 document with ARIA roles and accessibility features
    html_parts = []
    html_parts.append(f"""
    <!DOCTYPE html>
    <html lang="{document_language}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Accessible Document</title>
        <style>
            /* Base styles with accessibility considerations */
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
                background-color: #fff;
            }}

            /* Ensure sufficient color contrast (WCAG AA 4.5:1) */
            h1, h2, h3, h4, h5, h6 {{
                color: #222;
                margin-top: 1.5em;
                line-height: 1.2;
            }}

            /* Image handling for WCAG */
            img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 1em 0;
            }}

            /* Accessible table styles */
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1.5em 0;
                border: 1px solid #ddd;
            }}
            caption {{
                font-weight: bold;
                text-align: left;
                margin-bottom: 0.5em;
                font-size: 1.1em;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            /* Zebra striping for better readability */
            tr:nth-child(even) {{
                background-color: #f8f8f8;
            }}

            /* Ensure page breaks are accessible */
            .page-break {{
                height: 40px;
                margin: 40px 0;
                border-bottom: 1px dashed #ccc;
                text-align: center;
                position: relative;
            }}
            .page-break::after {{
                content: "Page Break";
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 0 10px;
                color: #666;
                font-size: 0.8em;
            }}

            /* Document structure */
            .pdf-page {{
                margin-bottom: 2em;
                border: 1px solid #eee;
                padding: 2em;
                border-radius: 5px;
            }}

            /* Focus indicators for keyboard navigation */
            a:focus, button:focus, input:focus {{
                outline: 3px solid #4a90e2;
                outline-offset: 2px;
            }}

            /* Skip link for keyboard users */
            .skip-link {{
                position: absolute;
                top: -40px;
                left: 0;
                background: #4a90e2;
                color: white;
                padding: 8px 16px;
                z-index: 100;
                transition: top 0.3s;
            }}
            .skip-link:focus {{
                top: 0;
            }}

            /* Print-specific styles */
            @media print {{
                body {{
                    width: 100%;
                    max-width: none;
                    margin: 0;
                    padding: 0;
                }}
                .pdf-page {{
                    border: none;
                    padding: 0;
                    margin: 0 0 2em 0;
                }}
                .page-break {{
                    page-break-after: always;
                    border: none;
                    height: 0;
                }}
                .page-break::after {{
                    display: none;
                }}
                .skip-link {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <a href="#main-content" class="skip-link">Skip to main content</a>
        <main id="main-content">
    """)

    # Add document title if first page starts with heading
    if ocr_response.pages and ocr_response.pages[0].markdown:
        first_line = ocr_response.pages[0].markdown.strip().split('\n')[0]
        if first_line.startswith('# '):
            document_title = first_line.replace('# ', '').strip()
            html_parts.append(f"<h1 id='document-title'>{document_title}</h1>")

    # Process each page
    for i, page in enumerate(ocr_response.pages):
        page_number = i + 1

        # Process all images to get alt text
        print(f"Processing page {page_number}/{len(ocr_response.pages)}...")

        # Create a dict of images by ID for quick lookup
        image_data = {}
        image_alt_texts = {}

        # Process images for this page
        images_processed = 0
        for img in page.images:
            # Check if we've reached the maximum number of images to process
            if max_images is not None and images_processed >= max_images:
                print(f"Reached maximum number of images to process ({max_images})")
                break
                
            images_processed += 1
            image_data[img.id] = img.image_base64

            # Generate alt text for each image using surrounding text for context
            # Extract text before and after the image reference to provide context
            image_reference = f"![{img.id}]({img.id})"
            img_pos = page.markdown.find(image_reference)

            if img_pos > -1:
                # Get text before and after the image (up to 250 chars each)
                before_text = page.markdown[max(0, img_pos-250):img_pos]
                after_text = page.markdown[img_pos+len(image_reference):min(len(page.markdown), img_pos+len(image_reference)+250)]
                context = before_text + "\n" + after_text
            else:
                context = ""

            print(f"  Generating alt text for image {img.id}...")
            start_time = time.time()
            alt_text = generate_alt_text_for_image(client, img.image_base64, context=context)
            print(f"  ✓ Alt text generated in {time.time() - start_time:.2f} seconds")
            image_alt_texts[img.id] = alt_text

        # Add page heading with proper ARIA role
        html_parts.append(f"<section class='pdf-page' id='page-{page.index}' aria-label='Page {page_number}'>")

        # Process tables for accessibility
        enhanced_md = process_tables_for_accessibility(page.markdown)

        # Replace image markers with accessible HTML img tags
        for img_id, base64_str in image_data.items():
            # Get the generated alt text or use a default
            alt_text = image_alt_texts.get(img_id, f"Image {img_id} from document")

            # Extract image dimensions if available
            img_obj = next((img for img in page.images if img.id == img_id), None)
            width = img_obj.bottom_right_x - img_obj.top_left_x
            height = img_obj.bottom_right_y - img_obj.top_left_y

            # Create figure with caption for complex images
            enhanced_md = enhanced_md.replace(
                f"![{img_id}]({img_id})",
                f"<figure id='figure-{img_id}'>"
                f"<img src='{base64_str}' alt='{alt_text}' id='{img_id}'"
                f" width='{width}' height='{height}' />"
                f"<figcaption>Figure: {alt_text[:60]}...</figcaption>"
                f"</figure>"
            )

        # Convert markdown to semantic HTML5
        html_content = convert_markdown_to_semantic_html(enhanced_md)
        html_parts.append(html_content)

        # Close page section and add page break if not the last page
        html_parts.append("</section>")
        if i < len(ocr_response.pages) - 1:
            html_parts.append(f"<div class='page-break' role='separator' aria-label='Page break between pages {page_number} and {page_number+1}'></div>")

    # Close main content and document
    html_parts.append("</main>")

    # Add footer with document metadata
    html_parts.append("""
    <footer role="contentinfo">
        <p>Document processed with Mistral OCR and converted to accessible HTML.</p>
    </footer>
    </body>
    </html>""")

    return '\n'.join(html_parts)

def convert_markdown_to_semantic_html(markdown_content: str) -> str:
    """Convert markdown to semantic HTML5 with accessibility features."""
    # Headers with proper hierarchy and IDs
    markdown_content = re.sub(r'^# (.+)$', lambda m: f"<h1 id='{slugify(m.group(1))}'>{m.group(1)}</h1>", markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^## (.+)$', lambda m: f"<h2 id='{slugify(m.group(1))}'>{m.group(1)}</h2>", markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^### (.+)$', lambda m: f"<h3 id='{slugify(m.group(1))}'>{m.group(1)}</h3>", markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^#### (.+)$', lambda m: f"<h4 id='{slugify(m.group(1))}'>{m.group(1)}</h4>", markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^##### (.+)$', lambda m: f"<h5 id='{slugify(m.group(1))}'>{m.group(1)}</h5>", markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^###### (.+)$', lambda m: f"<h6 id='{slugify(m.group(1))}'>{m.group(1)}</h6>", markdown_content, flags=re.MULTILINE)

    # Lists with proper semantics
    # Find ordered lists and convert to semantic HTML
    ordered_list_pattern = r'(^\d+\. .+$(\n^\d+\. .+$)*)'
    ordered_lists = re.findall(ordered_list_pattern, markdown_content, re.MULTILINE)
    for ol_match in ordered_lists:
        ol_content = ol_match[0]
        items = re.findall(r'^\d+\. (.+)$', ol_content, re.MULTILINE)

        # Build semantic ordered list
        new_list = "<ol>\n"
        for item in items:
            new_list += f"  <li>{item}</li>\n"
        new_list += "</ol>"

        # Replace in original markdown
        markdown_content = markdown_content.replace(ol_content, new_list)

    # Find unordered lists and convert to semantic HTML
    unordered_list_pattern = r'(^- .+$(\n^- .+$)*)'
    unordered_lists = re.findall(unordered_list_pattern, markdown_content, re.MULTILINE)
    for ul_match in unordered_lists:
        ul_content = ul_match[0]
        items = re.findall(r'^- (.+)$', ul_content, re.MULTILINE)

        # Build semantic unordered list
        new_list = "<ul>\n"
        for item in items:
            new_list += f"  <li>{item}</li>\n"
        new_list += "</ul>"

        # Replace in original markdown
        markdown_content = markdown_content.replace(ul_content, new_list)

    # Tables with proper semantics and ARIA
    table_sections = re.findall(r'\*\*Table (\d+)\*\*\n\n(\|.+\|\n)+', markdown_content)
    for table_match in table_sections:
        table_num = table_match[0]
        table_content = table_match[1]

        # Find the complete table section
        complete_table_section = f"**Table {table_num}**\n\n{table_content}"
        table_section = re.search(re.escape(complete_table_section), markdown_content)
        if not table_section:
            continue

        table_section = table_section.group(0)
        rows = re.findall(r'\|(.+)\|', table_section)

        if len(rows) < 2:  # Need at least header and one data row
            continue

        # Skip separator row if present
        separator_index = -1
        for i, row in enumerate(rows):
            if re.match(r'^[\s\-:|]+$', row):  # Row contains only separators
                separator_index = i
                break

        # Build accessible table
        table_id = f"table-{table_num}"
        semantic_table = f"<div class='table-container' role='region' aria-labelledby='{table_id}-caption' tabindex='0'>\n"
        semantic_table += f"<table id='{table_id}'>\n"
        semantic_table += f"<caption id='{table_id}-caption'>Table {table_num}</caption>\n"

        # Header row processing
        header_row = rows[0]
        headers = [cell.strip() for cell in header_row.split('|')]
        header_ids = [f"{table_id}-col-{i+1}" for i in range(len(headers))]

        semantic_table += "<thead>\n<tr>\n"
        for i, header in enumerate(headers):
            semantic_table += f"<th id='{header_ids[i]}' scope='col'>{header}</th>\n"
        semantic_table += "</tr>\n</thead>\n"

        # Data rows
        semantic_table += "<tbody>\n"
        data_rows = [r for i, r in enumerate(rows) if i != 0 and i != separator_index]

        for row_idx, row in enumerate(data_rows):
            cells = [cell.strip() for cell in row.split('|')]
            semantic_table += "<tr>\n"

            # First cell might be a row header
            first_cell = cells[0] if cells else ""
            if first_cell and all(c == first_cell for c in cells):
                semantic_table += f"<th scope='colgroup' colspan='{len(cells)}'>{first_cell}</th>\n"
            else:
                for col_idx, cell in enumerate(cells):
                    if col_idx == 0 and is_likely_header(cell, cells):
                        # This is likely a row header
                        semantic_table += f"<th scope='row'>{cell}</th>\n"
                    else:
                        # Regular cell - reference its header for accessibility
                        header_id = header_ids[col_idx] if col_idx < len(header_ids) else ""
                        headers_attr = f" headers='{header_id}'" if header_id else ""
                        semantic_table += f"<td{headers_attr}>{cell}</td>\n"

            semantic_table += "</tr>\n"

        semantic_table += "</tbody>\n</table>\n</div>"

        # Replace in original markdown
        markdown_content = markdown_content.replace(table_section, semantic_table)

    # Bold and italic
    markdown_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', markdown_content)
    markdown_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', markdown_content)

    # Links with aria-label for better screen reader experience
    markdown_content = re.sub(
        r'\[(.+?)\]\((.+?)\)',
        lambda m: f"<a href=\"{m.group(2)}\" aria-label=\"{m.group(1)}\">{m.group(1)}</a>",
        markdown_content
    )

    # Convert remaining paragraphs with proper HTML5 structure
    paragraphs = re.split(r'\n{2,}', markdown_content)
    html_parts = []

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        # Skip if already HTML
        if p.startswith('<') and p.endswith('>'):
            html_parts.append(p)
        else:
            # Replace single line breaks with <br>
            p = p.replace('\n', '<br>')
            # Wrap in paragraph tags
            html_parts.append(f"<p>{p}</p>")

    return '\n'.join(html_parts)

def slugify(text: str) -> str:
    """Convert text to a URL-friendly format for IDs."""
    # Replace non-alphanumeric with hyphens
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Replace spaces with hyphens
    return re.sub(r'\s+', '-', text)

def is_likely_header(cell: str, row_cells: List[str]) -> bool:
    """Determine if a cell is likely a row header."""
    # Check if first cell is formatted differently (e.g., all caps, shorter)
    if cell.isupper() and not all(c.isupper() for c in row_cells[1:]):
        return True
    # Check if first cell is shorter than average of other cells
    if len(row_cells) > 1:
        avg_len = sum(len(c) for c in row_cells[1:]) / (len(row_cells) - 1)
        if len(cell) < avg_len * 0.5:  # Significantly shorter
            return True
    return False

def save_html_to_file(html_content: str, output_path: str) -> None:
    """Save HTML content to a file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML saved to {output_path}")
    except Exception as e:
        print(f"❌ Error saving HTML to {output_path}: {str(e)}")

def open_in_browser(file_path: str) -> None:
    """Open the HTML file in the default browser."""
    import webbrowser
    try:
        print(f"Opening {file_path} in browser...")
        webbrowser.open(f"file://{os.path.abspath(file_path)}")
    except Exception as e:
        print(f"❌ Error opening browser: {str(e)}")

def main():
    """Main function to process PDF documents."""
    args = parse_arguments()
    
    # Get API key from arguments or environment variable
    api_key = args.api_key or MISTRAL_API_KEY
    
    if not api_key:
        print("❌ Error: No Mistral API key provided")
        print("Please set the MISTRAL_API_KEY environment variable in a .env file")
        print("or provide it using the --api-key argument")
        sys.exit(1)
    
    # Initialize Mistral client
    try:
        client = Mistral(api_key=api_key)
        print("✅ Mistral client initialized")
    except Exception as e:
        print(f"❌ Error initializing Mistral client: {str(e)}")
        sys.exit(1)
    
    # Load PDF content
    try:
        if args.file:
            file_content = load_pdf_from_file(args.file)
            filename = os.path.basename(args.file)
        else:  # args.url
            file_content = load_pdf_from_url(args.url)
            filename = os.path.basename(args.url) if args.url.lower().endswith('.pdf') else "document.pdf"
    except Exception as e:
        print(f"❌ Error loading PDF: {str(e)}")
        sys.exit(1)
    
    # Process with OCR
    ocr_result = process_pdf_with_ocr(client, file_content, filename)
    
    # Convert to accessible HTML
    print("\nGenerating accessible HTML...")
    html_content = convert_ocr_to_accessible_html(client, ocr_result, args.max_images)
    
    # Save HTML to file
    save_html_to_file(html_content, args.output)
    
    # Open in browser if requested
    if args.open_browser:
        open_in_browser(args.output)
    
    print("\n✅ Processing complete!")

if __name__ == "__main__":
    main()
