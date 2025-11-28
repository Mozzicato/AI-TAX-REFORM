"""
Entity & Relationship Extraction Pipeline
Extracts tax entities and relationships from document chunks using GPT-4
"""

import json
import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import openai

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# ============================================================================
# EXTRACTION PROMPTS
# ============================================================================

ENTITY_EXTRACTION_PROMPT = """
You are an expert tax law analyst. Extract all tax entities from the following text.

Return ONLY valid JSON (no markdown, no explanations):
{
  "entities": [
    {
      "id": "entity_unique_id",
      "type": "Tax | Taxpayer | Agency | Process | Threshold | Penalty | Deadline | Rule | Document | Exception",
      "name": "entity name",
      "properties": {
        "key1": "value1",
        "key2": "value2"
      },
      "description": "brief description"
    }
  ]
}

Entity Types:
- Tax: VAT, PAYE, DST, CGT, Education Tax, etc. (properties: type, rate, effective_date, description)
- Taxpayer: Individual, Freelancer, SME, Digital Service Provider (properties: category, resident, threshold)
- Agency: FIRS, JTB, State IRS (properties: name, jurisdiction, contact)
- Process: VAT Registration, PAYE Filing, etc. (properties: name, duration, frequency, mandatory)
- Threshold: Income/turnover thresholds (properties: amount, currency, applies_to, logic)
- Penalty: Late filing, non-payment (properties: type, amount, percentage, calculation_basis)
- Deadline: Tax filing dates (properties: event, date, frequency, reminder_days)
- Rule: Tax rules and policies (properties: content, policy_ref, effective_date, status)
- Exception: Tax exemptions (properties: description, applies_to, conditions)

Text to analyze:
{text}
"""

RELATIONSHIP_EXTRACTION_PROMPT = """
You are an expert tax law analyst. Extract relationships between tax entities.

Given these entities: {entities}

Return ONLY valid JSON (no markdown, no explanations):
{
  "relationships": [
    {
      "source_id": "entity_id_1",
      "target_id": "entity_id_2",
      "relationship_type": "applies_to | enforced_by | requires | defined_in | liable_for | triggers | has_exception | penalizes",
      "properties": {
        "condition": "optional condition",
        "strength": "strong | moderate | weak"
      }
    }
  ]
}

Relationship Types:
- applies_to: Tax applies to taxpayer category
- enforced_by: Tax is enforced by an agency
- requires: Tax/Process requires a document/step
- liable_for: Taxpayer is liable for a tax
- triggers: Threshold triggers a tax
- has_exception: Tax has an exception
- penalizes: Rule incurs a penalty
- defined_in: Process defined in a document

Text to analyze:
{text}

Entities found: {entities_json}
"""

# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def extract_entities(text: str) -> Dict:
    """
    Extract entities from text using GPT-4
    
    Args:
        text: Document chunk to analyze
        
    Returns:
        Dictionary with extracted entities
    """
    try:
        prompt = ENTITY_EXTRACTION_PROMPT.format(text=text)
        
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a tax law expert. Extract entities and return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content
        
        # Parse JSON response
        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {result_text}")
            return {"entities": []}
            
    except Exception as e:
        print(f"Error extracting entities: {str(e)}")
        return {"entities": []}

def extract_relationships(text: str, entities: List[Dict]) -> Dict:
    """
    Extract relationships between entities using GPT-4
    
    Args:
        text: Document chunk context
        entities: List of extracted entities
        
    Returns:
        Dictionary with extracted relationships
    """
    try:
        entities_json = json.dumps(entities, indent=2)
        prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(
            entities=", ".join([e.get("name", e.get("id")) for e in entities]),
            text=text,
            entities_json=entities_json
        )
        
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a tax law expert. Extract relationships and return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        result_text = response.choices[0].message.content
        
        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError:
            print(f"Failed to parse relationships JSON: {result_text}")
            return {"relationships": []}
            
    except Exception as e:
        print(f"Error extracting relationships: {str(e)}")
        return {"relationships": []}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_entity(entity: Dict) -> Tuple[bool, str]:
    """Validate extracted entity"""
    
    if not entity.get("id"):
        return False, "Missing entity ID"
    
    if not entity.get("type"):
        return False, "Missing entity type"
    
    if not entity.get("name"):
        return False, "Missing entity name"
    
    valid_types = [
        "Tax", "Taxpayer", "Agency", "Process", "Threshold",
        "Penalty", "Deadline", "Rule", "Document", "Exception"
    ]
    
    if entity.get("type") not in valid_types:
        return False, f"Invalid entity type: {entity.get('type')}"
    
    return True, "Valid"

def validate_relationship(relationship: Dict, entity_ids: set) -> Tuple[bool, str]:
    """Validate extracted relationship"""
    
    if not relationship.get("source_id"):
        return False, "Missing source_id"
    
    if not relationship.get("target_id"):
        return False, "Missing target_id"
    
    if not relationship.get("relationship_type"):
        return False, "Missing relationship_type"
    
    valid_rel_types = [
        "applies_to", "enforced_by", "requires", "defined_in",
        "liable_for", "triggers", "has_exception", "penalizes"
    ]
    
    if relationship.get("relationship_type") not in valid_rel_types:
        return False, f"Invalid relationship type: {relationship.get('relationship_type')}"
    
    if relationship.get("source_id") not in entity_ids:
        return False, f"Source entity not found: {relationship.get('source_id')}"
    
    if relationship.get("target_id") not in entity_ids:
        return False, f"Target entity not found: {relationship.get('target_id')}"
    
    return True, "Valid"

