"""
Document preprocessing script
Cleans and chunks extracted text for entity extraction
"""

import json
import re
from pathlib import Path
from typing import List, Dict

def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep dots, commas, etc.
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()

def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks with overlap
    
    Args:
        text (str): Text to split
        chunk_size (int): Target chunk size in words
        overlap (int): Overlap size in words
    
    Returns:
        List[str]: List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks

def preprocess_document(json_file: str, output_file: str = None) -> Dict:
    """
    Preprocess extracted PDF document
    
    Args:
        json_file (str): Path to extracted JSON file
        output_file (str): Path to save processed file
    
    Returns:
        Dict: Processed document data
    """
    print(f"📋 Processing: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    processed_data = {
        "source_file": extracted_data["file"],
        "total_pages": len(extracted_data["pages"]),
        "chunks": []
    }
    
    for page_data in extracted_data["pages"]:
        page_num = page_data["page_number"]
        text = page_data["text"]
        
        # Clean text
        cleaned_text = clean_text(text)
        
        if not cleaned_text:
            continue
        
        # Split into chunks
        chunks = split_into_chunks(cleaned_text, chunk_size=500, overlap=50)
        
        for chunk_idx, chunk in enumerate(chunks):
            chunk_obj = {
                "page": page_num,
                "chunk_index": chunk_idx,
                "text": chunk,
                "tokens_estimate": len(chunk.split())
            }
            processed_data["chunks"].append(chunk_obj)
    
    print(f"✅ Created {len(processed_data['chunks'])} chunks")
    
    # Save if output file specified
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to: {output_path}")
    
    return processed_data

if __name__ == "__main__":
    # Example: python preprocess_document.py extracted.json processed.json
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        preprocess_document(json_file, output_file)
    else:
        print("Usage: python preprocess_document.py <json_file> [output_file]")
