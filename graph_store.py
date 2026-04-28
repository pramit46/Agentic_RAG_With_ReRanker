"""
Graph Store Module using Neo4j
Handles relationship-based knowledge storage and graph traversal queries
"""
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from config import config
import json

class GraphStore:
    """
    Graph database implementation using Neo4j
    Stores entities and relationships for context-aware retrieval
    """
    
    def __init__(self):
        """
        Initialize Neo4j driver and establish connection
        Verifies connection to the database
        """
        try:
            self.driver = GraphDatabase.driver(
                config.NEO4J_URI,
                auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
            )
            # Test connection
            self.driver.verify_connectivity()
            print(f"✓ Connected to Neo4j at {config.NEO4J_URI}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {str(e)}")
    
    def close(self):
        """
        Close the Neo4j driver connection
        Should be called when the application shuts down
        """
        if self.driver:
            self.driver.close()
            print("✓ Closed Neo4j connection")
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract meaningful keywords from a natural language query
        Removes common stop words and punctuation
        
        Args:
            query: User's search query
        
        Returns:
            List of keywords to search for
        """
        # Common stop words to filter out
        stop_words = {'what', 'is', 'are', 'the', 'a', 'an', 'how', 'why', 'when', 'where', 
                      'who', 'which', 'can', 'could', 'would', 'should', 'do', 'does', 'did',
                      'tell', 'me', 'about', 'explain', 'describe', 'define'}
        
        # Remove punctuation and split into words
        import re
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out stop words and short words (< 3 chars)
        keywords = [w for w in words if w not in stop_words and len(w) >= 3]
        
        # If no keywords found, return original query
        return keywords if keywords else [query]
    
    def create_document_node(self, doc_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """
        Create a document node in the graph database
        
        Args:
            doc_id: Unique document identifier
            text: Document text content
            metadata: Additional document metadata
        """
        with self.driver.session() as session:
            session.run("""
                MERGE (d:Document {id: $doc_id})
                SET d.text = $text,
                    d.metadata = $metadata,
                    d.created_at = datetime()
            """, doc_id=doc_id, text=text, metadata=json.dumps(metadata))
    
    def create_entity_node(self, entity_name: str, entity_type: str) -> None:
        """
        Create an entity node in the graph
        
        Args:
            entity_name: Name of the entity
            entity_type: Type/category of the entity (e.g., Person, Organization, Concept)
        """
        with self.driver.session() as session:
            session.run("""
                MERGE (e:Entity {name: $name})
                SET e.type = $type,
                    e.updated_at = datetime()
            """, name=entity_name, type=entity_type)
    
    def create_relationship(self, doc_id: str, entity_name: str, relationship_type: str) -> None:
        """
        Create a relationship between a document and an entity
        
        Args:
            doc_id: Document identifier
            entity_name: Entity name
            relationship_type: Type of relationship (e.g., MENTIONS, CONTAINS, RELATES_TO)
        """
        with self.driver.session() as session:
            session.run(f"""
                MATCH (d:Document {{id: $doc_id}})
                MATCH (e:Entity {{name: $entity_name}})
                MERGE (d)-[r:{relationship_type}]->(e)
                SET r.created_at = datetime()
            """, doc_id=doc_id, entity_name=entity_name)
    
    def add_documents_with_entities(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents with their entities and relationships to the graph
        
        Args:
            documents: List of document dictionaries containing text, metadata, and entities
        """
        for doc in documents:
            doc_id = doc.get("id", str(hash(doc["text"])))
            text = doc["text"]
            metadata = doc.get("metadata", {})
            entities = doc.get("entities", [])
            
            # Create document node
            self.create_document_node(doc_id, text, metadata)
            
            # Create entity nodes and relationships
            for entity in entities:
                entity_name = entity.get("name")
                entity_type = entity.get("type", "Unknown")
                relationship = entity.get("relationship", "MENTIONS")
                
                if entity_name:
                    self.create_entity_node(entity_name, entity_type)
                    self.create_relationship(doc_id, entity_name, relationship)
        
        print(f"✓ Added {len(documents)} documents with entities to graph store")
    
    def graph_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Perform graph-based search using entity relationships
        Finds documents connected to relevant entities
        
        Args:
            query: Search query (can contain entity names or keywords)
            top_k: Number of results to return (defaults to config.TOP_K_GRAPH)
        
        Returns:
            List of documents with graph-based relevance scores
        """
        if top_k is None:
            top_k = config.TOP_K_GRAPH
        
        # Extract keywords from natural language query
        keywords = self._extract_keywords(query)
        
        documents = []
        doc_ids_seen = set()  # Track unique documents
        
        with self.driver.session() as session:
            # Search for each keyword and combine results
            for keyword in keywords:
                result = session.run("""
                    MATCH (d:Document)-[r]->(e:Entity)
                    WHERE toLower(e.name) CONTAINS toLower($search_query) 
                       OR toLower(d.text) CONTAINS toLower($search_query)
                    WITH d, COUNT(r) as relationship_count
                    ORDER BY relationship_count DESC
                    LIMIT $limit
                    RETURN d.id as id, d.text as text, d.metadata as metadata, relationship_count
                """, search_query=keyword, limit=top_k)
                
                for record in result:
                    doc_id = record["id"]
                    # Only add each document once (take highest score)
                    if doc_id not in doc_ids_seen:
                        doc_ids_seen.add(doc_id)
                        documents.append({
                            "text": record["text"],
                            "metadata": json.loads(record["metadata"]) if record["metadata"] else {},
                            "score": float(record["relationship_count"]) / 10.0,  # Normalize score
                            "source": "graph_search",
                            "id": doc_id
                        })
            
            # Sort by score and limit results
            documents.sort(key=lambda x: x["score"], reverse=True)
            documents = documents[:top_k]
        
        return documents
    
    def get_entity_relationships(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Get all documents related to a specific entity
        
        Args:
            entity_name: Name of the entity to search for
        
        Returns:
            List of related documents
        """
        documents = []
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)-[r]->(e:Entity {name: $entity_name})
                RETURN d.id as id, d.text as text, d.metadata as metadata, type(r) as relationship_type
            """, entity_name=entity_name)
            
            for record in result:
                documents.append({
                    "text": record["text"],
                    "metadata": json.loads(record["metadata"]) if record["metadata"] else {},
                    "relationship": record["relationship_type"],
                    "source": "entity_relationship",
                    "id": record["id"]
                })
        
        return documents
    
    def reset(self) -> None:
        """
        Reset the graph database by deleting all nodes and relationships
        Use with caution - this removes all stored data
        """
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Reset graph database")
