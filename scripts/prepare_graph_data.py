"""
Simple Neo4j Graph Population
Pattern-based approach without connection requirement
Creates sample data that can be imported
"""

import json
from pathlib import Path

def generate_cypher_script(entities_file: str, relationships_file: str, output_file: str):
    """
    Generate Cypher import script from extracted entities
    
    Args:
        entities_file: Path to entities JSON
        relationships_file: Path to relationships JSON
        output_file: Path to output Cypher script
    """
    with open(entities_file, 'r', encoding='utf-8') as f:
        entities = json.load(f)
    
    with open(relationships_file, 'r', encoding='utf-8') as f:
        relationships = json.load(f)
    
    cypher_lines = []
    
    # Header
    cypher_lines.append("// Neo4j Import Script - Generated from Tax Document Extraction")
    cypher_lines.append("// This script creates nodes and relationships for the tax knowledge graph")
    cypher_lines.append("")
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("// CREATE CONSTRAINTS")
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("")
    cypher_lines.append("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tax) REQUIRE t.id IS UNIQUE;")
    cypher_lines.append("CREATE CONSTRAINT IF NOT EXISTS FOR (tp:Taxpayer) REQUIRE tp.id IS UNIQUE;")
    cypher_lines.append("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Agency) REQUIRE a.id IS UNIQUE;")
    cypher_lines.append("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Process) REQUIRE p.id IS UNIQUE;")
    cypher_lines.append("CREATE CONSTRAINT IF NOT EXISTS FOR (pen:Penalty) REQUIRE pen.id IS UNIQUE;")
    cypher_lines.append("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Deadline) REQUIRE d.id IS UNIQUE;")
    cypher_lines.append("")
    
    # Create indices
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("// CREATE INDICES")
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("")
    cypher_lines.append("CREATE INDEX IF NOT EXISTS FOR (t:Tax) ON (t.name);")
    cypher_lines.append("CREATE INDEX IF NOT EXISTS FOR (tp:Taxpayer) ON (tp.name);")
    cypher_lines.append("CREATE INDEX IF NOT EXISTS FOR (a:Agency) ON (a.name);")
    cypher_lines.append("")
    
    # Create nodes
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("// CREATE NODES")
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("")
    
    # Group entities by type
    entities_by_type = {}
    for entity in entities:
        entity_type = entity['type']
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity)
    
    # Create nodes for each type
    for entity_type, type_entities in entities_by_type.items():
        cypher_lines.append(f"// Create {entity_type} nodes")
        for i, entity in enumerate(type_entities, 1):
            # Escape quotes in name
            name = entity['name'].replace('"', '\\"')
            desc = entity.get('description', '').replace('"', '\\"')
            
            cypher_line = f"MERGE (n:{entity_type} {{id: '{entity['id']}', name: \"{name}\", page: {entity.get('page', 0)}, description: \"{desc}\"}})"
            cypher_lines.append(cypher_line)
        cypher_lines.append("")
    
    # Create relationships
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("// CREATE RELATIONSHIPS")
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("")
    
    # Group relationships by type
    rels_by_type = {}
    for rel in relationships[:100]:  # Limit to first 100 to keep file manageable
        rel_type = rel['relationship']
        if rel_type not in rels_by_type:
            rels_by_type[rel_type] = []
        rels_by_type[rel_type].append(rel)
    
    for rel_type, type_rels in rels_by_type.items():
        cypher_lines.append(f"// Create {rel_type} relationships")
        for rel in type_rels:
            source_type = rel['source_type']
            target_type = rel['target_type']
            
            cypher_line = f"MATCH (s:{source_type} {{id: '{rel['source_id']}'}}), (t:{target_type} {{id: '{rel['target_id']}'}}) MERGE (s)-[:{rel_type}]->(t)"
            cypher_lines.append(cypher_line)
        cypher_lines.append("")
    
    # Statistics
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("// VERIFICATION QUERIES")
    cypher_lines.append("// ============================================================================")
    cypher_lines.append("")
    cypher_lines.append("// Count total nodes")
    cypher_lines.append("MATCH (n) RETURN COUNT(n) as total_nodes;")
    cypher_lines.append("")
    cypher_lines.append("// Count nodes by type")
    cypher_lines.append("MATCH (n) RETURN labels(n)[0] as type, COUNT(n) as count ORDER BY count DESC;")
    cypher_lines.append("")
    cypher_lines.append("// Count relationships by type")
    cypher_lines.append("MATCH ()-[r]-() RETURN TYPE(r) as relationship, COUNT(r) as count ORDER BY count DESC;")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cypher_lines))
    
    print(f"✅ Generated Cypher script: {output_file}")
    print(f"   - {len(entities)} entities")
    print(f"   - {sum(len(v) for v in rels_by_type.values())} relationships")
    print(f"   - {len(cypher_lines)} lines")


def create_sample_data_json(entities_file: str, relationships_file: str, output_file: str):
    """
    Create sample data JSON for verification
    
    Args:
        entities_file: Path to entities JSON
        relationships_file: Path to relationships JSON
        output_file: Path to output JSON
    """
    with open(entities_file, 'r', encoding='utf-8') as f:
        entities = json.load(f)
    
    with open(relationships_file, 'r', encoding='utf-8') as f:
        relationships = json.load(f)
    
    # Create sample data structure
    sample_data = {
        "metadata": {
            "source": "Nigeria Tax Act 2025",
            "extraction_date": "2025-01-15",
            "total_entities": len(entities),
            "total_relationships": len(relationships)
        },
        "entities": entities,
        "relationships": relationships[:100],  # First 100 relationships
        "statistics": {
            "by_type": {}
        }
    }
    
    # Calculate statistics
    for entity_type in set(e['type'] for e in entities):
        count = len([e for e in entities if e['type'] == entity_type])
        sample_data['statistics']['by_type'][entity_type] = count
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created sample data JSON: {output_file}")


def main():
    # Paths
    entities_file = 'data/extracted/entities.json'
    relationships_file = 'data/extracted/relationships.json'
    cypher_output = 'data/extracted/import.cypher'
    sample_output = 'data/extracted/sample_data.json'
    
    print("📊 Generating Neo4j import scripts...\n")
    
    # Generate Cypher script
    generate_cypher_script(entities_file, relationships_file, cypher_output)
    
    print("\n📋 Creating sample data JSON...\n")
    
    # Create sample data
    create_sample_data_json(entities_file, relationships_file, sample_output)
    
    print("\n✅ Graph data preparation complete!")
    print(f"\nNext steps:")
    print(f"1. Use the Cypher script to populate Neo4j:")
    print(f"   - Go to Neo4j Browser")
    print(f"   - Copy content from: {cypher_output}")
    print(f"   - Paste and execute")
    print(f"\n2. Or use Neo4j Import tools:")
    print(f"   - See {sample_output} for data structure")


if __name__ == "__main__":
    main()
