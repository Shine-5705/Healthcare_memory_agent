"""
Evidence Logger for Qdrant Retrieval Traceability

This module provides detailed logging and tracking of:
- What vectors were retrieved from Qdrant
- Similarity scores and distances
- How retrieval influenced AI decisions
- Complete audit trail for transparency

Required for hackathon: "Evidence-based outputs with traceability"
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class VectorRetrievalEvidence:
    """Evidence of a single vector retrieval from Qdrant"""
    collection_name: str
    query_type: str  # "text", "image", "audio", "hybrid"
    query_embedding_hash: str  # Hash of query vector for tracking
    retrieved_point_id: str
    similarity_score: float
    rank: int  # Position in results (1 = best match)
    payload_summary: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionInfluence:
    """How retrieved vectors influenced a decision"""
    decision_type: str  # "recommendation", "diagnosis", "similar_case"
    retrieved_evidence: List[VectorRetrievalEvidence]
    influence_score: float  # 0-1: How much this influenced decision
    reasoning: str  # Human-readable explanation
    confidence: float  # 0-1: Confidence in decision
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_type": self.decision_type,
            "retrieved_evidence": [e.to_dict() for e in self.retrieved_evidence],
            "influence_score": self.influence_score,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


class EvidenceLogger:
    """
    Centralized evidence logging for Qdrant retrievals
    
    Provides:
    - Detailed retrieval logging
    - Decision influence tracking
    - Audit trail generation
    - Evidence visualization data
    """
    
    def __init__(self):
        self.evidence_log: List[DecisionInfluence] = []
        
    def log_vector_retrieval(
        self,
        collection_name: str,
        query_type: str,
        query_embedding: List[float],
        search_results: List[Any],
        decision_type: str,
        reasoning: str,
        influence_score: float = 1.0,
        confidence: float = 0.8
    ) -> DecisionInfluence:
        """
        Log vector retrieval with full evidence
        
        Args:
            collection_name: Qdrant collection searched
            query_type: Type of query (text, image, audio)
            query_embedding: The query vector used
            search_results: Results from Qdrant search
            decision_type: What decision this supports
            reasoning: How retrieval influenced decision
            influence_score: 0-1 score of influence
            confidence: Confidence in decision
            
        Returns:
            DecisionInfluence object with full evidence
        """
        # Hash query vector for tracking
        query_hash = self._hash_vector(query_embedding)
        
        # Build evidence for each retrieved point
        retrieved_evidence = []
        for rank, result in enumerate(search_results, start=1):
            # Extract point data
            point_id = result.id if hasattr(result, 'id') else str(result.get('id', 'unknown'))
            score = result.score if hasattr(result, 'score') else result.get('score', 0.0)
            payload = result.payload if hasattr(result, 'payload') else result.get('payload', {})
            
            # Create payload summary (exclude large fields)
            payload_summary = self._summarize_payload(payload)
            
            evidence = VectorRetrievalEvidence(
                collection_name=collection_name,
                query_type=query_type,
                query_embedding_hash=query_hash,
                retrieved_point_id=point_id,
                similarity_score=round(float(score), 4),
                rank=rank,
                payload_summary=payload_summary,
                timestamp=datetime.now().isoformat()
            )
            
            retrieved_evidence.append(evidence)
        
        # Create decision influence record
        decision_influence = DecisionInfluence(
            decision_type=decision_type,
            retrieved_evidence=retrieved_evidence,
            influence_score=influence_score,
            reasoning=reasoning,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
        
        # Store in log
        self.evidence_log.append(decision_influence)
        
        # Print evidence summary
        self._print_evidence_summary(decision_influence)
        
        return decision_influence
    
    def _hash_vector(self, vector: List[float]) -> str:
        """Create hash of vector for tracking"""
        vector_str = json.dumps([round(v, 6) for v in vector[:10]])  # First 10 dims
        return hashlib.md5(vector_str.encode()).hexdigest()[:12]
    
    def _summarize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of payload (exclude embeddings, large fields)"""
        summary = {}
        exclude_keys = ['embedding', 'vector', 'image_data', 'audio_data']
        
        for key, value in payload.items():
            if key in exclude_keys:
                summary[key] = f"<{type(value).__name__}>"
            elif isinstance(value, (str, int, float, bool)):
                summary[key] = value
            elif isinstance(value, list) and len(value) < 10:
                summary[key] = value
            else:
                summary[key] = f"<{type(value).__name__}>"
        
        return summary
    
    def _print_evidence_summary(self, decision: DecisionInfluence):
        """Print human-readable evidence summary"""
        print(f"\n{'='*70}")
        print(f"📊 EVIDENCE-BASED DECISION: {decision.decision_type}")
        print(f"{'='*70}")
        
        print(f"\n🎯 Decision Reasoning:")
        print(f"   {decision.reasoning}")
        print(f"   Confidence: {decision.confidence:.1%}")
        print(f"   Influence Score: {decision.influence_score:.1%}")
        
        print(f"\n🔍 Retrieved from Qdrant: {len(decision.retrieved_evidence)} vectors")
        
        for evidence in decision.retrieved_evidence[:5]:  # Show top 5
            print(f"\n   [{evidence.rank}] Point ID: {evidence.retrieved_point_id}")
            print(f"       Collection: {evidence.collection_name}")
            print(f"       Similarity: {evidence.similarity_score:.4f}")
            print(f"       Query Type: {evidence.query_type}")
            
            # Show key payload fields
            if 'diagnosis' in evidence.payload_summary:
                print(f"       Diagnosis: {evidence.payload_summary['diagnosis']}")
            if 'condition' in evidence.payload_summary:
                print(f"       Condition: {evidence.payload_summary['condition']}")
            if 'treatment' in evidence.payload_summary:
                print(f"       Treatment: {evidence.payload_summary.get('treatment', 'N/A')}")
        
        print(f"\n{'='*70}\n")
    
    def get_evidence_for_decision(
        self,
        decision_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get evidence log entries
        
        Args:
            decision_type: Filter by decision type (optional)
            limit: Maximum number of entries
            
        Returns:
            List of decision influence records
        """
        filtered = self.evidence_log
        
        if decision_type:
            filtered = [d for d in filtered if d.decision_type == decision_type]
        
        return [d.to_dict() for d in filtered[-limit:]]
    
    def generate_evidence_report(
        self,
        patient_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive evidence report
        
        Args:
            patient_id: Filter by patient (optional)
            
        Returns:
            Detailed evidence report with statistics
        """
        # Calculate statistics
        total_retrievals = sum(len(d.retrieved_evidence) for d in self.evidence_log)
        avg_similarity = 0.0
        if total_retrievals > 0:
            all_scores = [
                e.similarity_score 
                for d in self.evidence_log 
                for e in d.retrieved_evidence
            ]
            avg_similarity = sum(all_scores) / len(all_scores)
        
        # Count by collection
        collection_counts = {}
        for decision in self.evidence_log:
            for evidence in decision.retrieved_evidence:
                collection = evidence.collection_name
                collection_counts[collection] = collection_counts.get(collection, 0) + 1
        
        # Count by decision type
        decision_counts = {}
        for decision in self.evidence_log:
            dtype = decision.decision_type
            decision_counts[dtype] = decision_counts.get(dtype, 0) + 1
        
        return {
            "summary": {
                "total_decisions": len(self.evidence_log),
                "total_vector_retrievals": total_retrievals,
                "average_similarity_score": round(avg_similarity, 4),
                "collections_used": len(collection_counts),
                "decision_types": len(decision_counts)
            },
            "collection_usage": collection_counts,
            "decision_type_breakdown": decision_counts,
            "recent_decisions": self.get_evidence_for_decision(limit=10),
            "generated_at": datetime.now().isoformat()
        }
    
    def export_evidence_trace(
        self,
        decision_index: int
    ) -> Dict[str, Any]:
        """
        Export detailed trace for a specific decision
        
        Args:
            decision_index: Index of decision to trace
            
        Returns:
            Complete evidence trace with visualization data
        """
        if decision_index >= len(self.evidence_log):
            return {"error": "Decision not found"}
        
        decision = self.evidence_log[decision_index]
        
        # Build visualization data
        nodes = []
        edges = []
        
        # Query node
        nodes.append({
            "id": "query",
            "label": f"Query ({decision.decision_type})",
            "type": "query",
            "data": {
                "decision_type": decision.decision_type,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence
            }
        })
        
        # Retrieved vector nodes
        for evidence in decision.retrieved_evidence:
            node_id = f"vector_{evidence.retrieved_point_id}"
            nodes.append({
                "id": node_id,
                "label": f"Rank {evidence.rank}\nScore: {evidence.similarity_score:.3f}",
                "type": "retrieved_vector",
                "data": {
                    "collection": evidence.collection_name,
                    "similarity": evidence.similarity_score,
                    "rank": evidence.rank,
                    "payload": evidence.payload_summary
                }
            })
            
            # Edge from query to vector
            edges.append({
                "source": "query",
                "target": node_id,
                "label": f"{evidence.similarity_score:.3f}",
                "weight": evidence.similarity_score
            })
        
        # Decision node
        nodes.append({
            "id": "decision",
            "label": f"Decision\n({decision.confidence:.1%} confidence)",
            "type": "decision",
            "data": {
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "influence_score": decision.influence_score
            }
        })
        
        # Edges from vectors to decision
        for evidence in decision.retrieved_evidence:
            node_id = f"vector_{evidence.retrieved_point_id}"
            edges.append({
                "source": node_id,
                "target": "decision",
                "label": f"influence: {decision.influence_score:.2f}",
                "weight": decision.influence_score
            })
        
        return {
            "decision_info": decision.to_dict(),
            "visualization": {
                "nodes": nodes,
                "edges": edges
            },
            "trace_summary": {
                "collections_searched": list(set(e.collection_name for e in decision.retrieved_evidence)),
                "vectors_retrieved": len(decision.retrieved_evidence),
                "avg_similarity": round(
                    sum(e.similarity_score for e in decision.retrieved_evidence) / len(decision.retrieved_evidence),
                    4
                ) if decision.retrieved_evidence else 0,
                "top_similarity": max(e.similarity_score for e in decision.retrieved_evidence) if decision.retrieved_evidence else 0,
                "influence_on_decision": decision.influence_score
            }
        }
    
    def clear_log(self):
        """Clear evidence log"""
        self.evidence_log = []
        print("✅ Evidence log cleared")


# Singleton instance
_evidence_logger = None

def get_evidence_logger() -> EvidenceLogger:
    """Get or create singleton evidence logger"""
    global _evidence_logger
    if _evidence_logger is None:
        _evidence_logger = EvidenceLogger()
    return _evidence_logger
