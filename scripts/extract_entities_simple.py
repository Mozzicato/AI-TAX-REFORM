"""
Simple Entity Extraction for Tax Documents
Pattern-based extraction without API calls
Used for initial data population and testing
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Tax-related keywords and patterns
TAX_KEYWORDS = {
    "VAT": ["Value Added Tax", "VAT", "value added"],
    "PAYE": ["Pay As You Earn", "PAYE", "payroll tax"],
    "DST": ["Digital Service Tax", "DST", "digital services"],
    "CIT": ["Corporate Income Tax", "CIT", "company income"],
    "PIT": ["Personal Income Tax", "PIT", "personal income"],
    "CGT": ["Capital Gains Tax", "CGT", "capital gains"],
    "Stamp Duty": ["stamp duty", "stamp tax"],
    "Withholding Tax": ["withholding tax", "WHT"],
}

TAXPAYER_TYPES = {
    "Individual": ["individual", "person", "natural person", "resident"],
    "SME": ["SME", "small and medium", "small business", "micro business"],
    "Corporation": ["corporation", "company", "enterprise", "business"],
    "Partnership": ["partnership", "joint venture", "cooperative"],
    "Non-profit": ["non-profit", "charity", "foundation", "NGO"],
    "Digital Service Provider": ["digital service", "online service", "e-commerce"],
}

AGENCY_KEYWORDS = {
    "FIRS": ["Federal Inland Revenue Service", "FIRS", "federal revenue"],
    "JTB": ["Joint Tax Board", "JTB", "joint board"],
    "State IRS": ["state internal revenue", "state IRS", "state revenue"],
    "LIRS": ["Lagos Internal Revenue Service", "LIRS"],
}

PROCESS_KEYWORDS = {
    "Registration": ["register", "registration", "enroll", "enrollment"],
    "Filing": ["file", "filing", "submit", "submission"],
    "Payment": ["pay", "payment", "remit", "remittance"],
    "Compliance": ["comply", "compliance", "adherence"],
    "Audit": ["audit", "auditing", "examination", "review"],
    "Appeal": ["appeal", "dispute", "objection"],
}

PENALTY_KEYWORDS = {
    "Late Payment Charge": ["late payment", "penalty", "charge", "interest"],
    "Fraud Penalty": ["fraud", "evasion", "false", "fraudulent"],
    "Non-compliance Fine": ["non-compliance", "fine", "violation"],
    "Interest": ["interest", "accumulated interest"],
}

DEADLINE_PATTERNS = [
    r"(?:by|before|on or before|within)\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)",
    r"(?:within|within\s+)(\d+)\s+(?:days|weeks|months)",
    r"\b(?:30|60|90)\s+days?\b",
]


def extract_text_chunks(json_file: str, chunk_size: int = 500) -> List[Dict]:
    """
    Extract and chunk text from JSON
    
    Args:
        json_file: Path to extracted PDF JSON
        chunk_size: Characters per chunk
        
    Returns:
        List of text chunks with metadata
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chunks = []
    chunk_id = 0
    
    for page_data in data['pages']:
        text = page_data.get('text', '')
        page_num = page_data.get('page_number', 1)
        
        # Split into chunks
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size > chunk_size:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'chunk_id': chunk_id,
                    'page': page_num,
                    'text': chunk_text,
                    'length': len(chunk_text)
                })
                chunk_id += 1
                current_chunk = []
                current_size = 0
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'chunk_id': chunk_id,
                'page': page_num,
                'text': chunk_text,
                'length': len(chunk_text)
            })
            chunk_id += 1
    
    return chunks


