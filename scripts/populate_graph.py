"""
Neo4j Graph Population Script
Populates Neo4j database with extracted entities and relationships
"""

import json
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

load_dotenv()

# ============================================================================
# NEO4J CONNECTION
# ============================================================================

class Neo4jConnection:
    """Neo4j database connection manager"""
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        self.driver = None
        self.session = None
    
    def connect(self):
        """Establish Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Verify connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            print("✅ Connected to Neo4j successfully!")
            return True
        except ServiceUnavailable:
            print("❌ Could not connect to Neo4j. Check URI and credentials.")
            return False
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("✅ Disconnected from Neo4j")
    
    def execute_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Execute a Cypher query"""
        if not self.driver:
            print("❌ Not connected to Neo4j")
            return []
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            print(f"❌ Query execution error: {str(e)}")
            return []

# ============================================================================
# ENTITY POPULATION
# ============================================================================

def create_entity_node(conn: Neo4jConnection, entity: Dict) -> Tuple[bool, str]:
    """
    Create a node for an entity in Neo4j
    
    Args:
        conn: Neo4j connection
        entity: Entity dictionary with type, name, properties
        
    Returns:
        Tuple of (success, message)
    """
    
    entity_type = entity.get("type")
    entity_name = entity.get("name")
    properties = entity.get("properties", {})
    
    if not entity_type or not entity_name:
        return False, "Missing entity type or name"
    
    # Build properties clause
    props_list = [f"name: '{entity_name}'"]
    for key, value in properties.items():
        if isinstance(value, str):
            props_list.append(f"{key}: '{value}'")
        elif isinstance(value, (int, float)):
            props_list.append(f"{key}: {value}")
        elif isinstance(value, bool):
            props_list.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, list):
            props_list.append(f"{key}: {json.dumps(value)}")
    
    props_clause = ", ".join(props_list)
    
    # Create Cypher query
    query = f"""
    MERGE (n:{entity_type} {{name: '{entity_name}'}})
    SET {", ".join([f"n.{key} = ${key}" for key in properties.keys()])}
    RETURN n
    """
    
    try:
        # Build parameters
        params = {"entity_type": entity_type, "name": entity_name}
        params.update(properties)
        
        # Execute more simple query
        simple_query = f"""
        MERGE (n:{entity_type} {{name: $name}})
        RETURN n
        """
        conn.execute_query(simple_query, {"name": entity_name})
        
        return True, f"Created {entity_type} node: {entity_name}"
    except Exception as e:
        return False, f"Error creating node: {str(e)}"

def populate_entities(conn: Neo4jConnection, entities: List[Dict]) -> Dict:
    """
    Populate all entities to Neo4j
    
    Args:
        conn: Neo4j connection
        entities: List of extracted entities
        
    Returns:
        Statistics dictionary
    """
    
    print("\n🔧 Populating entities to Neo4j...")
    
    stats = {
        "total": len(entities),
        "created": 0,
        "failed": 0,
        "by_type": {}
    }
    
    for i, entity in enumerate(entities, 1):
        entity_type = entity.get("type")
        entity_name = entity.get("name")
        
        success, msg = create_entity_node(conn, entity)
        
        if success:
            stats["created"] += 1
            stats["by_type"][entity_type] = stats["by_type"].get(entity_type, 0) + 1
            if i % 5 == 0:
                print(f"  ✅ [{i}/{len(entities)}] {msg}")
        else:
            stats["failed"] += 1
            print(f"  ⚠️  [{i}/{len(entities)}] {msg}")
    
    print(f"\n📊 Entity population summary:")
    print(f"   Created: {stats['created']}")
    print(f"   Failed: {stats['failed']}")
    for entity_type, count in stats["by_type"].items():
        print(f"   {entity_type}: {count}")
    
    return stats

# ============================================================================
# RELATIONSHIP POPULATION
# ============================================================================

def create_relationship(conn: Neo4jConnection, relationship: Dict) -> Tuple[bool, str]:
    """
    Create a relationship between two entities in Neo4j
    
    Args:
        conn: Neo4j connection
        relationship: Relationship dictionary
        
    Returns:
        Tuple of (success, message)
    """
    
    source_id = relationship.get("source_id")
    target_id = relationship.get("target_id")
    rel_type = relationship.get("relationship_type")
    
    if not all([source_id, target_id, rel_type]):
        return False, "Missing relationship fields"
    
    try:
        query = f"""
        MATCH (a {{name: $source}})
        MATCH (b {{name: $target}})
        MERGE (a)-[r:{rel_type}]-(b)
        RETURN r
        """
        
        conn.execute_query(query, {
            "source": source_id,
            "target": target_id
        })
        
        return True, f"Created {rel_type} relationship"
    except Exception as e:
        return False, f"Error creating relationship: {str(e)}"

