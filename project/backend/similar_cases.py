"""
Similar Patient Cases Retrieval System using Qdrant Hybrid Search

This module provides intelligent case-based reasoning by finding similar historical patient cases
to support clinical decision-making. Uses hybrid search across multiple dimensions:
- Conversation history and symptoms (semantic similarity)
- Diagnoses and conditions (exact matching + semantic)
- Vitals patterns (numerical similarity)
- Treatment outcomes and medications

Features:
- Multi-dimensional similarity scoring
- Privacy-preserving case anonymization
- Evidence-based historical data retrieval
- Comparable conditions and vitals analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range
from sentence_transformers import SentenceTransformer
import numpy as np

# Import existing Qdrant systems for data retrieval
from patient_memory import PatientMemorySystem
from vitals_tracker import VitalsTracker
from medical_knowledge_base import MedicalKnowledgeBase
from ai_recommendations import RecommendationEngine

# Import evidence logger for traceability
try:
    from evidence_logger import get_evidence_logger
    EVIDENCE_LOGGER_AVAILABLE = True
except ImportError:
    EVIDENCE_LOGGER_AVAILABLE = False


class SimilarCasesEngine:
    """
    Intelligent similar patient case retrieval system using Qdrant hybrid search
    
    Finds historically similar cases to support clinical decision-making by analyzing:
    - Patient symptoms and conversation patterns
    - Medical conditions and diagnoses
    - Vitals trends and measurements
    - Treatment responses and outcomes
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure one instance"""
        if cls._instance is None:
            cls._instance = super(SimilarCasesEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the similar cases engine with Qdrant vector database"""
        if self._initialized:
            return
            
        print("🔍 Initializing Similar Cases Engine...")
        
        # Initialize Qdrant client (in-memory for development)
        self.client = QdrantClient(":memory:")
        
        # Collection name for similar cases index
        self.collection_name = "similar_cases"
        
        # Initialize embedding model (same as other systems for consistency)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension of all-MiniLM-L6-v2
        
        # Create collection for case indexing
        self._create_collection()
        
        # Initialize dependent systems for data retrieval
        self.patient_memory = PatientMemorySystem()
        self.vitals_tracker = VitalsTracker()
        self.medical_kb = MedicalKnowledgeBase()
        self.recommendation_engine = RecommendationEngine()
        
        # Case similarity weights for scoring
        self.similarity_weights = {
            'symptoms': 0.30,      # 30% weight for symptom similarity
            'conditions': 0.25,    # 25% weight for condition matching
            'vitals': 0.20,        # 20% weight for vitals patterns
            'demographics': 0.10,  # 10% weight for age/gender similarity
            'treatments': 0.15,    # 15% weight for treatment response
        }
        
        self._initialized = True
        print("✅ Similar Cases Engine initialized")
    
    def _create_collection(self):
        """Create Qdrant collection for case indexing"""
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(collection_name=self.collection_name)
            except:
                pass
            
            # Create new collection with vector configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            print(f"📦 Created collection: {self.collection_name}")
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            raise
    
    def _create_case_profile(
        self,
        patient_id: str,
        symptoms: List[str],
        conditions: List[str],
        vitals_summary: Dict[str, Any],
        demographics: Dict[str, Any],
        treatments: List[str],
        outcome: Optional[str] = None
    ) -> str:
        """
        Create a comprehensive text profile for case embedding
        
        Args:
            patient_id: Patient identifier
            symptoms: List of reported symptoms
            conditions: List of diagnosed conditions
            vitals_summary: Summary of vital signs
            demographics: Age, gender, etc.
            treatments: Medications and interventions
            outcome: Treatment outcome description
            
        Returns:
            Combined text profile for embedding
        """
        profile_parts = []
        
        # Add demographics context
        if demographics:
            age = demographics.get('age', 'unknown')
            gender = demographics.get('gender', 'unknown')
            profile_parts.append(f"Patient demographics: {age} year old {gender}")
        
        # Add symptoms
        if symptoms:
            symptoms_text = ", ".join(symptoms)
            profile_parts.append(f"Presenting symptoms: {symptoms_text}")
        
        # Add conditions
        if conditions:
            conditions_text = ", ".join(conditions)
            profile_parts.append(f"Diagnosed conditions: {conditions_text}")
        
        # Add vitals summary
        if vitals_summary:
            vitals_text = []
            for vital, value in vitals_summary.items():
                vitals_text.append(f"{vital}: {value}")
            profile_parts.append(f"Vital signs: {', '.join(vitals_text)}")
        
        # Add treatments
        if treatments:
            treatments_text = ", ".join(treatments)
            profile_parts.append(f"Treatments: {treatments_text}")
        
        # Add outcome
        if outcome:
            profile_parts.append(f"Outcome: {outcome}")
        
        return " | ".join(profile_parts)
    
    def index_patient_case(
        self,
        patient_id: str,
        case_date: str,
        symptoms: List[str],
        conditions: List[str],
        vitals_summary: Dict[str, float],
        demographics: Dict[str, Any],
        treatments: List[str] = None,
        outcome: Optional[str] = None,
        case_notes: Optional[str] = None
    ) -> str:
        """
        Index a patient case for future similarity searches
        
        Args:
            patient_id: Patient identifier (will be anonymized in storage)
            case_date: Date of case (YYYY-MM-DD format)
            symptoms: List of symptoms reported
            conditions: List of diagnosed conditions
            vitals_summary: Dict of vitals (e.g., {'blood_pressure': 140, 'heart_rate': 85})
            demographics: Age, gender, etc.
            treatments: Medications and interventions used
            outcome: Treatment outcome description
            case_notes: Additional clinical notes
            
        Returns:
            Case ID for the indexed case
        """
        try:
            # Create case profile for embedding
            profile_text = self._create_case_profile(
                patient_id=patient_id,
                symptoms=symptoms,
                conditions=conditions,
                vitals_summary=vitals_summary,
                demographics=demographics,
                treatments=treatments or [],
                outcome=outcome
            )
            
            # Generate embedding
            embedding = self.embedding_model.encode(profile_text).tolist()
            
            # Create case ID
            case_id = f"case_{patient_id}_{case_date}_{datetime.now().timestamp()}"
            
            # Prepare metadata (anonymized for privacy)
            metadata = {
                'case_id': case_id,
                'anonymized_patient_id': f"patient_{hash(patient_id) % 10000}",  # Hash for privacy
                'case_date': case_date,
                'symptoms': symptoms,
                'conditions': conditions,
                'vitals_summary': vitals_summary,
                'age_range': self._get_age_range(demographics.get('age')),
                'gender': demographics.get('gender', 'unknown'),
                'treatments': treatments or [],
                'outcome': outcome or "unknown",
                'case_notes': case_notes or "",
                'indexed_at': datetime.now().isoformat()
            }
            
            # Store in Qdrant
            point = PointStruct(
                id=hash(case_id) % (2**63),  # Convert to positive integer
                vector=embedding,
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return case_id
            
        except Exception as e:
            print(f"❌ Error indexing case: {e}")
            raise
    
    def _get_age_range(self, age: Optional[int]) -> str:
        """Categorize age into ranges for privacy and matching"""
        if age is None:
            return "unknown"
        if age < 18:
            return "pediatric"
        elif age < 35:
            return "young_adult"
        elif age < 50:
            return "adult"
        elif age < 65:
            return "middle_age"
        else:
            return "senior"
    
    def _extract_patient_profile(self, patient_id: str) -> Dict[str, Any]:
        """
        Extract comprehensive patient profile from existing systems
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Dictionary with symptoms, conditions, vitals, demographics
        """
        profile = {
            'symptoms': [],
            'conditions': [],
            'vitals_summary': {},
            'demographics': {},
            'treatments': []
        }
        
        try:
            # Extract symptoms from conversation history
            conversations = self.patient_memory.get_patient_history(
                patient_id=patient_id,
                limit=20  # Look at recent conversations
            )
            
            symptom_keywords = [
                'pain', 'ache', 'fatigue', 'tired', 'dizzy', 'nausea', 'cough',
                'fever', 'headache', 'breathless', 'chest pain', 'anxiety',
                'depressed', 'insomnia', 'swelling', 'rash', 'itch', 'vomit'
            ]
            
            for conv in conversations:
                user_msg = conv.get('user_message', '').lower()
                for keyword in symptom_keywords:
                    if keyword in user_msg:
                        if keyword not in profile['symptoms']:
                            profile['symptoms'].append(keyword)
            
            # Extract vitals summary (average of last 30 days)
            vitals_data = self.vitals_tracker.get_vitals_history(
                patient_id=patient_id,
                days=30
            )
            
            if vitals_data:
                # Calculate averages for each vital type
                vitals_by_type = {}
                for reading in vitals_data:
                    for vital_name, vital_value in reading.items():
                        if vital_name not in ['patient_id', 'timestamp', 'recorded_at']:
                            if vital_name not in vitals_by_type:
                                vitals_by_type[vital_name] = []
                            vitals_by_type[vital_name].append(vital_value)
                
                # Calculate averages
                for vital_name, values in vitals_by_type.items():
                    if values:
                        profile['vitals_summary'][vital_name] = round(np.mean(values), 2)
            
            # Extract conditions from recommendations (if available)
            try:
                rec_history = self.recommendation_engine.get_recommendation_history(
                    patient_id=patient_id,
                    limit=5
                )
                
                for rec in rec_history:
                    for recommendation in rec.get('recommendations', []):
                        condition = recommendation.get('condition')
                        if condition and condition not in profile['conditions']:
                            profile['conditions'].append(condition)
            except:
                pass  # Recommendations may not exist for all patients
            
        except Exception as e:
            print(f"⚠️ Error extracting patient profile: {e}")
        
        return profile
    
    def _calculate_similarity_score(
        self,
        query_profile: Dict[str, Any],
        case_metadata: Dict[str, Any],
        vector_similarity: float
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate multi-dimensional similarity score
        
        Args:
            query_profile: Current patient's profile
            case_metadata: Historical case metadata
            vector_similarity: Cosine similarity from vector search
            
        Returns:
            Tuple of (total_score, component_scores)
        """
        scores = {
            'symptoms': 0.0,
            'conditions': 0.0,
            'vitals': 0.0,
            'demographics': 0.0,
            'treatments': 0.0,
            'vector': vector_similarity
        }
        
        # Symptom similarity (Jaccard index)
        query_symptoms = set(query_profile.get('symptoms', []))
        case_symptoms = set(case_metadata.get('symptoms', []))
        if query_symptoms or case_symptoms:
            intersection = len(query_symptoms & case_symptoms)
            union = len(query_symptoms | case_symptoms)
            scores['symptoms'] = intersection / union if union > 0 else 0.0
        
        # Condition similarity (Jaccard index)
        query_conditions = set(query_profile.get('conditions', []))
        case_conditions = set(case_metadata.get('conditions', []))
        if query_conditions or case_conditions:
            intersection = len(query_conditions & case_conditions)
            union = len(query_conditions | case_conditions)
            scores['conditions'] = intersection / union if union > 0 else 0.0
        
        # Vitals similarity (normalized distance)
        query_vitals = query_profile.get('vitals_summary', {})
        case_vitals = case_metadata.get('vitals_summary', {})
        
        if query_vitals and case_vitals:
            # Find common vitals
            common_vitals = set(query_vitals.keys()) & set(case_vitals.keys())
            if common_vitals:
                differences = []
                for vital in common_vitals:
                    # Normalize by typical ranges
                    vital_ranges = {
                        'systolic_bp': 60, 'diastolic_bp': 40, 'heart_rate': 60,
                        'blood_glucose': 100, 'oxygen_saturation': 10,
                        'temperature': 3, 'respiratory_rate': 10, 'weight': 50
                    }
                    range_val = vital_ranges.get(vital, 50)
                    diff = abs(query_vitals[vital] - case_vitals[vital]) / range_val
                    differences.append(min(diff, 1.0))  # Cap at 1.0
                
                scores['vitals'] = 1.0 - np.mean(differences)
        
        # Demographics similarity (age range + gender)
        demo_score = 0.0
        query_age_range = self._get_age_range(query_profile.get('demographics', {}).get('age'))
        case_age_range = case_metadata.get('age_range', 'unknown')
        if query_age_range == case_age_range:
            demo_score += 0.7
        
        query_gender = query_profile.get('demographics', {}).get('gender', 'unknown')
        case_gender = case_metadata.get('gender', 'unknown')
        if query_gender == case_gender:
            demo_score += 0.3
        
        scores['demographics'] = demo_score
        
        # Treatment similarity (Jaccard index)
        query_treatments = set(query_profile.get('treatments', []))
        case_treatments = set(case_metadata.get('treatments', []))
        if query_treatments or case_treatments:
            intersection = len(query_treatments & case_treatments)
            union = len(query_treatments | case_treatments)
            scores['treatments'] = intersection / union if union > 0 else 0.0
        
        # Calculate weighted total score
        total_score = (
            scores['symptoms'] * self.similarity_weights['symptoms'] +
            scores['conditions'] * self.similarity_weights['conditions'] +
            scores['vitals'] * self.similarity_weights['vitals'] +
            scores['demographics'] * self.similarity_weights['demographics'] +
            scores['treatments'] * self.similarity_weights['treatments'] +
            vector_similarity * 0.3  # Base semantic similarity weight
        )
        
        # Normalize to 0-1 range
        total_score = min(max(total_score, 0.0), 1.0)
        
        return total_score, scores
    
    def find_similar_cases(
        self,
        patient_id: str,
        top_k: int = 5,
        min_similarity: float = 0.3,
        include_demographics: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical patient cases for clinical decision support
        
        Args:
            patient_id: Current patient identifier
            top_k: Number of similar cases to return (default: 5)
            min_similarity: Minimum similarity threshold (0-1, default: 0.3)
            include_demographics: Whether to include demographic factors in matching
            
        Returns:
            List of similar cases with similarity scores and shared attributes
            
        Example:
            {
                'case_id': 'case_patient_123_2025-12-15_...',
                'similarity_score': 0.87,
                'similarity_breakdown': {
                    'symptoms': 0.75,
                    'conditions': 0.90,
                    'vitals': 0.85,
                    'demographics': 1.0,
                    'treatments': 0.60
                },
                'shared_symptoms': ['chest pain', 'fatigue'],
                'shared_conditions': ['Hypertension', 'Type 2 Diabetes'],
                'case_date': '2025-12-15',
                'age_range': 'adult',
                'gender': 'male',
                'outcome': 'improved with medication',
                'treatments': ['Metformin', 'Lisinopril'],
                'vitals_summary': {'systolic_bp': 145, 'heart_rate': 82},
                'case_notes': 'Patient responded well to combination therapy'
            }
        """
        try:
            # Extract current patient profile
            query_profile = self._extract_patient_profile(patient_id)
            
            # Create query text from profile
            query_text = self._create_case_profile(
                patient_id=patient_id,
                symptoms=query_profile['symptoms'],
                conditions=query_profile['conditions'],
                vitals_summary=query_profile['vitals_summary'],
                demographics=query_profile['demographics'],
                treatments=query_profile['treatments']
            )
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # Search for similar cases (get more than needed for filtering)
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k * 3  # Get extra for filtering
            ).points
            
            # Calculate detailed similarity scores and filter
            similar_cases = []
            
            for result in search_results:
                case_metadata = result.payload
                vector_similarity = result.score
                
                # Calculate multi-dimensional similarity
                total_score, component_scores = self._calculate_similarity_score(
                    query_profile=query_profile,
                    case_metadata=case_metadata,
                    vector_similarity=vector_similarity
                )
                
                # Filter by minimum similarity
                if total_score < min_similarity:
                    continue
                
                # Calculate shared attributes
                shared_symptoms = list(
                    set(query_profile['symptoms']) & set(case_metadata.get('symptoms', []))
                )
                shared_conditions = list(
                    set(query_profile['conditions']) & set(case_metadata.get('conditions', []))
                )
                
                # Build similar case object
                similar_case = {
                    'case_id': case_metadata['case_id'],
                    'similarity_score': round(total_score, 3),
                    'similarity_breakdown': {
                        key: round(val, 3) for key, val in component_scores.items()
                    },
                    'shared_symptoms': shared_symptoms,
                    'shared_conditions': shared_conditions,
                    'case_date': case_metadata['case_date'],
                    'age_range': case_metadata.get('age_range', 'unknown'),
                    'gender': case_metadata.get('gender', 'unknown'),
                    'outcome': case_metadata.get('outcome', 'unknown'),
                    'treatments': case_metadata.get('treatments', []),
                    'vitals_summary': case_metadata.get('vitals_summary', {}),
                    'case_notes': case_metadata.get('case_notes', ''),
                    'anonymized_patient_id': case_metadata.get('anonymized_patient_id', 'unknown')
                }
                
                similar_cases.append(similar_case)
            
            # Sort by similarity score (descending)
            similar_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # LOG EVIDENCE: Track similar cases retrieval
            if EVIDENCE_LOGGER_AVAILABLE and similar_cases:
                evidence_logger = get_evidence_logger()
                reasoning = (
                    f"Found {len(similar_cases)} similar patient cases using hybrid search. "
                    f"Top match has {similar_cases[0]['similarity_score']:.2f} similarity score. "
                    f"Shared conditions: {', '.join(similar_cases[0]['shared_conditions'][:3]) if similar_cases[0]['shared_conditions'] else 'none'}. "
                    f"These cases provide evidence-based treatment insights and outcome predictions."
                )
                evidence_logger.log_vector_retrieval(
                    collection_name=self.collection_name,
                    query_type="text",
                    query_embedding=query_embedding,
                    search_results=search_results[:top_k],
                    decision_type="similar_cases_search",
                    reasoning=reasoning,
                    influence_score=0.90,
                    confidence=similar_cases[0]['similarity_score'] if similar_cases else 0.5
                )
            
            # Return top k cases
            return similar_cases[:top_k]
            
        except Exception as e:
            print(f"❌ Error finding similar cases: {e}")
            raise
    
    def get_case_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about indexed cases
        
        Returns:
            Dictionary with case database statistics
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            
            # Get all points to analyze
            all_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # High limit to get all cases
            )[0]
            
            # Analyze conditions and symptoms distribution
            all_conditions = []
            all_symptoms = []
            age_ranges = []
            outcomes = []
            
            for point in all_points:
                payload = point.payload
                all_conditions.extend(payload.get('conditions', []))
                all_symptoms.extend(payload.get('symptoms', []))
                age_ranges.append(payload.get('age_range', 'unknown'))
                outcomes.append(payload.get('outcome', 'unknown'))
            
            # Count frequencies
            from collections import Counter
            condition_counts = Counter(all_conditions)
            symptom_counts = Counter(all_symptoms)
            age_range_counts = Counter(age_ranges)
            outcome_counts = Counter(outcomes)
            
            return {
                'total_cases': collection_info.points_count,
                'most_common_conditions': dict(condition_counts.most_common(10)),
                'most_common_symptoms': dict(symptom_counts.most_common(10)),
                'age_distribution': dict(age_range_counts),
                'outcome_distribution': dict(outcome_counts),
                'collection_size_mb': collection_info.points_count * self.embedding_dim * 4 / (1024 * 1024)
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {
                'error': str(e),
                'total_cases': 0,
                'most_common_conditions': {},
                'most_common_symptoms': {},
                'age_distribution': {},
                'outcome_distribution': {},
                'collection_size_mb': 0
            }
    
    def delete_patient_cases(self, patient_id: str) -> int:
        """
        Delete all cases for a patient (GDPR compliance)
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Number of cases deleted
        """
        try:
            # Find all cases for this patient
            anonymized_id = f"patient_{hash(patient_id) % 10000}"
            
            # Get all points
            all_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000
            )[0]
            
            # Find matching case IDs
            case_ids_to_delete = []
            for point in all_points:
                if point.payload.get('anonymized_patient_id') == anonymized_id:
                    case_ids_to_delete.append(point.id)
            
            # Delete cases
            if case_ids_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=case_ids_to_delete
                )
            
            return len(case_ids_to_delete)
            
        except Exception as e:
            print(f"❌ Error deleting patient cases: {e}")
            raise


# Singleton instance
_similar_cases_engine = None

def get_similar_cases_engine() -> SimilarCasesEngine:
    """Get or create singleton instance of SimilarCasesEngine"""
    global _similar_cases_engine
    if _similar_cases_engine is None:
        _similar_cases_engine = SimilarCasesEngine()
    return _similar_cases_engine
