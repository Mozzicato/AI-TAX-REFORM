"""
Script to extract text from PDF files
Used for preprocessing tax documents before entity extraction
"""

import pdfplumber
import json
from pathlib import Path
import sys

def extract_text_from_pdf(pdf_path, output_path=None):
    """
    Extract text from a PDF file and save to JSON
    
    Args:
        pdf_path (str): Path to PDF file
        output_path (str): Path to save extracted text (optional)
    
    Returns:
        dict: Extracted text with metadata
    """
    extracted_data = {
        "file": str(pdf_path),
        "pages": []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Processing: {pdf_path}")
            print(f"📊 Total pages: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text()
                
                # Extract tables if any
                tables = page.extract_tables()
                
                # Build page data
                page_data = {
                    "page_number": page_num,
                    "text": text,
                    "tables": tables if tables else [],
                    "height": page.height,
                    "width": page.width
                }
                
                extracted_data["pages"].append(page_data)
                
                if page_num % 10 == 0:
                    print(f"✓ Processed page {page_num}")
        
        # Save to JSON if output path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Saved to: {output_file}")
        
        print(f"✅ Successfully extracted text from {len(extracted_data['pages'])} pages\n")
        return extracted_data
    
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {str(e)}")
        return None

def batch_extract_pdfs(pdf_directory, output_directory):
    """
    Extract text from all PDFs in a directory
    
    Args:
        pdf_directory (str): Directory containing PDF files
        output_directory (str): Directory to save extracted files
    """
    pdf_dir = Path(pdf_directory)
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_directory}")
        return
    
    print(f"🔍 Found {len(pdf_files)} PDF files\n")
    
    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}_extracted.json"
        extract_text_from_pdf(str(pdf_file), str(output_file))

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else "extracted.json"
        extract_text_from_pdf(pdf_path, output_path)
    else:
        print("Usage: python extract_pdf.py <pdf_file> [output_file]")
        print("Or: python extract_pdf.py --batch <pdf_directory> <output_directory>")