def populate_relationships(conn: Neo4jConnection, relationships: List[Dict]) -> Dict:
    """
    Populate all relationships to Neo4j
    
    Args:
        conn: Neo4j connection
        relationships: List of extracted relationships
        
    Returns:
        Statistics dictionary
    """
    
    print("\n🔗 Populating relationships to Neo4j...")
    
    stats = {
        "total": len(relationships),
        "created": 0,
        "failed": 0,
        "by_type": {}
    }
    
    for i, rel in enumerate(relationships, 1):
        rel_type = rel.get("relationship_type")
        
        success, msg = create_relationship(conn, rel)
        
        if success:
            stats["created"] += 1
            stats["by_type"][rel_type] = stats["by_type"].get(rel_type, 0) + 1
            if i % 5 == 0:
                print(f"  ✅ [{i}/{len(relationships)}] {msg}")
        else:
            stats["failed"] += 1
            if i % 10 == 0:
                print(f"  ⚠️  [{i}/{len(relationships)}] {msg}")
    
    print(f"\n📊 Relationship population summary:")
    print(f"   Created: {stats['created']}")
    print(f"   Failed: {stats['failed']}")
    for rel_type, count in stats["by_type"].items():
        print(f"   {rel_type}: {count}")
    
    return stats

# ============================================================================
# GRAPH VALIDATION
# ============================================================================

def validate_graph(conn: Neo4jConnection) -> Dict:
    """
    Validate the populated graph
    
    Args:
        conn: Neo4j connection
        
    Returns:
        Validation statistics
    """
    
    print("\n✔️  Validating graph...")
    
    stats = {}
    
    # Count nodes by label
    query = "MATCH (n) RETURN labels(n)[0] as label, COUNT(*) as count"
    results = conn.execute_query(query)
    
    print("\n📊 Nodes by type:")
    for record in results:
        label = record.get("label") or "Unknown"
        count = record.get("count", 0)
        stats[label] = count
        print(f"   {label}: {count}")
    
    # Count relationships
    query = "MATCH ()-[r]->() RETURN type(r) as rel_type, COUNT(*) as count"
    results = conn.execute_query(query)
    
    print("\n📊 Relationships by type:")
    for record in results:
        rel_type = record.get("rel_type") or "Unknown"
        count = record.get("count", 0)
        print(f"   {rel_type}: {count}")
    
    return stats

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def load_extraction_results(input_dir: str = "data/extracted") -> Dict:
    """Load extracted entities and relationships from files"""
    
    entities_file = os.path.join(input_dir, "entities.json")
    relationships_file = os.path.join(input_dir, "relationships.json")
    
    entities = []
    relationships = []
    
    if os.path.exists(entities_file):
        with open(entities_file, "r") as f:
            entities = json.load(f)
        print(f"✅ Loaded {len(entities)} entities")
    
    if os.path.exists(relationships_file):
        with open(relationships_file, "r") as f:
            relationships = json.load(f)
        print(f"✅ Loaded {len(relationships)} relationships")
    
    return {"entities": entities, "relationships": relationships}

def populate_graph(entities: List[Dict], relationships: List[Dict]):
    """Main pipeline to populate the graph"""
    
    # Connect to Neo4j
    conn = Neo4jConnection()
    if not conn.connect():
        print("❌ Failed to connect to Neo4j. Check your credentials in .env")
        return
    
    try:
        # Populate entities
        entity_stats = populate_entities(conn, entities)
        
        # Populate relationships
        rel_stats = populate_relationships(conn, relationships)
        
        # Validate
        validate_graph(conn)
        
        print("\n✅ Graph population completed successfully!")
        
    finally:
        conn.disconnect()

# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "data/extracted"
    
    print(f"📂 Loading extraction results from: {input_dir}")
    results = load_extraction_results(input_dir)
    
    print(f"\n🚀 Starting graph population...")
    populate_graph(results["entities"], results["relationships"])
