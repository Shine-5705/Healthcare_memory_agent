"""
Audio Health Analysis with Qdrant Vector Storage

This module stores and retrieves audio health data (cough analysis, respiratory sounds)
using TRUE multimodal embeddings:
- Audio embeddings (Wav2Vec2 - 768 dimensions)
- Text descriptions (all-MiniLM - 384 dimensions)

Features:
- Audio-to-audio search (find similar cough patterns)
- Text-to-audio search (e.g., "show me dry cough recordings")
- Cough classification and pattern matching
- Respiratory health trend analysis
- Privacy-preserving (embeddings only, no raw audio stored long-term)
- GDPR-compliant deletion
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import uuid
import hashlib
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Import multimodal embedding generator
try:
    from multimodal_embeddings import get_embedding_generator
    MULTIMODAL_AVAILABLE = True
    print("✅ Multimodal audio embeddings available")
except ImportError as e:
    print(f"⚠️ Multimodal embeddings not available: {e}")
    MULTIMODAL_AVAILABLE = False


class AudioHealthHistory:
    """
    Manages audio health analysis history using Qdrant vector database
    
    Stores cough recordings and respiratory sounds with:
    - Audio embeddings for acoustic similarity
    - Text embeddings for semantic search
    - Classification labels and health indicators
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure one instance"""
        if cls._instance is None:
            cls._instance = super(AudioHealthHistory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the audio health history storage"""
        if self._initialized:
            return
            
        print("🎵 Initializing Audio Health History...")
        
        # Initialize Qdrant client (in-memory for development)
        self.client = QdrantClient(":memory:")
        
        # Collection name
        self.collection_name = "audio_health_history"
        
        # Initialize text embedding model
        self.text_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_embedding_dim = 384
        
        # Audio embedding dimension (Wav2Vec2)
        self.audio_embedding_dim = 768
        
        # Create collection
        self._create_collection()
        
        # Cough classification categories
        self.cough_types = {
            'dry': ['dry', 'non-productive', 'hacking', 'tickly'],
            'wet': ['wet', 'productive', 'chesty', 'phlegmy'],
            'barking': ['barking', 'croup', 'seal-like'],
            'whooping': ['whooping', 'pertussis', 'paroxysmal'],
            'chronic': ['chronic', 'persistent', 'long-lasting']
        }
        
        self.severity_levels = ['mild', 'moderate', 'severe']
        
        self._initialized = True
        print("✅ Audio Health History initialized")
    
    def _create_collection(self):
        """Create Qdrant collection for MULTIMODAL audio health history"""
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(collection_name=self.collection_name)
            except:
                pass
            
            # Create collection with named vectors for multimodal storage
            vectors_config = {
                "text": VectorParams(
                    size=self.text_embedding_dim,
                    distance=Distance.COSINE
                )
            }
            
            # Add audio vector if available
            if MULTIMODAL_AVAILABLE:
                vectors_config["audio"] = VectorParams(
                    size=self.audio_embedding_dim,
                    distance=Distance.COSINE
                )
                print("🎵 Multimodal collection: Audio + Text vectors enabled")
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config
            )
            print(f"📦 Created multimodal collection: {self.collection_name}")
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            raise
    
    def _classify_cough_type(self, description: str) -> str:
        """
        Classify cough type based on description
        
        Args:
            description: Text description of cough
            
        Returns:
            Cough type classification
        """
        description_lower = description.lower()
        
        for cough_type, keywords in self.cough_types.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return cough_type
        
        return 'unclassified'
    
    def store_audio_analysis(
        self,
        patient_id: str,
        audio_data: Optional[Union[str, bytes, np.ndarray]],
        cough_description: str,
        cough_type: str,
        severity: str,
        duration_seconds: int,
        frequency: str,  # e.g., "3-4 times per hour"
        associated_symptoms: List[str],
        confidence: float = 0.8,
        diagnosis: str = "",
        recommendations: List[str] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Store audio health analysis with MULTIMODAL embeddings
        
        Args:
            patient_id: Patient identifier (will be anonymized)
            audio_data: Audio data (file path, bytes, or numpy array) - can be None
            cough_description: Text description of the cough
            cough_type: Type of cough (dry/wet/barking/whooping/chronic)
            severity: Severity level (mild/moderate/severe)
            duration_seconds: Length of audio recording
            frequency: How often cough occurs
            associated_symptoms: Other symptoms (fever, sore throat, etc.)
            confidence: Analysis confidence (0-1)
            diagnosis: Primary diagnosis
            recommendations: Treatment recommendations
            timestamp: Analysis timestamp
            
        Returns:
            Analysis case ID
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            if recommendations is None:
                recommendations = []
            
            # Create comprehensive text for embedding
            analysis_text = self._create_analysis_text(
                cough_description=cough_description,
                cough_type=cough_type,
                severity=severity,
                frequency=frequency,
                associated_symptoms=associated_symptoms,
                diagnosis=diagnosis,
                recommendations=recommendations
            )
            
            # Generate TEXT embedding
            text_embedding = self.text_embedding_model.encode(analysis_text).tolist()
            
            # Generate AUDIO embedding if available
            audio_embedding = None
            has_audio = False
            if audio_data is not None and MULTIMODAL_AVAILABLE:
                try:
                    embedding_gen = get_embedding_generator()
                    audio_embedding = embedding_gen.generate_audio_embedding(audio_data)
                    if audio_embedding is not None:
                        audio_embedding = audio_embedding.tolist()
                        has_audio = True
                        print("🎵 Generated audio embedding (768-dim Wav2Vec2 vector)")
                except Exception as e:
                    print(f"⚠️ Failed to generate audio embedding: {e}")
            
            # Create unique case ID
            case_id = f"audio_health_{uuid.uuid4().hex[:12]}"
            
            # Anonymize patient ID
            anonymized_patient_id = f"patient_{hashlib.sha256(patient_id.encode()).hexdigest()[:12]}"
            
            # Prepare metadata
            metadata = {
                'case_id': case_id,
                'anonymized_patient_id': anonymized_patient_id,
                'cough_description': cough_description,
                'cough_type': cough_type,
                'severity': severity,
                'duration_seconds': duration_seconds,
                'frequency': frequency,
                'associated_symptoms': associated_symptoms,
                'confidence': confidence,
                'diagnosis': diagnosis or 'Not specified',
                'recommendations': recommendations,
                'timestamp': timestamp.isoformat(),
                'indexed_at': datetime.now().isoformat(),
                'has_audio_embedding': has_audio
            }
            
            # Store in Qdrant with MULTIMODAL vectors
            vectors_dict = {"text": text_embedding}
            if has_audio and audio_embedding is not None:
                vectors_dict["audio"] = audio_embedding
            
            point = PointStruct(
                id=hash(case_id) % (2**63),
                vector=vectors_dict,
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"✅ Stored audio analysis: {case_id} - {cough_type} cough ({severity})")
            return case_id
            
        except Exception as e:
            print(f"❌ Error storing audio analysis: {e}")
            raise
    
    def _create_analysis_text(
        self,
        cough_description: str,
        cough_type: str,
        severity: str,
        frequency: str,
        associated_symptoms: List[str],
        diagnosis: str,
        recommendations: List[str]
    ) -> str:
        """Create comprehensive text for embedding"""
        text_parts = []
        
        text_parts.append(f"Cough Type: {cough_type}")
        text_parts.append(f"Description: {cough_description}")
        text_parts.append(f"Severity: {severity}")
        text_parts.append(f"Frequency: {frequency}")
        
        if associated_symptoms:
            text_parts.append(f"Symptoms: {', '.join(associated_symptoms)}")
        
        if diagnosis:
            text_parts.append(f"Diagnosis: {diagnosis}")
        
        if recommendations:
            text_parts.append(f"Recommendations: {' | '.join(recommendations)}")
        
        return " | ".join(text_parts)
    
    def find_similar_audio(
        self,
        audio_data: Union[str, bytes, np.ndarray],
        top_k: int = 10,
        severity_filter: str = None,
        cough_type_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find acoustically similar cough recordings using AUDIO-TO-AUDIO search
        
        Args:
            audio_data: Query audio (file path, bytes, or numpy array)
            top_k: Number of similar cases to return
            severity_filter: Filter by severity level
            cough_type_filter: Filter by cough type
            
        Returns:
            List of acoustically similar cases
        """
        if not MULTIMODAL_AVAILABLE:
            print("⚠️ Multimodal embeddings not available")
            return []
        
        try:
            # Generate audio embedding from query
            embedding_gen = get_embedding_generator()
            query_embedding = embedding_gen.generate_audio_embedding(audio_data)
            
            if query_embedding is None:
                print("❌ Failed to generate query audio embedding")
                return []
            
            print(f"🔍 Searching for acoustically similar coughs...")
            
            # Search using AUDIO vector
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                using="audio",  # Use named audio vector
                limit=top_k * 2,
                with_payload=True
            ).points
            
            # Process and filter results
            similar_cases = []
            
            for result in search_results:
                case_metadata = result.payload
                
                # Skip if no audio embedding
                if not case_metadata.get('has_audio_embedding', False):
                    continue
                
                # Apply filters
                if severity_filter and case_metadata.get('severity') != severity_filter:
                    continue
                
                if cough_type_filter and case_metadata.get('cough_type') != cough_type_filter:
                    continue
                
                similar_case = {
                    'case_id': case_metadata['case_id'],
                    'acoustic_similarity': round(result.score, 3),
                    'cough_description': case_metadata['cough_description'],
                    'cough_type': case_metadata['cough_type'],
                    'severity': case_metadata['severity'],
                    'frequency': case_metadata['frequency'],
                    'associated_symptoms': case_metadata.get('associated_symptoms', []),
                    'diagnosis': case_metadata.get('diagnosis', ''),
                    'recommendations': case_metadata.get('recommendations', []),
                    'timestamp': case_metadata['timestamp']
                }
                
                similar_cases.append(similar_case)
                
                if len(similar_cases) >= top_k:
                    break
            
            print(f"✅ Found {len(similar_cases)} acoustically similar cases")
            return similar_cases
            
        except Exception as e:
            print(f"❌ Error finding similar audio: {e}")
            return []
    
    def find_by_description(
        self,
        cough_description: str,
        top_k: int = 10,
        severity_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar cases by text description
        
        Args:
            cough_description: Text description of cough symptoms
            top_k: Number of results
            severity_filter: Filter by severity
            
        Returns:
            List of matching cases
        """
        try:
            # Generate text embedding
            query_embedding = self.text_embedding_model.encode(cough_description).tolist()
            
            # Search using text vector
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                using="text",  # Use named text vector
                limit=top_k * 2,
                with_payload=True
            ).points
            
            # Process results
            matching_cases = []
            
            for result in search_results:
                case_metadata = result.payload
                
                # Apply filters
                if severity_filter and case_metadata.get('severity') != severity_filter:
                    continue
                
                matching_case = {
                    'case_id': case_metadata['case_id'],
                    'similarity_score': round(result.score, 3),
                    'cough_description': case_metadata['cough_description'],
                    'cough_type': case_metadata['cough_type'],
                    'severity': case_metadata['severity'],
                    'diagnosis': case_metadata.get('diagnosis', ''),
                    'recommendations': case_metadata.get('recommendations', []),
                    'timestamp': case_metadata['timestamp']
                }
                
                matching_cases.append(matching_case)
                
                if len(matching_cases) >= top_k:
                    break
            
            print(f"✅ Found {len(matching_cases)} cases matching description")
            return matching_cases
            
        except Exception as e:
            print(f"❌ Error finding by description: {e}")
            return []
    
    def get_patient_audio_history(
        self,
        patient_id: str,
        days: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get audio health history for a patient
        
        Args:
            patient_id: Patient identifier
            days: Number of days to look back
            limit: Maximum number of records
            
        Returns:
            List of patient's audio analyses
        """
        try:
            # Anonymize patient ID
            anonymized_patient_id = f"patient_{hashlib.sha256(patient_id.encode()).hexdigest()[:12]}"
            
            # Get all points (filtering would require scrolling)
            all_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit * 2
            )[0]
            
            # Filter by patient
            patient_history = []
            
            for point in all_points:
                if point.payload.get('anonymized_patient_id') == anonymized_patient_id:
                    patient_history.append({
                        'case_id': point.payload['case_id'],
                        'cough_description': point.payload['cough_description'],
                        'cough_type': point.payload['cough_type'],
                        'severity': point.payload['severity'],
                        'frequency': point.payload['frequency'],
                        'diagnosis': point.payload.get('diagnosis', ''),
                        'recommendations': point.payload.get('recommendations', []),
                        'timestamp': point.payload['timestamp']
                    })
            
            # Sort by timestamp (most recent first)
            patient_history.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return patient_history[:limit]
            
        except Exception as e:
            print(f"❌ Error getting patient history: {e}")
            return []
    
    def delete_patient_data(self, patient_id: str) -> int:
        """
        Delete all audio data for a patient (GDPR compliance)
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Number of records deleted
        """
        try:
            # Anonymize patient ID
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
            
            print(f"✅ Deleted {len(ids_to_delete)} audio records for patient {patient_id}")
            return len(ids_to_delete)
            
        except Exception as e:
            print(f"❌ Error deleting patient data: {e}")
            raise


# Singleton instance
_audio_health_history = None

def get_audio_health_history() -> AudioHealthHistory:
    """Get or create singleton instance of AudioHealthHistory"""
    global _audio_health_history
    if _audio_health_history is None:
        _audio_health_history = AudioHealthHistory()
    return _audio_health_history


if __name__ == "__main__":
    # Test the audio health history
    print("\n🧪 Testing Audio Health History...")
    
    history = get_audio_health_history()
    
    # Test storing an analysis (without actual audio for now)
    case_id = history.store_audio_analysis(
        patient_id="test_patient_123",
        audio_data=None,  # Would be actual audio in production
        cough_description="Dry, persistent cough, worse at night",
        cough_type="dry",
        severity="moderate",
        duration_seconds=30,
        frequency="10-15 times per hour",
        associated_symptoms=["sore throat", "slight fever"],
        diagnosis="Possible upper respiratory infection",
        recommendations=["Rest", "Hydration", "Cough suppressant"]
    )
    
    print(f"\n✅ Test case stored: {case_id}")
    
    # Test text-based search
    similar = history.find_by_description("persistent dry cough at night", top_k=5)
    print(f"✅ Found {len(similar)} similar cases by description")
    
    print("\n✅ Audio Health History test completed!")
