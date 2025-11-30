"""
JSON-Based Knowledge Graph Service for NTRIA
Replaces Neo4j with a simple JSON file store.
No Docker, no cloud setup - just works!
"""

import os
import json
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GRAPH_DB_PATH = os.getenv("GRAPH_DB_PATH", "/workspaces/AI-TAX-REFORM/data/knowledge_graph.json")


class JsonGraphService:
    """Simple JSON-based knowledge graph service."""
    
    def __init__(self, db_path: str = GRAPH_DB_PATH, read_only: bool = True):
        """
        Initialize the graph service.
        
        Args:
            db_path: Path to the JSON graph file
            read_only: If True, write operations will be disabled (runtime safety)
        """
        self.db_path = Path(db_path)
        self.read_only = read_only
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create graph
        if self.db_path.exists():
            with open(self.db_path, "r") as f:
                self.graph = json.load(f)
        else:
            self.graph = {
                "nodes": {},      # id -> {type, name, properties}
                "edges": [],      # [{source, target, type, properties}]
                "metadata": {
                    "version": "1.0",
                    "created": str(Path(db_path).stat().st_mtime if self.db_path.exists() else "new")
                }
            }
            if not self.read_only:
                self._save()
        
        mode = "READ-ONLY" if self.read_only else "READ-WRITE"
        print(f"✅ JSON Graph initialized ({mode}): {len(self.graph['nodes'])} nodes, {len(self.graph['edges'])} edges")
    
    def _save(self):
        """Save graph to disk."""
        if self.read_only:
            print("⚠️ Attempted to save in READ-ONLY mode. Operation ignored.")
            return
            
        with open(self.db_path, "w") as f:
            json.dump(self.graph, f, indent=2)
    
    # ========================================================================
    # Node Operations
    # ========================================================================
    
    def add_node(
        self, 
        node_id: str, 
        node_type: str, 
        name: str, 
        properties: Optional[Dict] = None
    ) -> Dict:
        """Add a node to the graph."""
        node = {
            "id": node_id,
            "type": node_type,
            "name": name,
            "properties": properties or {}
        }
        self.graph["nodes"][node_id] = node
        self._save()
        return node
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get a node by ID."""
        return self.graph["nodes"].get(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Get all nodes of a specific type."""
        return [
            node for node in self.graph["nodes"].values()
            if node["type"] == node_type
        ]
    
    def search_nodes(self, query: str, node_type: Optional[str] = None) -> List[Dict]:
        """Search nodes by name (case-insensitive)."""
        query_lower = query.lower()
        results = []
        
        for node in self.graph["nodes"].values():
            if node_type and node["type"] != node_type:
                continue
            if query_lower in node["name"].lower():
                results.append(node)
        
        return results
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its edges."""
        if node_id not in self.graph["nodes"]:
            return False
        
        del self.graph["nodes"][node_id]
        self.graph["edges"] = [
            e for e in self.graph["edges"]
            if e["source"] != node_id and e["target"] != node_id
        ]
        self._save()
        return True
    
    # ========================================================================
    # Edge Operations
    # ========================================================================
    
    def add_edge(
        self, 
        source_id: str, 
        target_id: str, 
        edge_type: str, 
        properties: Optional[Dict] = None
    ) -> Dict:
        """Add an edge between two nodes."""
        edge = {
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "properties": properties or {}
        }
        self.graph["edges"].append(edge)
        self._save()
        return edge
    
    def get_edges(
        self, 
        source_id: Optional[str] = None, 
        target_id: Optional[str] = None,
        edge_type: Optional[str] = None
    ) -> List[Dict]:
        """Get edges with optional filters."""
        results = []
        
        for edge in self.graph["edges"]:
            if source_id and edge["source"] != source_id:
                continue
            if target_id and edge["target"] != target_id:
                continue
            if edge_type and edge["type"] != edge_type:
                continue
            results.append(edge)
        
        return results
    
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[Dict]:
        """Get all nodes connected to a node."""
        neighbor_ids: Set[str] = set()
        
        for edge in self.graph["edges"]:
            if edge_type and edge["type"] != edge_type:
                continue
            if edge["source"] == node_id:
                neighbor_ids.add(edge["target"])
            elif edge["target"] == node_id:
                neighbor_ids.add(edge["source"])
        
        return [self.graph["nodes"][nid] for nid in neighbor_ids if nid in self.graph["nodes"]]
    
    # ========================================================================
    # Query Operations (Graph RAG)
    # ========================================================================
    
    def find_related_entities(
        self, 
        entity_names: List[str], 
        max_depth: int = 2
    ) -> List[Dict]:
        """
        Find entities related to the given names.
        Used for Graph RAG context building.
        """
        # Find matching nodes
        start_nodes = []
        for name in entity_names:
            matching = self.search_nodes(name)
            start_nodes.extend(matching)
        
        if not start_nodes:
            return []
        
        # BFS to find related nodes
        visited = set()
        related = []
        queue = [(node["id"], 0) for node in start_nodes]
        
        while queue:
            node_id, depth = queue.pop(0)
            
            if node_id in visited or depth > max_depth:
                continue
            
            visited.add(node_id)
            node = self.graph["nodes"].get(node_id)
            
            if node:
                related.append({
                    **node,
                    "depth": depth
                })
                
                # Add neighbors to queue
                for neighbor in self.get_neighbors(node_id):
                    if neighbor["id"] not in visited:
                        queue.append((neighbor["id"], depth + 1))
        
        return related
    
    def get_entity_context(self, entity_name: str) -> str:
        """
        Get context about an entity for RAG.
        Returns a text description of the entity and its relationships.
        """
        nodes = self.search_nodes(entity_name)
        
        if not nodes:
            return ""
        
        context_parts = []
        
        for node in nodes[:3]:  # Limit to top 3 matches
            context_parts.append(f"{node['type']}: {node['name']}")
            
            # Add properties
            for key, value in node.get("properties", {}).items():
                if value:
                    context_parts.append(f"  - {key}: {value}")
            
            # Add relationships
            edges = self.get_edges(source_id=node["id"])
            for edge in edges[:5]:  # Limit relationships
                target = self.graph["nodes"].get(edge["target"])
                if target:
                    context_parts.append(f"  → {edge['type']}: {target['name']}")
            
            # Add incoming relationships
            edges = self.get_edges(target_id=node["id"])
            for edge in edges[:5]:
                source = self.graph["nodes"].get(edge["source"])
                if source:
                    context_parts.append(f"  ← {edge['type']}: {source['name']}")
        
        return "\n".join(context_parts)
    
    # ========================================================================
    # Bulk Operations
    # ========================================================================
    
    def import_from_json(self, data: Dict) -> Dict[str, int]:
        """
        Import nodes and edges from a dictionary.
        
        Args:
            data: Dict with 'nodes' list and 'edges' list
            
        Returns:
            Count of imported nodes and edges
        """
        nodes_added = 0
        edges_added = 0
        
        # Import nodes
        for node in data.get("nodes", []):
            node_id = node.get("id", node.get("name", "").replace(" ", "_").lower())
            self.graph["nodes"][node_id] = {
                "id": node_id,
                "type": node.get("type", "Entity"),
                "name": node.get("name", node_id),
                "properties": node.get("properties", {})
            }
            nodes_added += 1
        
        # Import edges
        for edge in data.get("edges", data.get("relationships", [])):
            self.graph["edges"].append({
                "source": edge.get("source", edge.get("from", "")),
                "target": edge.get("target", edge.get("to", "")),
                "type": edge.get("type", edge.get("relationship", "related_to")),
                "properties": edge.get("properties", {})
            })
            edges_added += 1
        
        self._save()
        return {"nodes": nodes_added, "edges": edges_added}
    
    def clear(self):
        """Clear all data."""
        self.graph = {
            "nodes": {},
            "edges": [],
            "metadata": {"version": "1.0", "cleared": "true"}
        }
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        node_types = {}
        for node in self.graph["nodes"].values():
            t = node["type"]
            node_types[t] = node_types.get(t, 0) + 1
        
        edge_types = {}
        for edge in self.graph["edges"]:
            t = edge["type"]
            edge_types[t] = edge_types.get(t, 0) + 1
        
        return {
            "total_nodes": len(self.graph["nodes"]),
            "total_edges": len(self.graph["edges"]),
            "node_types": node_types,
            "edge_types": edge_types
        }


# Singleton instance
_graph_service = None

def get_graph_service() -> JsonGraphService:
    """Get or create graph service instance."""
    global _graph_service
    if _graph_service is None:
        _graph_service = JsonGraphService()
    return _graph_service


# Quick test
if __name__ == "__main__":
    service = get_graph_service()
    
    print("\n📊 Graph Stats:")
    print(json.dumps(service.get_stats(), indent=2))
    
    # Test search
    print("\n🔍 Testing search for 'VAT'...")
    results = service.search_nodes("VAT")
    print(f"Found {len(results)} nodes")
    for r in results:
        print(f"  - {r['type']}: {r['name']}")