# ============================================================================
# PROCESSING PIPELINE
# ============================================================================

def process_document_chunk(chunk: Dict) -> Dict:
    """
    Process a single document chunk
    
    Args:
        chunk: Document chunk with id, text, metadata
        
    Returns:
        Processing result with entities and relationships
    """
    
    print(f"\n📄 Processing chunk: {chunk.get('chunk_id')}")
    
    # Extract entities
    print("  → Extracting entities...")
    entity_result = extract_entities(chunk["text"])
    entities = entity_result.get("entities", [])
    
    # Validate entities
    valid_entities = []
    for entity in entities:
        is_valid, msg = validate_entity(entity)
        if is_valid:
            valid_entities.append(entity)
        else:
            print(f"    ⚠️  Invalid entity: {msg}")
    
    print(f"  ✅ Extracted {len(valid_entities)} valid entities")
    
    # Extract relationships
    if valid_entities:
        print("  → Extracting relationships...")
        rel_result = extract_relationships(chunk["text"], valid_entities)
        relationships = rel_result.get("relationships", [])
        
        # Validate relationships
        entity_ids = set(e.get("id") for e in valid_entities)
        valid_relationships = []
        for rel in relationships:
            is_valid, msg = validate_relationship(rel, entity_ids)
            if is_valid:
                valid_relationships.append(rel)
            else:
                print(f"    ⚠️  Invalid relationship: {msg}")
        
        print(f"  ✅ Extracted {len(valid_relationships)} valid relationships")
    else:
        valid_relationships = []
    
    return {
        "chunk_id": chunk.get("chunk_id"),
        "source": chunk.get("metadata", {}).get("source"),
        "page": chunk.get("metadata", {}).get("page"),
        "entities": valid_entities,
        "relationships": valid_relationships,
        "timestamp": chunk.get("timestamp")
    }

def process_all_chunks(chunks: List[Dict]) -> Dict:
    """
    Process all document chunks
    
    Args:
        chunks: List of document chunks
        
    Returns:
        Combined extraction results
    """
    
    all_entities = {}
    all_relationships = []
    
    print(f"\n🚀 Processing {len(chunks)} chunks...")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[{i}/{len(chunks)}]", end=" ")
        
        result = process_document_chunk(chunk)
        
        # Store entities (deduplicate by name)
        for entity in result["entities"]:
            entity_key = f"{entity['type']}:{entity['name']}"
            if entity_key not in all_entities:
                all_entities[entity_key] = entity
        
        # Store relationships
        all_relationships.extend(result["relationships"])
    
    print(f"\n\n📊 EXTRACTION SUMMARY:")
    print(f"   Total entities extracted: {len(all_entities)}")
    print(f"   Total relationships extracted: {len(all_relationships)}")
    
    return {
        "entities": list(all_entities.values()),
        "relationships": all_relationships,
        "total_chunks_processed": len(chunks)
    }

# ============================================================================
# SAVE RESULTS
# ============================================================================

def save_extraction_results(results: Dict, output_dir: str = "data/extracted"):
    """Save extraction results to JSON files"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save entities
    entities_file = os.path.join(output_dir, "entities.json")
    with open(entities_file, "w") as f:
        json.dump(results["entities"], f, indent=2)
    print(f"✅ Entities saved to {entities_file}")
    
    # Save relationships
    relationships_file = os.path.join(output_dir, "relationships.json")
    with open(relationships_file, "w") as f:
        json.dump(results["relationships"], f, indent=2)
    print(f"✅ Relationships saved to {relationships_file}")
    
    # Save summary
    summary_file = os.path.join(output_dir, "summary.json")
    summary = {
        "total_entities": len(results["entities"]),
        "total_relationships": len(results["relationships"]),
        "chunks_processed": results["total_chunks_processed"],
        "entity_types": {}
    }
    
    # Count by type
    for entity in results["entities"]:
        entity_type = entity.get("type")
        summary["entity_types"][entity_type] = summary["entity_types"].get(entity_type, 0) + 1
    
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary saved to {summary_file}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Example usage
    sample_chunks = [
        {
            "chunk_id": "chunk_001",
            "text": """
            VAT, or Value Added Tax, is charged at the standard rate of 7.5% on the 
            supply of goods and services in Nigeria. Any business with annual turnover 
            exceeding ₦25 million must register for VAT with FIRS (Federal Inland Revenue Service).
            Failure to register attracts penalties of 5% of the tax plus interest.
            """,
            "metadata": {
                "source": "Tax Reform Act 2025",
                "page": 5
            },
            "timestamp": "2025-11-28T10:00:00Z"
        },
        {
            "chunk_id": "chunk_002",
            "text": """
            PAYE (Pay-As-You-Earn) tax is withheld from employees' salaries. 
            Individuals with annual income exceeding ₦8 million are liable for PAYE.
            Employers must file monthly PAYE returns by the 10th of each month.
            Late filing incurs a penalty of ₦50,000 plus 5% of the tax amount.
            """,
            "metadata": {
                "source": "Tax Reform Act 2025",
                "page": 12
            },
            "timestamp": "2025-11-28T10:00:00Z"
        }
    ]
    
    # Process chunks
    results = process_all_chunks(sample_chunks)
    
    # Save results
    save_extraction_results(results)
    
    print("\n✅ Extraction pipeline completed successfully!")
