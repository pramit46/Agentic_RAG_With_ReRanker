"""
Human-in-the-Loop (HITL) Re-ranking Module
Implements implicit feedback learning by boosting results when humans select them
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from config import config
import numpy as np

class HITLReranker:
    """
    HITL Re-ranking system with implicit feedback
    Learns from user selections to improve future ranking
    
    When a user selects a result, that result gets boosted in future rankings
    for similar queries, implementing implicit relevance feedback
    """
    
    def __init__(self):
        """
        Initialize the HITL re-ranker
        Loads existing feedback data if available
        """
        self.feedback_file = Path(config.HITL_FEEDBACK_FILE)
        self.feedback_data = self._load_feedback()
        print("✓ Initialized HITL re-ranker")
    
    def _load_feedback(self) -> Dict[str, Any]:
        """
        Load existing feedback data from persistent storage
        
        Returns:
            Dictionary containing historical feedback data
        """
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
                    print(f"✓ Loaded {len(data.get('selections', {}))} feedback entries")
                    return data
            except Exception as e:
                print(f"⚠ Error loading feedback data: {e}")
                return {"selections": {}, "query_history": []}
        
        return {"selections": {}, "query_history": []}
    
    def _save_feedback(self) -> None:
        """
        Persist feedback data to disk
        Enables learning across application restarts
        """
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"⚠ Error saving feedback data: {e}")
    
    def _generate_doc_key(self, document: Dict[str, Any]) -> str:
        """
        Generate a unique key for a document
        Uses document ID or hash of text content
        
        Args:
            document: Document dictionary
        
        Returns:
            Unique document identifier
        """
        if "id" in document:
            return str(document["id"])
        
        # Fallback to hash of text
        return str(hash(document.get("text", "")))
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate simple word-based similarity between two queries
        Used to find relevant historical feedback for current query
        
        Args:
            query1: First query string
            query2: Second query string
        
        Returns:
            Similarity score between 0 and 1
        """
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-rank documents based on HITL feedback and original scores
        Applies boost to documents that have been selected by users for similar queries
        
        Args:
            query: Current search query
            documents: List of retrieved documents with scores
        
        Returns:
            Re-ranked list of documents with updated scores
        """
        if not documents:
            return documents
        
        # Create a mapping of document keys to boost factors
        boost_factors = defaultdict(float)
        
        # Find similar queries from history
        selections = self.feedback_data.get("selections", {})
        
        for hist_query, doc_selections in selections.items():
            similarity = self._calculate_similarity(query, hist_query)
            
            if similarity > 0.3:  # Threshold for query similarity
                # Apply boost based on query similarity and selection count
                for doc_key, selection_data in doc_selections.items():
                    selection_count = selection_data.get("count", 0)
                    recency_weight = selection_data.get("recency_weight", 1.0)
                    
                    # Boost = base_factor * similarity * selection_count * recency
                    boost = config.HITL_BOOST_FACTOR * similarity * selection_count * recency_weight
                    boost_factors[doc_key] = max(boost_factors[doc_key], boost)
        
        # Apply boosts to documents
        for doc in documents:
            doc_key = self._generate_doc_key(doc)
            
            if doc_key in boost_factors:
                # Apply multiplicative boost to original score
                original_score = doc.get("score", 0.0)
                boost = boost_factors[doc_key]
                
                # Store original score and boost for transparency
                doc["original_score"] = original_score
                doc["hitl_boost"] = boost
                doc["score"] = original_score * (1 + boost)
                doc["boosted"] = True
            else:
                doc["boosted"] = False
        
        # Sort by updated scores
        reranked = sorted(documents, key=lambda x: x.get("score", 0.0), reverse=True)
        
        return reranked
    
    def record_selection(self, query: str, selected_document: Dict[str, Any]) -> None:
        """
        Record when a user selects a document
        This is the implicit feedback that drives learning
        
        Args:
            query: The query that was used
            selected_document: The document that the user selected
        """
        doc_key = self._generate_doc_key(selected_document)
        
        # Initialize query entry if not exists
        if query not in self.feedback_data["selections"]:
            self.feedback_data["selections"][query] = {}
        
        # Update or create selection record
        if doc_key in self.feedback_data["selections"][query]:
            # Increment selection count
            self.feedback_data["selections"][query][doc_key]["count"] += 1
            self.feedback_data["selections"][query][doc_key]["last_selected"] = datetime.now().isoformat()
            # Reset recency weight on new selection
            self.feedback_data["selections"][query][doc_key]["recency_weight"] = 1.0
        else:
            # Create new selection record
            self.feedback_data["selections"][query][doc_key] = {
                "count": 1,
                "first_selected": datetime.now().isoformat(),
                "last_selected": datetime.now().isoformat(),
                "recency_weight": 1.0,
                "text_preview": selected_document.get("text", "")[:200]
            }
        
        # Add to query history
        self.feedback_data["query_history"].append({
            "query": query,
            "doc_key": doc_key,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save feedback
        self._save_feedback()
        
        print(f"✓ Recorded selection for query: '{query}'")
    
    def decay_old_selections(self) -> None:
        """
        Apply decay to older selections to prioritize recent feedback
        Should be called periodically to keep feedback fresh
        """
        for query, doc_selections in self.feedback_data["selections"].items():
            for doc_key, selection_data in doc_selections.items():
                # Apply decay to recency weight
                current_weight = selection_data.get("recency_weight", 1.0)
                selection_data["recency_weight"] = current_weight * config.HITL_DECAY_FACTOR
        
        self._save_feedback()
        print("✓ Applied decay to old selections")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the HITL feedback system
        
        Returns:
            Dictionary with feedback statistics
        """
        total_queries = len(self.feedback_data["selections"])
        total_selections = sum(
            len(docs) for docs in self.feedback_data["selections"].values()
        )
        total_interactions = len(self.feedback_data["query_history"])
        
        return {
            "unique_queries": total_queries,
            "unique_selections": total_selections,
            "total_interactions": total_interactions
        }
    
    def reset(self) -> None:
        """
        Reset all feedback data
        Use with caution - removes all learned preferences
        """
        self.feedback_data = {"selections": {}, "query_history": []}
        self._save_feedback()
        print("✓ Reset HITL feedback data")
