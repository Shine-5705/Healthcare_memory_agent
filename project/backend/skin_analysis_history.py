"""
Skin Analysis History Storage using Qdrant with MULTIMODAL Embeddings

This module stores historical skin analysis results with BOTH image and text embeddings for similarity search.
Supports pattern matching and diagnosis assistance by finding similar previous cases based on:
- Visual similarity (CLIP image embeddings) - 512 dimensions
- Diagnosis text similarity (text embeddings) - 384 dimensions
- Severity levels
- Skin condition categories
- Treatment recommendations

Features:
- TRUE MULTIMODAL: Image vectors stored in Qdrant (not just text descriptions)
- Image-to-image search (find visually similar skin conditions)
- Text-to-image search (cross-modal retrieval)
- Semantic search across historical diagnoses
- Similar case retrieval for pattern recognition
- Privacy-preserving (embeddings only, optional raw image storage)
- GDPR-compliant deletion
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import json
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, NamedVector
from sentence_transformers import SentenceTransformer
import hashlib
from PIL import Image
import os

# Import multimodal embedding generator
try:
    from multimodal_embeddings import get_embedding_generator
    MULTIMODAL_AVAILABLE = True
    print("✅ Multimodal embeddings available")
except ImportError as e:
    print(f"⚠️ Multimodal embeddings not available: {e}")
    MULTIMODAL_AVAILABLE = False


class SkinAnalysisHistory:
    """
    Manages historical skin analysis results using Qdrant vector database
    
    Stores diagnosis results with semantic embeddings to enable:
    - Finding similar historical cases
    - Pattern recognition across skin conditions
    - Evidence-based diagnosis support
    - Treatment outcome tracking
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure one instance"""
        if cls._instance is None:
            cls._instance = super(SkinAnalysisHistory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the skin analysis history storage"""
        if self._initialized:
            return
            
        print("🔬 Initializing Skin Analysis History...")
        
        # Initialize Qdrant client (in-memory for development)
        self.client = QdrantClient(":memory:")
        
        # Collection name for skin analysis history
        self.collection_name = "skin_analysis_history"
        
        # Initialize embedding model (same as other systems)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384
        
        # Create collection
        self._create_collection()
        
        # Skin condition categories for classification
        self.condition_categories = {
            'acne': ['acne', 'pimple', 'comedone', 'blackhead', 'whitehead'],
            'eczema': ['eczema', 'dermatitis', 'atopic', 'dry skin'],
            'psoriasis': ['psoriasis', 'plaque', 'scaly patches'],
            'rosacea': ['rosacea', 'flushing', 'facial redness'],
            'fungal': ['fungal', 'tinea', 'ringworm', 'candida', 'yeast'],
            'bacterial': ['bacterial', 'cellulitis', 'impetigo', 'folliculitis'],
            'viral': ['viral', 'warts', 'herpes', 'shingles'],
            'allergic': ['allergic', 'contact dermatitis', 'hives', 'urticaria'],
            'pigmentation': ['hyperpigmentation', 'melasma', 'vitiligo', 'age spots'],
            'aging': ['wrinkles', 'fine lines', 'sagging', 'aging'],
            'sun_damage': ['sun damage', 'sunburn', 'photoaging', 'solar'],
            'other': []
        }
        
        self._initialized = True
        print("✅ Skin Analysis History initialized")
    
    def _create_collection(self):
        """Create Qdrant collection for MULTIMODAL skin analysis history"""
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(collection_name=self.collection_name)
            except:
                pass
            
            # Create new collection with NAMED VECTORS for multimodal storage
            vectors_config = {
                "text": VectorParams(
                    size=self.embedding_dim,  # 384 for all-MiniLM-L6-v2
                    distance=Distance.COSINE
                )
            }
            
            # Add image vector if CLIP is available
            if MULTIMODAL_AVAILABLE:
                vectors_config["image"] = VectorParams(
                    size=512,  # CLIP ViT-B/32 dimension
                    distance=Distance.COSINE
                )
                print("📸 Multimodal collection: Image + Text vectors enabled")
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config
            )
            print(f"📦 Created multimodal collection: {self.collection_name}")
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            raise
    
    def _categorize_condition(self, diagnosis: str) -> str:
        """
        Categorize skin condition based on diagnosis text
        
        Args:
            diagnosis: Diagnosis text
            
        Returns:
            Category name
        """
        diagnosis_lower = diagnosis.lower()
        
        for category, keywords in self.condition_categories.items():
            for keyword in keywords:
                if keyword in diagnosis_lower:
                    return category
        
        return 'other'
    
    def _create_analysis_text(
        self,
        diagnosis: str,
        severity: str,
        recommendations: List[str],
        affected_areas: List[str] = None
    ) -> str:
        """
        Create comprehensive text for embedding
        
        Args:
            diagnosis: Primary diagnosis
            severity: Severity level
            recommendations: Treatment recommendations
            affected_areas: Affected body areas
            
        Returns:
            Combined text for embedding
        """
        text_parts = []
        
        # Add diagnosis
        text_parts.append(f"Diagnosis: {diagnosis}")
        
        # Add severity
        text_parts.append(f"Severity: {severity}")
        
        # Add affected areas
        if affected_areas:
            text_parts.append(f"Areas: {', '.join(affected_areas)}")
        
        # Add recommendations
        if recommendations:
            text_parts.append(f"Recommendations: {' | '.join(recommendations)}")
        
        return " | ".join(text_parts)
    
    def store_analysis(
        self,
        patient_id: str,
        diagnosis: str,
        severity: str,
        confidence: float,
        recommendations: List[str],
        image_data: Optional[Union[Image.Image, str, bytes]] = None,
        affected_areas: List[str] = None,
        additional_observations: str = None,
        follow_up_needed: bool = False,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Store skin analysis result in history with MULTIMODAL embeddings
        
        Args:
            patient_id: Patient identifier (will be anonymized)
            diagnosis: Primary diagnosis text
            severity: Severity level (mild/moderate/severe)
            confidence: Diagnosis confidence (0-1)
            recommendations: List of treatment recommendations
            image_data: Image data (PIL Image, base64 string, or bytes) - NEW!
            affected_areas: Body areas affected
            additional_observations: Extra clinical notes
            follow_up_needed: Whether follow-up is required
            timestamp: Analysis timestamp (defaults to now)
            
        Returns:
            Analysis case ID
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Create text for embedding
            analysis_text = self._create_analysis_text(
                diagnosis=diagnosis,
                severity=severity,
                recommendations=recommendations,
                affected_areas=affected_areas or []
            )
            
            # Generate TEXT embedding
            text_embedding = self.embedding_model.encode(analysis_text).tolist()
            
            # Generate IMAGE embedding if available
            image_embedding = None
            has_image = False
            if image_data is not None and MULTIMODAL_AVAILABLE:
                try:
                    embedding_gen = get_embedding_generator()
                    image_embedding = embedding_gen.generate_image_embedding(image_data)
                    if image_embedding is not None:
                        image_embedding = image_embedding.tolist()
                        has_image = True
                        print("📸 Generated image embedding (512-dim CLIP vector)")
                except Exception as e:
                    print(f"⚠️ Failed to generate image embedding: {e}")
            
            # Create unique case ID
            case_id = f"skin_analysis_{uuid.uuid4().hex[:12]}"
            
            # Categorize condition
            category = self._categorize_condition(diagnosis)
            
            # Create anonymized patient ID
            anonymized_patient_id = f"patient_{hashlib.sha256(patient_id.encode()).hexdigest()[:12]}"
            
            # Prepare metadata
            metadata = {
                'case_id': case_id,
                'anonymized_patient_id': anonymized_patient_id,
                'diagnosis': diagnosis,
                'severity': severity,
                'confidence': confidence,
                'recommendations': recommendations,
                'affected_areas': affected_areas or [],
                'category': category,
                'additional_observations': additional_observations or '',
                'follow_up_needed': follow_up_needed,
                'timestamp': timestamp.isoformat(),
                'indexed_at': datetime.now().isoformat(),
                'has_image_embedding': has_image  # Track if image vector exists
            }
            
            # Store in Qdrant with MULTIMODAL vectors
            vectors_dict = {"text": text_embedding}
            if has_image and image_embedding is not None:
                vectors_dict["image"] = image_embedding
            
            point = PointStruct(
                id=hash(case_id) % (2**63),
                vector=vectors_dict,
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"✅ Stored skin analysis: {case_id} - {diagnosis} ({severity})")
            return case_id
            
        except Exception as e:
            print(f"❌ Error storing analysis: {e}")
            raise
    
    def find_similar_cases(
        self,
        diagnosis: str,
        severity: str = None,
        recommendations: List[str] = None,
        affected_areas: List[str] = None,
        top_k: int = 5,
        min_confidence: float = 0.0,
        category_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical skin analysis cases
        
        Args:
            diagnosis: Current diagnosis text
            severity: Severity level (optional filter)
            recommendations: Current recommendations (optional)
            affected_areas: Affected areas (optional)
            top_k: Number of similar cases to return
            min_confidence: Minimum diagnosis confidence filter
            category_filter: Filter by condition category
            
        Returns:
            List of similar cases with similarity scores
            
        Example:
            {
                'case_id': 'skin_analysis_abc123',
                'similarity_score': 0.89,
                'diagnosis': 'Moderate acne vulgaris',
                'severity': 'moderate',
                'confidence': 0.85,
                'recommendations': ['Benzoyl peroxide', 'Gentle cleanser'],
                'affected_areas': ['face', 'forehead'],
                'category': 'acne',
                'additional_observations': 'Inflammatory papules present',
                'follow_up_needed': True,
                'timestamp': '2025-12-15T10:30:00',
                'pattern_match': 'Similar inflammatory response'
            }
        """
        try:
            # Create query text
            query_text = self._create_analysis_text(
                diagnosis=diagnosis,
                severity=severity or 'unknown',
                recommendations=recommendations or [],
                affected_areas=affected_areas or []
            )
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_text).tolist()
            
            # Search for similar cases
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k * 2  # Get extra for filtering
            ).points
            
            # Process and filter results
            similar_cases = []
            
            for result in search_results:
                case_metadata = result.payload
                similarity_score = result.score
                
                # Apply confidence filter
                if case_metadata.get('confidence', 0) < min_confidence:
                    continue
                
                # Apply category filter
                if category_filter and case_metadata.get('category') != category_filter:
                    continue
                
                # Identify pattern matches
                pattern_match = self._identify_pattern_match(
                    query_diagnosis=diagnosis,
                    case_diagnosis=case_metadata['diagnosis'],
                    similarity_score=similarity_score
                )
                
                # Build similar case object
                similar_case = {
                    'case_id': case_metadata['case_id'],
                    'similarity_score': round(similarity_score, 3),
                    'diagnosis': case_metadata['diagnosis'],
                    'severity': case_metadata['severity'],
                    'confidence': case_metadata['confidence'],
                    'recommendations': case_metadata.get('recommendations', []),
                    'affected_areas': case_metadata.get('affected_areas', []),
                    'category': case_metadata.get('category', 'other'),
                    'additional_observations': case_metadata.get('additional_observations', ''),
                    'follow_up_needed': case_metadata.get('follow_up_needed', False),
                    'timestamp': case_metadata['timestamp'],
                    'pattern_match': pattern_match,
                    'anonymized_patient_id': case_metadata.get('anonymized_patient_id', 'unknown')
                }
                
                similar_cases.append(similar_case)
            
            # Sort by similarity score
            similar_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top k
            return similar_cases[:top_k]
            
        except Exception as e:
            print(f"❌ Error finding similar cases: {e}")
            return []
    
    def _identify_pattern_match(
        self,
        query_diagnosis: str,
        case_diagnosis: str,
        similarity_score: float
    ) -> str:
        """
        Identify specific pattern matches between cases
        
        Args:
            query_diagnosis: Current diagnosis
            case_diagnosis: Historical case diagnosis
            similarity_score: Similarity score
            
        Returns:
            Pattern match description
        """
        query_lower = query_diagnosis.lower()
        case_lower = case_diagnosis.lower()
        
        # Check for exact condition match
        for category, keywords in self.condition_categories.items():
            if any(kw in query_lower for kw in keywords) and any(kw in case_lower for kw in keywords):
                if similarity_score > 0.8:
                    return f"Highly similar {category} presentation"
                elif similarity_score > 0.6:
                    return f"Similar {category} pattern"
        
        # Check for severity match
        severity_terms = ['mild', 'moderate', 'severe', 'acute', 'chronic']
        for term in severity_terms:
            if term in query_lower and term in case_lower:
                return f"Matching {term} severity level"
        
        # Check for location match
        locations = ['face', 'body', 'hands', 'feet', 'scalp', 'arms', 'legs']
        for loc in locations:
            if loc in query_lower and loc in case_lower:
                return f"Similar location ({loc})"
        
        # Generic similarity
        if similarity_score > 0.7:
            return "Similar clinical presentation"
        elif similarity_score > 0.5:
            return "Moderate similarity in symptoms"
        else:
            return "Some overlapping features"
    
    def get_patient_history(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all historical analyses for a patient
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of records
            
        Returns:
            List of patient's historical analyses
        """
        try:
            # Create anonymized patient ID
            anonymized_patient_id = f"patient_{hashlib.sha256(patient_id.encode()).hexdigest()[:12]}"
            
            # Get all points
            all_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000
            )[0]
            
            # Filter by patient
            patient_cases = []
            for point in all_points:
                if point.payload.get('anonymized_patient_id') == anonymized_patient_id:
                    case = {
                        'case_id': point.payload['case_id'],
                        'diagnosis': point.payload['diagnosis'],
                        'severity': point.payload['severity'],
                        'confidence': point.payload['confidence'],
                        'recommendations': point.payload.get('recommendations', []),
                        'affected_areas': point.payload.get('affected_areas', []),
                        'category': point.payload.get('category', 'other'),
                        'timestamp': point.payload['timestamp'],
                        'follow_up_needed': point.payload.get('follow_up_needed', False)
                    }
                    patient_cases.append(case)
            
            # Sort by timestamp (most recent first)
            patient_cases.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return patient_cases[:limit]
            
        except Exception as e:
            print(f"❌ Error getting patient history: {e}")
            return []
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored skin analyses
        
        Returns:
            Statistics by category, severity, etc.
        """
        try:
            # Get all points
            all_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000
            )[0]
            
            # Collect statistics
            category_counts = {}
            severity_counts = {}
            follow_up_counts = {'needed': 0, 'not_needed': 0}
            confidence_levels = []
            
            for point in all_points:
                payload = point.payload
                
                # Category counts
                category = payload.get('category', 'other')
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Severity counts
                severity = payload.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Follow-up counts
                if payload.get('follow_up_needed', False):
                    follow_up_counts['needed'] += 1
                else:
                    follow_up_counts['not_needed'] += 1
                
                # Confidence levels
                confidence_levels.append(payload.get('confidence', 0))
            
            # Calculate average confidence
            avg_confidence = sum(confidence_levels) / len(confidence_levels) if confidence_levels else 0
            
            return {
                'total_cases': len(all_points),
                'category_distribution': category_counts,
                'severity_distribution': severity_counts,
                'follow_up_distribution': follow_up_counts,
                'average_confidence': round(avg_confidence, 3),
                'confidence_range': {
                    'min': round(min(confidence_levels), 3) if confidence_levels else 0,
                    'max': round(max(confidence_levels), 3) if confidence_levels else 0
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {
                'error': str(e),
                'total_cases': 0
            }
    
    def delete_patient_analyses(self, patient_id: str) -> int:
        """
        Delete all analyses for a patient (GDPR compliance)
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Number of analyses deleted
        """
        try:
            # Create anonymized patient ID
            anonymized_patient_id = f"patient_{hashlib.sha256(patient_id.encode()).hexdigest()[:12]}"
            
            # Get all points
            all_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000
            )[0]
            
            # Find matching IDs
            ids_to_delete = []
            for point in all_points:
                if point.payload.get('anonymized_patient_id') == anonymized_patient_id:
                    ids_to_delete.append(point.id)
            
            # Delete
            if ids_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=ids_to_delete
                )
            
            print(f"✅ Deleted {len(ids_to_delete)} analyses for patient {patient_id}")
            return len(ids_to_delete)
            
        except Exception as e:
            print(f"❌ Error deleting analyses: {e}")
            raise
    
    def find_similar_images(
        self,
        image_data: Union[Image.Image, str, bytes],
        top_k: int = 10,
        severity_filter: str = None,
        category_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find visually similar skin conditions using IMAGE-TO-IMAGE search
        
        This is TRUE multimodal search - finds similar cases based on visual appearance,
        not text descriptions!
        
        Args:
            image_data: Query image (PIL Image, base64 string, or bytes)
            top_k: Number of similar cases to return
            severity_filter: Filter by severity level
            category_filter: Filter by condition category
            
        Returns:
            List of visually similar cases with similarity scores
            
        Example:
            Upload rash image → Returns 10 most visually similar rashes from history
        """
        if not MULTIMODAL_AVAILABLE:
            print("⚠️ Multimodal embeddings not available")
            return []
        
        try:
            # Generate image embedding from query
            embedding_gen = get_embedding_generator()
            query_embedding = embedding_gen.generate_image_embedding(image_data)
            
            if query_embedding is None:
                print("❌ Failed to generate query image embedding")
                return []
            
            print(f"🔍 Searching for visually similar skin conditions...")
            
            # Search using IMAGE vector (not text!)
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                using="image",  # Use named vector
                limit=top_k * 2,  # Get extra for filtering
                with_payload=True
            ).points
            
            # Process and filter results
            similar_cases = []
            
            for result in search_results:
                case_metadata = result.payload
                
                # Skip if no image embedding
                if not case_metadata.get('has_image_embedding', False):
                    continue
                
                # Apply filters
                if severity_filter and case_metadata.get('severity') != severity_filter:
                    continue
                
                if category_filter and case_metadata.get('category') != category_filter:
                    continue
                
                similar_case = {
                    'case_id': case_metadata['case_id'],
                    'visual_similarity': round(result.score, 3),  # Image similarity!
                    'diagnosis': case_metadata['diagnosis'],
                    'severity': case_metadata['severity'],
                    'confidence': case_metadata['confidence'],
                    'recommendations': case_metadata.get('recommendations', []),
                    'affected_areas': case_metadata.get('affected_areas', []),
                    'category': case_metadata.get('category', 'other'),
                    'timestamp': case_metadata['timestamp']
                }
                
                similar_cases.append(similar_case)
                
                if len(similar_cases) >= top_k:
                    break
            
            print(f"✅ Found {len(similar_cases)} visually similar cases")
            return similar_cases
            
        except Exception as e:
            print(f"❌ Error finding similar images: {e}")
            return []
    
    def find_by_text_query(
        self,
        text_query: str,
        search_in_images: bool = True,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Cross-modal search: TEXT query → IMAGE results
        
        Example: "Show me eczema on elbows" → Returns images of eczema on elbows
        
        Args:
            text_query: Natural language query
            search_in_images: If True, search in image space (cross-modal)
            top_k: Number of results
            
        Returns:
            List of matching cases
        """
        if not MULTIMODAL_AVAILABLE or not search_in_images:
            # Fallback to text-only search
            return self.find_similar_cases(
                diagnosis=text_query,
                top_k=top_k
            )
        
        try:
            # Generate text embedding in CLIP space (same space as images!)
            embedding_gen = get_embedding_generator()
            query_embedding = embedding_gen.generate_text_embedding(text_query)
            
            if query_embedding is None:
                print("❌ Failed to generate text embedding")
                return []
            
            print(f"🔍 Cross-modal search: '{text_query}' → finding matching images...")
            
            # Search using text embedding in IMAGE space (CLIP magic!)
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                using="image",  # Use named vector for cross-modal search
                limit=top_k,
                with_payload=True
            ).points
            
            # Process results
            matching_cases = []
            
            for result in search_results:
                case_metadata = result.payload
                
                # Skip if no image embedding
                if not case_metadata.get('has_image_embedding', False):
                    continue
                
                matching_case = {
                    'case_id': case_metadata['case_id'],
                    'relevance_score': round(result.score, 3),
                    'diagnosis': case_metadata['diagnosis'],
                    'severity': case_metadata['severity'],
                    'recommendations': case_metadata.get('recommendations', []),
                    'affected_areas': case_metadata.get('affected_areas', []),
                    'category': case_metadata.get('category', 'other'),
                    'timestamp': case_metadata['timestamp']
                }
                
                matching_cases.append(matching_case)
            
            print(f"✅ Found {len(matching_cases)} cases matching '{text_query}'")
            return matching_cases
            
        except Exception as e:
            print(f"❌ Error in cross-modal search: {e}")
            return []


# Singleton instance
_skin_analysis_history = None

def get_skin_analysis_history() -> SkinAnalysisHistory:
    """Get or create singleton instance of SkinAnalysisHistory"""
    global _skin_analysis_history
    if _skin_analysis_history is None:
        _skin_analysis_history = SkinAnalysisHistory()
    return _skin_analysis_history
