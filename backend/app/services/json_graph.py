"""
JSON-based Knowledge Graph Service
Replaces Neo4j with a simple JSON file storage - no setup required!
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class JSONGraphDB:
    """Simple JSON-based graph database - no Neo4j needed!"""
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path or os.getenv(
            'GRAPH_DB_PATH', 
            '/workspaces/AI-TAX-REFORM/data/knowledge_graph.json'
        )
        self.graph = self._load_graph()
    
    def _load_graph(self) -> Dict:
        """Load graph from JSON file or create empty one"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default empty graph structure
        return {
            "nodes": {},
            "relationships": [],
            "metadata": {
                "created": None,
                "last_updated": None,
                "version": "1.0"
            }
        }
    
    def _save_graph(self):
        """Save graph to JSON file"""
        # Ensure directory exists
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        self.graph["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.file_path, 'w') as f:
            json.dump(self.graph, f, indent=2)
    
    def add_node(self, node_id: str, node_type: str, properties: Dict = None) -> Dict:
        """Add a node to the graph"""
        node = {
            "id": node_id,
            "type": node_type,
            "properties": properties or {}
        }
        self.graph["nodes"][node_id] = node
        self._save_graph()
        return node
    
    def add_relationship(self, source_id: str, target_id: str, 
                         rel_type: str, properties: Dict = None) -> Dict:
        """Add a relationship between two nodes"""
        rel = {
            "source": source_id,
            "target": target_id,
            "type": rel_type,
            "properties": properties or {}
        }
        self.graph["relationships"].append(rel)
        self._save_graph()
        return rel
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get a node by ID"""
        return self.graph["nodes"].get(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Get all nodes of a specific type"""
        return [
            node for node in self.graph["nodes"].values()
            if node["type"] == node_type
        ]
    
    def get_relationships(self, node_id: str = None, rel_type: str = None) -> List[Dict]:
        """Get relationships, optionally filtered by node or type"""
        rels = self.graph["relationships"]
        
        if node_id:
            rels = [r for r in rels if r["source"] == node_id or r["target"] == node_id]
        
        if rel_type:
            rels = [r for r in rels if r["type"] == rel_type]
        
        return rels
    
    def search(self, query: str, node_types: List[str] = None) -> List[Dict]:
        """Search nodes by text match in properties"""
        query_lower = query.lower()
        results = []
        
        for node in self.graph["nodes"].values():
            # Filter by type if specified
            if node_types and node["type"] not in node_types:
                continue
            
            # Search in node properties
            for key, value in node["properties"].items():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(node)
                    break
        
        return results
    
    def get_related_entities(self, node_id: str, 
                              rel_types: List[str] = None,
                              max_depth: int = 2) -> List[Dict]:
        """Get entities related to a node up to max_depth"""
        visited = set()
        results = []
        
        def traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            for rel in self.graph["relationships"]:
                # Check if relationship type matches filter
                if rel_types and rel["type"] not in rel_types:
                    continue
                
                # Get connected node
                if rel["source"] == current_id:
                    target = self.graph["nodes"].get(rel["target"])
                    if target and target["id"] not in visited:
                        results.append({
                            "node": target,
                            "relationship": rel,
                            "depth": depth
                        })
                        traverse(rel["target"], depth + 1)
                
                elif rel["target"] == current_id:
                    source = self.graph["nodes"].get(rel["source"])
                    if source and source["id"] not in visited:
                        results.append({
                            "node": source,
                            "relationship": rel,
                            "depth": depth
                        })
                        traverse(rel["source"], depth + 1)
        
        traverse(node_id, 1)
        return results
    
    def get_stats(self) -> Dict:
        """Get graph statistics"""
        node_types = {}
        for node in self.graph["nodes"].values():
            node_type = node["type"]
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        rel_types = {}
        for rel in self.graph["relationships"]:
            rel_type = rel["type"]
            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
        
        return {
            "total_nodes": len(self.graph["nodes"]),
            "total_relationships": len(self.graph["relationships"]),
            "node_types": node_types,
            "relationship_types": rel_types,
            "metadata": self.graph["metadata"]
        }
    
    def clear(self):
        """Clear the entire graph"""
        self.graph = {
            "nodes": {},
            "relationships": [],
            "metadata": self.graph["metadata"]
        }
        self._save_graph()
    
    def import_from_entities(self, entities_file: str, relationships_file: str = None):
        """Import graph from extracted entities JSON files"""
        # Load entities
        if os.path.exists(entities_file):
            with open(entities_file, 'r') as f:
                entities = json.load(f)
            
            for entity in entities:
                self.add_node(
                    node_id=entity.get("id", entity.get("name", "")),
                    node_type=entity.get("type", "Entity"),
                    properties={
                        "name": entity.get("name", ""),
                        "description": entity.get("description", ""),
                        **{k: v for k, v in entity.items() if k not in ["id", "type", "name", "description"]}
                    }
                )
        
        # Load relationships if provided
        if relationships_file and os.path.exists(relationships_file):
            with open(relationships_file, 'r') as f:
                relationships = json.load(f)
            
            for rel in relationships[:1000]:  # Limit to first 1000
                self.add_relationship(
                    source_id=rel.get("source", ""),
                    target_id=rel.get("target", ""),
                    rel_type=rel.get("type", "related_to"),
                    properties=rel.get("properties", {})
                )
        
        return self.get_stats()


# Singleton instance
_graph_db = None

def get_graph_db() -> JSONGraphDB:
    """Get or create the graph database instance"""
    global _graph_db
    if _graph_db is None:
        _graph_db = JSONGraphDB()
    return _graph_db


# GraphRetriever-compatible interface
class JSONGraphRetriever:
    """Graph retriever that works with JSON graph instead of Neo4j"""
    
    def __init__(self):
        self.db = get_graph_db()
    
    def search_entities(self, query: str, entity_types: List[str] = None) -> List[Dict]:
        """Search for entities matching the query"""
        return self.db.search(query, entity_types)
    
    def get_entity_context(self, entity_id: str) -> Dict:
        """Get full context for an entity including relationships"""
        node = self.db.get_node(entity_id)
        if not node:
            return {"entity": None, "related": []}
        
        related = self.db.get_related_entities(entity_id, max_depth=2)
        
        return {
            "entity": node,
            "related": related
        }
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant entities for a query"""
        # Extract potential entity mentions
        keywords = query.lower().split()
        
        results = []
        seen_ids = set()
        
        for keyword in keywords:
            if len(keyword) < 3:
                continue
            
            matches = self.db.search(keyword)
            for match in matches:
                if match["id"] not in seen_ids:
                    seen_ids.add(match["id"])
                    results.append(match)
        
        # Sort by relevance (simple: more keyword matches = higher score)
        def score(node):
            text = json.dumps(node["properties"]).lower()
            return sum(1 for kw in keywords if kw in text)
        
        results.sort(key=score, reverse=True)
        
        return results[:top_k]