def extract_entities_from_chunks(chunks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract entities and relationships from text chunks
    
    Args:
        chunks: List of text chunks
        
    Returns:
        Tuple of (entities, relationships)
    """
    entities = []
    relationships = []
    entity_map = defaultdict(list)  # For relationship tracking
    
    entity_id = 0
    
    for chunk in chunks:
        text = chunk['text'].lower()
        page = chunk['page']
        
        # Extract Tax entities
        for tax_name, keywords in TAX_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    entity = {
                        'id': f'tax_{entity_id}',
                        'type': 'Tax',
                        'name': tax_name,
                        'description': f'Tax type mentioned on page {page}',
                        'page': page,
                        'chunk_id': chunk['chunk_id']
                    }
                    entities.append(entity)
                    entity_map[f'tax_{entity_id}'].append('Tax')
                    entity_id += 1
                    break
        
        # Extract Taxpayer entities
        for taxpayer_type, keywords in TAXPAYER_TYPES.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    entity = {
                        'id': f'taxpayer_{entity_id}',
                        'type': 'Taxpayer',
                        'name': taxpayer_type,
                        'description': f'Taxpayer type: {taxpayer_type}',
                        'page': page,
                        'chunk_id': chunk['chunk_id']
                    }
                    entities.append(entity)
                    entity_map[f'taxpayer_{entity_id}'].append('Taxpayer')
                    entity_id += 1
                    break
        
        # Extract Agency entities
        for agency_name, keywords in AGENCY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    entity = {
                        'id': f'agency_{entity_id}',
                        'type': 'Agency',
                        'name': agency_name,
                        'description': f'Tax agency: {agency_name}',
                        'page': page,
                        'chunk_id': chunk['chunk_id']
                    }
                    entities.append(entity)
                    entity_map[f'agency_{entity_id}'].append('Agency')
                    entity_id += 1
                    break
        
        # Extract Process entities
        for process_name, keywords in PROCESS_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    entity = {
                        'id': f'process_{entity_id}',
                        'type': 'Process',
                        'name': process_name,
                        'description': f'Tax process: {process_name}',
                        'page': page,
                        'chunk_id': chunk['chunk_id']
                    }
                    entities.append(entity)
                    entity_map[f'process_{entity_id}'].append('Process')
                    entity_id += 1
                    break
        
        # Extract Penalty entities
        for penalty_name, keywords in PENALTY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    entity = {
                        'id': f'penalty_{entity_id}',
                        'type': 'Penalty',
                        'name': penalty_name,
                        'description': f'Penalty: {penalty_name}',
                        'page': page,
                        'chunk_id': chunk['chunk_id']
                    }
                    entities.append(entity)
                    entity_map[f'penalty_{entity_id}'].append('Penalty')
                    entity_id += 1
                    break
        
        # Extract Deadlines
        for pattern in DEADLINE_PATTERNS:
            matches = re.finditer(pattern, chunk['text'], re.IGNORECASE)
            for match in matches:
                entity = {
                    'id': f'deadline_{entity_id}',
                    'type': 'Deadline',
                    'name': match.group(0),
                    'description': f'Deadline: {match.group(0)}',
                    'page': page,
                    'chunk_id': chunk['chunk_id']
                }
                entities.append(entity)
                entity_map[f'deadline_{entity_id}'].append('Deadline')
                entity_id += 1
    
    # Create relationships (Tax applies to Taxpayer, enforced by Agency, etc.)
    rel_id = 0
    tax_entities = [e for e in entities if e['type'] == 'Tax']
    taxpayer_entities = [e for e in entities if e['type'] == 'Taxpayer']
    agency_entities = [e for e in entities if e['type'] == 'Agency']
    
    # Tax applies to Taxpayers
    for tax in tax_entities:
        for taxpayer in taxpayer_entities:
            relationships.append({
                'id': f'rel_{rel_id}',
                'source_id': tax['id'],
                'source_type': 'Tax',
                'target_id': taxpayer['id'],
                'target_type': 'Taxpayer',
                'relationship': 'applies_to',
                'description': f"{tax['name']} applies to {taxpayer['name']}"
            })
            rel_id += 1
    
    # Tax enforced by Agency
    for tax in tax_entities:
        for agency in agency_entities:
            relationships.append({
                'id': f'rel_{rel_id}',
                'source_id': tax['id'],
                'source_type': 'Tax',
                'target_id': agency['id'],
                'target_type': 'Agency',
                'relationship': 'enforced_by',
                'description': f"{tax['name']} is enforced by {agency['name']}"
            })
            rel_id += 1
    
    # Process related to Tax
    process_entities = [e for e in entities if e['type'] == 'Process']
    for process in process_entities:
        for tax in tax_entities[:min(2, len(tax_entities))]:  # Limit relationships
            relationships.append({
                'id': f'rel_{rel_id}',
                'source_id': process['id'],
                'source_type': 'Process',
                'target_id': tax['id'],
                'target_type': 'Tax',
                'relationship': 'related_to',
                'description': f"{process['name']} related to {tax['name']}"
            })
            rel_id += 1
    
    return entities, relationships


def main():
    # Paths
    json_file = 'data/chunked/Nigeria-Tax-Act-2025.json'
    entities_output = 'data/extracted/entities.json'
    relationships_output = 'data/extracted/relationships.json'
    chunks_output = 'data/extracted/chunks.json'
    
    # Create output directory
    Path('data/extracted').mkdir(parents=True, exist_ok=True)
    
    print("📖 Extracting text chunks...")
    chunks = extract_text_chunks(json_file, chunk_size=500)
    print(f"✅ Created {len(chunks)} text chunks")
    
    # Save chunks
    with open(chunks_output, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved chunks to {chunks_output}")
    
    print("\n🔍 Extracting entities...")
    entities, relationships = extract_entities_from_chunks(chunks)
    
    # Remove duplicates
    unique_entities = {(e['type'], e['name']): e for e in entities}.values()
    entities = list(unique_entities)
    
    print(f"✅ Extracted {len(entities)} unique entities:")
    for entity_type in set(e['type'] for e in entities):
        count = len([e for e in entities if e['type'] == entity_type])
        print(f"   • {entity_type}: {count}")
    
    print(f"\n✅ Extracted {len(relationships)} relationships")
    
    # Save entities
    with open(entities_output, 'w', encoding='utf-8') as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved entities to {entities_output}")
    
    # Save relationships
    with open(relationships_output, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved relationships to {relationships_output}")
    
    print("\n📊 Summary:")
    print(f"   Total Chunks: {len(chunks)}")
    print(f"   Total Entities: {len(entities)}")
    print(f"   Total Relationships: {len(relationships)}")


if __name__ == "__main__":
    main()
