"""
Patient Memory System using Qdrant Vector Database
Stores and retrieves patient chat history, symptoms, and medical interactions
"""
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatientMemorySystem:
    """Manages patient conversation memory using Qdrant vector database"""
    
    def __init__(self, collection_name: str = "patient_conversations"):
        """
        Initialize the Patient Memory System
        
        Args:
            collection_name: Name of the Qdrant collection to use
        """
        self.collection_name = collection_name
        
        # Initialize Qdrant client (using in-memory mode by default, can be configured for server mode)
        qdrant_url = os.getenv("QDRANT_URL", None)
        qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        
        if qdrant_url:
            logger.info(f"🔗 Connecting to Qdrant server at {qdrant_url}")
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            logger.info("💾 Using Qdrant in-memory mode")
            self.client = QdrantClient(":memory:")
        
        # Initialize embedding model
        logger.info("🤖 Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        
        # Create collection if it doesn't exist
        self._setup_collection()
        logger.info("✅ Patient Memory System initialized")
    
    def _setup_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"📦 Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info("✅ Collection created successfully")
            else:
                logger.info(f"✅ Collection '{self.collection_name}' already exists")
                
        except Exception as e:
            logger.error(f"❌ Error setting up collection: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            raise
    
    def store_conversation(
        self,
        patient_id: str,
        user_message: str,
        assistant_response: str,
        language: str = "en",
        symptoms: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store a conversation turn in Qdrant
        
        Args:
            patient_id: Unique identifier for the patient
            user_message: The user's message
            assistant_response: The AI assistant's response
            language: Language of the conversation
            symptoms: List of extracted symptoms (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            UUID of the stored conversation
        """
        try:
            # Create combined text for semantic search
            combined_text = f"User: {user_message}\nAssistant: {assistant_response}"
            
            # Generate embedding
            embedding = self._generate_embedding(combined_text)
            
            # Create unique ID
            conversation_id = str(uuid.uuid4())
            
            # Prepare payload
            payload = {
                "patient_id": patient_id,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "symptoms": symptoms or [],
                "metadata": metadata or {}
            }
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=conversation_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"✅ Stored conversation for patient {patient_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"❌ Error storing conversation: {e}")
            raise
    
    def retrieve_relevant_conversations(
        self,
        patient_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve the most relevant past conversations for a patient
        
        Args:
            patient_id: Unique identifier for the patient
            query: Current user message to find relevant context
            limit: Maximum number of conversations to retrieve (default: 5)
            
        Returns:
            List of relevant conversation dictionaries
        """
        try:
            # Generate embedding for the query
            query_embedding = self._generate_embedding(query)
            
            # Search for relevant conversations for this patient
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="patient_id",
                            match=MatchValue(value=patient_id)
                        )
                    ]
                ),
                limit=limit
            )
            
            # Format results
            conversations = []
            for result in search_results.points:
                conversation = {
                    "id": result.id,
                    "score": result.score,
                    "user_message": result.payload.get("user_message", ""),
                    "assistant_response": result.payload.get("assistant_response", ""),
                    "language": result.payload.get("language", "en"),
                    "timestamp": result.payload.get("timestamp", ""),
                    "symptoms": result.payload.get("symptoms", []),
                    "metadata": result.payload.get("metadata", {})
                }
                conversations.append(conversation)
            
            logger.info(f"✅ Retrieved {len(conversations)} relevant conversations for patient {patient_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error retrieving conversations: {e}")
            return []
    
    def get_patient_history(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get all recent conversations for a patient (chronologically)
        
        Args:
            patient_id: Unique identifier for the patient
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation dictionaries sorted by timestamp
        """
        try:
            # Scroll through all points for the patient
            records, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="patient_id",
                            match=MatchValue(value=patient_id)
                        )
                    ]
                ),
                limit=limit
            )
            
            # Format and sort by timestamp
            conversations = []
            for record in records:
                conversation = {
                    "id": record.id,
                    "user_message": record.payload.get("user_message", ""),
                    "assistant_response": record.payload.get("assistant_response", ""),
                    "language": record.payload.get("language", "en"),
                    "timestamp": record.payload.get("timestamp", ""),
                    "symptoms": record.payload.get("symptoms", []),
                    "metadata": record.payload.get("metadata", {})
                }
                conversations.append(conversation)
            
            # Sort by timestamp (most recent first)
            conversations.sort(key=lambda x: x["timestamp"], reverse=True)
            
            logger.info(f"✅ Retrieved {len(conversations)} conversations from history for patient {patient_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error retrieving patient history: {e}")
            return []
    
    def format_context_for_prompt(self, conversations: List[Dict]) -> str:
        """
        Format retrieved conversations into context for AI prompt
        
        Args:
            conversations: List of conversation dictionaries
            
        Returns:
            Formatted context string
        """
        if not conversations:
            return ""
        
        context_parts = ["Previous relevant conversations:"]
        
        for i, conv in enumerate(conversations, 1):
            timestamp = conv.get("timestamp", "Unknown time")
            user_msg = conv.get("user_message", "")
            assistant_msg = conv.get("assistant_response", "")
            symptoms = conv.get("symptoms", [])
            
            context_parts.append(f"\n[{i}] ({timestamp})")
            if symptoms:
                context_parts.append(f"   Symptoms: {', '.join(symptoms)}")
            context_parts.append(f"   User: {user_msg}")
            context_parts.append(f"   Assistant: {assistant_msg}")
        
        return "\n".join(context_parts)
    
    def extract_symptoms(self, text: str) -> List[str]:
        """
        Simple symptom extraction from text
        (Can be enhanced with NLP models)
        
        Args:
            text: Text to extract symptoms from
            
        Returns:
            List of detected symptoms
        """
        # Common symptoms keywords
        symptom_keywords = [
            "fever", "cough", "cold", "headache", "pain", "ache",
            "nausea", "vomiting", "diarrhea", "fatigue", "weakness",
            "dizziness", "breathless", "breathing", "chest pain",
            "stomach", "throat", "sore", "runny nose", "congestion"
        ]
        
        text_lower = text.lower()
        detected = [symptom for symptom in symptom_keywords if symptom in text_lower]
        
        return list(set(detected))  # Remove duplicates
    
    def delete_patient_data(self, patient_id: str) -> int:
        """
        Delete all data for a patient (for privacy/GDPR compliance)
        
        Args:
            patient_id: Unique identifier for the patient
            
        Returns:
            Number of records deleted
        """
        try:
            # Get all points for the patient
            records, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="patient_id",
                            match=MatchValue(value=patient_id)
                        )
                    ]
                ),
                limit=10000  # Large limit to get all records
            )
            
            # Delete all records
            point_ids = [record.id for record in records]
            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
            
            logger.info(f"✅ Deleted {len(point_ids)} records for patient {patient_id}")
            return len(point_ids)
            
        except Exception as e:
            logger.error(f"❌ Error deleting patient data: {e}")
            return 0


# Singleton instance
_memory_system = None

def get_memory_system() -> PatientMemorySystem:
    """Get or create the singleton PatientMemorySystem instance"""
    global _memory_system
    if _memory_system is None:
        _memory_system = PatientMemorySystem()
    return _memory_system
