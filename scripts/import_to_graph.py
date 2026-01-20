"""
Import Extracted Entities to JSON Graph
Loads the extracted entities and relationships into the JSON-based knowledge graph.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from dotenv import load_dotenv
load_dotenv()


def load_entities():
    """Load extracted entities."""
    # Use relative path
    base_dir = Path(__file__).parent.parent
    entities_path = base_dir / "data" / "extracted" / "entities.json"
    
    if not entities_path.exists():
        print(f"❌ Entities file not found: {entities_path}")
        return []
    
    with open(entities_path, "r") as f:
        return json.load(f)


def load_relationships():
    """Load extracted relationships."""
    # Use relative path
    base_dir = Path(__file__).parent.parent
    rels_path = base_dir / "data" / "extracted" / "relationships.json"
    
    if not rels_path.exists():
        print(f"❌ Relationships file not found: {rels_path}")
        return []
    
    with open(rels_path, "r") as f:
        data = json.load(f)
        # Limit to avoid huge graph
        if len(data) > 1000:
            print(f"   Limiting relationships from {len(data)} to 1000")
            return data[:1000]
        return data


def import_to_graph():
    """Import entities and relationships to JSON graph."""
    from app.services.graph_service import get_graph_service
    
    print("=" * 60)
    print("📥 IMPORTING DATA TO KNOWLEDGE GRAPH")
    print("=" * 60)
    
    # Initialize graph
    service = get_graph_service()
    
    # Get current stats
    print("\n📊 Current graph stats:")
    stats = service.get_stats()
    print(f"   Nodes: {stats['total_nodes']}")
    print(f"   Edges: {stats['total_edges']}")
    
    # Load entities
    print("\n📂 Loading entities...")
    entities = load_entities()
    print(f"   Loaded {len(entities)} entities")
    
    # Load relationships
    print("\n📂 Loading relationships...")
    relationships = load_relationships()
    print(f"   Loaded {len(relationships)} relationships")
    
    # Import entities as nodes
    print("\n➕ Adding nodes...")
    nodes_added = 0
    for entity in entities:
        # Handle different entity formats
        if isinstance(entity, dict):
            entity_type = entity.get("type", entity.get("label", "Entity"))
            entity_name = entity.get("name", entity.get("value", str(entity)))
            # Use the existing ID from the file
            entity_id = entity.get("id", entity_name.replace(" ", "_").lower())
            properties = {
                "description": entity.get("description", ""),
                "page": entity.get("page", 0),
                "chunk_id": entity.get("chunk_id", 0)
            }
        elif isinstance(entity, str):
            entity_type = "Entity"
            entity_name = entity
            entity_id = entity.replace(" ", "_").lower()
            properties = {}
        else:
            continue
        
        service.add_node(
            node_id=entity_id,
            node_type=entity_type,
            name=entity_name,
            properties=properties
        )
        nodes_added += 1
    
    print(f"   Added {nodes_added} nodes")
    
    # Import relationships as edges
    print("\n🔗 Adding edges...")
    edges_added = 0
    for rel in relationships:
        if isinstance(rel, dict):
            # Handle the actual format from extract_entities_simple.py
            source = rel.get("source_id", rel.get("source", rel.get("from", "")))
            target = rel.get("target_id", rel.get("target", rel.get("to", "")))
            rel_type = rel.get("relationship", rel.get("type", "related_to"))
            
            # Use IDs directly (they're already formatted)
            source_id = source if source else ""
            target_id = target if target else ""
            
            if source_id and target_id:
                service.add_edge(
                    source_id=source_id,
                    target_id=target_id,
                    edge_type=rel_type,
                    properties={"description": rel.get("description", "")}
                )
                edges_added += 1
    
    print(f"   Added {edges_added} edges")
    
    # Final stats
    print("\n📊 Final graph stats:")
    stats = service.get_stats()
    print(f"   Total nodes: {stats['total_nodes']}")
    print(f"   Total edges: {stats['total_edges']}")
    print(f"   Node types: {stats['node_types']}")
    print(f"   Edge types: {stats['edge_types']}")
    
    # Test search
    print("\n🔍 Testing graph search...")
    results = service.search_nodes("VAT")
    print(f"   Found {len(results)} nodes matching 'VAT'")
    for r in results[:5]:
        print(f"   - {r['type']}: {r['name']}")
    
    print("\n" + "=" * 60)
    print("✅ IMPORT COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    import_to_graph()
