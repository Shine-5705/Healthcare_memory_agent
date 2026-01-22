"""
AI Recommendation System using Qdrant Vector Database
Analyzes patient conditions, vitals, and history to generate personalized health advice
"""
import os
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import logging
import statistics

# Import other CareMate systems
try:
    from medical_knowledge_base import get_medical_knowledge_base
    MEDICAL_KNOWLEDGE_AVAILABLE = True
except ImportError:
    MEDICAL_KNOWLEDGE_AVAILABLE = False
    logging.warning("Medical knowledge base not available")

try:
    from vitals_tracker import get_vitals_tracker
    VITALS_TRACKER_AVAILABLE = True
except ImportError:
    VITALS_TRACKER_AVAILABLE = False
    logging.warning("Vitals tracker not available")

try:
    from patient_memory import get_memory_system
    PATIENT_MEMORY_AVAILABLE = True
except ImportError:
    PATIENT_MEMORY_AVAILABLE = False
    logging.warning("Patient memory system not available")

try:
    from evidence_logger import get_evidence_logger
    EVIDENCE_LOGGER_AVAILABLE = True
except ImportError:
    EVIDENCE_LOGGER_AVAILABLE = False
    logging.warning("Evidence logger not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationEngine:
    """AI-powered health recommendation system"""
    
    # Recommendation priority levels
    PRIORITY_CRITICAL = "critical"
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    
    # Recommendation categories
    CATEGORY_LIFESTYLE = "lifestyle"
    CATEGORY_MEDICATION = "medication"
    CATEGORY_MONITORING = "monitoring"
    CATEGORY_DIET = "diet"
    CATEGORY_EXERCISE = "exercise"
    CATEGORY_MENTAL_HEALTH = "mental_health"
    CATEGORY_PREVENTIVE = "preventive"
    
    def __init__(self, collection_name: str = "ai_recommendations"):
        """Initialize the AI Recommendation Engine"""
        self.collection_name = collection_name
        
        # Initialize Qdrant client
        qdrant_url = os.getenv("QDRANT_URL", None)
        qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        
        if qdrant_url:
            logger.info(f"🔗 Connecting to Qdrant server at {qdrant_url}")
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            logger.info("💾 Using Qdrant in-memory mode for AI recommendations")
            self.client = QdrantClient(":memory:")
        
        # Initialize embedding model
        logger.info("🤖 Loading sentence transformer model for recommendations...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384
        
        # Setup collection
        self._setup_collection()
        
        # Load external systems
        self.medical_kb = get_medical_knowledge_base() if MEDICAL_KNOWLEDGE_AVAILABLE else None
        self.vitals_tracker = get_vitals_tracker() if VITALS_TRACKER_AVAILABLE else None
        self.patient_memory = get_memory_system() if PATIENT_MEMORY_AVAILABLE else None
        
        logger.info("✅ AI Recommendation Engine initialized")
    
    def _setup_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"📦 Creating recommendations collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info("✅ Recommendations collection created successfully")
            else:
                logger.info(f"✅ Recommendations collection '{self.collection_name}' already exists")
                
        except Exception as e:
            logger.error(f"❌ Error setting up recommendations collection: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            raise
    
    def _analyze_vitals_trends(self, patient_id: str, days: int = 30) -> Dict:
        """Analyze patient's vitals trends and identify concerns"""
        if not self.vitals_tracker:
            return {"concerns": [], "trends": {}}
        
        try:
            # Get trend analysis
            trends = self.vitals_tracker.generate_trend_analysis(patient_id, days)
            
            concerns = []
            vital_status = {}
            
            if not trends or 'trends' not in trends:
                return {"concerns": [], "trends": {}}
            
            # Analyze each vital
            for vital_name, vital_data in trends['trends'].items():
                trend_direction = vital_data.get('trend_direction', 'stable')
                trend_percentage = vital_data.get('trend_percentage', 0)
                mean_value = vital_data.get('mean', 0)
                
                vital_status[vital_name] = {
                    'mean': mean_value,
                    'trend': trend_direction,
                    'change': trend_percentage
                }
                
                # Identify concerns based on trends
                if vital_name == 'systolic_bp':
                    if mean_value > 140:
                        concerns.append({
                            'vital': 'Blood Pressure (Systolic)',
                            'issue': f'Elevated average: {mean_value:.1f} mmHg',
                            'severity': 'high' if mean_value > 160 else 'medium',
                            'trend': trend_direction
                        })
                    elif trend_direction == 'increasing' and trend_percentage > 10:
                        concerns.append({
                            'vital': 'Blood Pressure (Systolic)',
                            'issue': f'Rising trend: +{trend_percentage:.1f}%',
                            'severity': 'medium',
                            'trend': trend_direction
                        })
                
                elif vital_name == 'heart_rate':
                    if mean_value > 100:
                        concerns.append({
                            'vital': 'Heart Rate',
                            'issue': f'Elevated average: {mean_value:.1f} bpm',
                            'severity': 'medium',
                            'trend': trend_direction
                        })
                
                elif vital_name == 'blood_glucose':
                    if mean_value > 140:
                        concerns.append({
                            'vital': 'Blood Glucose',
                            'issue': f'Elevated average: {mean_value:.1f} mg/dL',
                            'severity': 'high' if mean_value > 200 else 'medium',
                            'trend': trend_direction
                        })
                
                elif vital_name == 'oxygen_saturation':
                    if mean_value < 95:
                        concerns.append({
                            'vital': 'Oxygen Saturation',
                            'issue': f'Low average: {mean_value:.1f}%',
                            'severity': 'high' if mean_value < 90 else 'medium',
                            'trend': trend_direction
                        })
            
            return {
                'concerns': concerns,
                'trends': vital_status,
                'total_readings': trends.get('total_readings', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing vitals trends: {e}")
            return {"concerns": [], "trends": {}}
    
    def _extract_symptoms_from_history(self, patient_id: str, limit: int = 20) -> List[str]:
        """Extract symptoms from patient conversation history"""
        if not self.patient_memory:
            return []
        
        try:
            history = self.patient_memory.get_patient_history(patient_id, limit)
            
            all_symptoms = []
            for conversation in history:
                symptoms = conversation.get('symptoms', [])
                all_symptoms.extend(symptoms)
            
            # Remove duplicates while preserving order
            unique_symptoms = []
            seen = set()
            for symptom in all_symptoms:
                symptom_lower = symptom.lower()
                if symptom_lower not in seen:
                    seen.add(symptom_lower)
                    unique_symptoms.append(symptom)
            
            return unique_symptoms[:10]  # Return top 10 unique symptoms
            
        except Exception as e:
            logger.error(f"❌ Error extracting symptoms: {e}")
            return []
    
    def _search_relevant_conditions(self, patient_profile: str, limit: int = 3) -> List[Dict]:
        """Search medical knowledge base for relevant conditions"""
        if not self.medical_kb:
            return []
        
        try:
            # Generate query embedding and store for evidence logging
            self._last_query_embedding = self._generate_embedding(patient_profile)
            
            # Search medical knowledge
            results = self.medical_kb.search_medical_knowledge(patient_profile, limit)
            
            # Store raw search results for evidence tracking
            if hasattr(self.medical_kb, '_last_search_results'):
                self._last_search_results = self.medical_kb._last_search_results
            
            return results
        except Exception as e:
            logger.error(f"❌ Error searching conditions: {e}")
            return []
    
    def _generate_lifestyle_recommendations(self, conditions: List[Dict], concerns: List[Dict]) -> List[Dict]:
        """Generate lifestyle recommendations based on conditions and concerns"""
        recommendations = []
        
        for condition in conditions:
            care_guidelines = condition.get('care_guidelines', [])
            
            # Extract lifestyle-related guidelines
            for guideline in care_guidelines[:5]:
                if any(keyword in guideline.lower() for keyword in 
                       ['exercise', 'diet', 'weight', 'sleep', 'stress', 'smoking', 'alcohol', 'activity']):
                    recommendations.append({
                        'text': guideline,
                        'category': self._categorize_recommendation(guideline),
                        'condition': condition['name'],
                        'priority': self._determine_priority(guideline, concerns),
                        'evidence_level': 'high'
                    })
        
        return recommendations
    
    def _generate_medication_recommendations(self, conditions: List[Dict]) -> List[Dict]:
        """Generate medication-related recommendations"""
        recommendations = []
        
        for condition in conditions:
            treatments = condition.get('treatments', [])
            
            # Extract medication-related treatments
            for treatment in treatments[:4]:
                if any(keyword in treatment.lower() for keyword in 
                       ['medication', 'drug', 'inhibitor', 'blocker', 'therapy', '-pril', '-sartan', '-statin']):
                    recommendations.append({
                        'text': f"Discuss with doctor: {treatment}",
                        'category': self.CATEGORY_MEDICATION,
                        'condition': condition['name'],
                        'priority': self.PRIORITY_HIGH,
                        'evidence_level': 'high',
                        'requires_consultation': True
                    })
        
        return recommendations
    
    def _generate_monitoring_recommendations(self, conditions: List[Dict], vitals_concerns: List[Dict]) -> List[Dict]:
        """Generate monitoring and testing recommendations"""
        recommendations = []
        
        # Based on vital concerns
        for concern in vitals_concerns:
            vital = concern['vital']
            severity = concern['severity']
            
            if 'Blood Pressure' in vital:
                recommendations.append({
                    'text': 'Monitor blood pressure daily at the same time, record readings',
                    'category': self.CATEGORY_MONITORING,
                    'condition': 'Hypertension management',
                    'priority': self.PRIORITY_HIGH if severity == 'high' else self.PRIORITY_MEDIUM,
                    'evidence_level': 'high'
                })
            elif 'Blood Glucose' in vital:
                recommendations.append({
                    'text': 'Check blood glucose before meals and 2 hours after meals',
                    'category': self.CATEGORY_MONITORING,
                    'condition': 'Diabetes management',
                    'priority': self.PRIORITY_HIGH if severity == 'high' else self.PRIORITY_MEDIUM,
                    'evidence_level': 'high'
                })
            elif 'Oxygen' in vital:
                recommendations.append({
                    'text': 'Monitor oxygen saturation regularly, especially during activity',
                    'category': self.CATEGORY_MONITORING,
                    'condition': 'Respiratory health',
                    'priority': self.PRIORITY_HIGH,
                    'evidence_level': 'high'
                })
        
        return recommendations
    
    def _categorize_recommendation(self, text: str) -> str:
        """Categorize a recommendation based on its content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['exercise', 'walk', 'physical activity', 'aerobic']):
            return self.CATEGORY_EXERCISE
        elif any(word in text_lower for word in ['diet', 'eat', 'food', 'nutrition', 'sodium', 'calorie']):
            return self.CATEGORY_DIET
        elif any(word in text_lower for word in ['stress', 'anxiety', 'depression', 'mental', 'mood', 'therapy']):
            return self.CATEGORY_MENTAL_HEALTH
        elif any(word in text_lower for word in ['monitor', 'check', 'test', 'measure', 'track']):
            return self.CATEGORY_MONITORING
        elif any(word in text_lower for word in ['medication', 'drug', 'pill', 'prescription']):
            return self.CATEGORY_MEDICATION
        elif any(word in text_lower for word in ['prevent', 'avoid', 'quit', 'stop']):
            return self.CATEGORY_PREVENTIVE
        else:
            return self.CATEGORY_LIFESTYLE
    
    def _determine_priority(self, recommendation: str, concerns: List[Dict]) -> str:
        """Determine priority level for a recommendation"""
        rec_lower = recommendation.lower()
        
        # Check if recommendation addresses a critical concern
        for concern in concerns:
            if concern.get('severity') == 'high':
                vital = concern['vital'].lower()
                if any(word in rec_lower for word in vital.split()):
                    return self.PRIORITY_CRITICAL
        
        # Emergency/critical keywords
        if any(word in rec_lower for word in ['emergency', 'immediately', 'urgent', 'critical']):
            return self.PRIORITY_CRITICAL
        
        # High priority keywords
        if any(word in rec_lower for word in ['consult', 'doctor', 'medication', 'monitor', 'daily']):
            return self.PRIORITY_HIGH
        
        # Medium priority keywords
        if any(word in rec_lower for word in ['regular', 'weekly', 'maintain', 'follow']):
            return self.PRIORITY_MEDIUM
        
        return self.PRIORITY_LOW
    
    def _rank_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Rank recommendations by priority and relevance"""
        priority_order = {
            self.PRIORITY_CRITICAL: 0,
            self.PRIORITY_HIGH: 1,
            self.PRIORITY_MEDIUM: 2,
            self.PRIORITY_LOW: 3
        }
        
        # Sort by priority, then by evidence level
        ranked = sorted(
            recommendations,
            key=lambda x: (
                priority_order.get(x.get('priority', self.PRIORITY_LOW), 3),
                0 if x.get('evidence_level') == 'high' else 1
            )
        )
        
        return ranked
    
    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicate recommendations"""
        seen = set()
        unique = []
        
        for rec in recommendations:
            # Create a signature based on text
            signature = rec['text'].lower().strip()
            if signature not in seen:
                seen.add(signature)
                unique.append(rec)
        
        return unique
    
    def generate_recommendations(
        self,
        patient_id: str,
        include_vitals: bool = True,
        include_history: bool = True,
        max_recommendations: int = 15
    ) -> Dict:
        """
        Generate personalized health recommendations for a patient
        
        Args:
            patient_id: Patient identifier
            include_vitals: Include vitals analysis in recommendations
            include_history: Include conversation history analysis
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            Dictionary with recommendations, analysis, and metadata
        """
        try:
            logger.info(f"🔍 Generating recommendations for patient {patient_id}")
            
            # Step 1: Analyze patient vitals
            vitals_analysis = {}
            if include_vitals:
                vitals_analysis = self._analyze_vitals_trends(patient_id, 30)
            
            # Step 2: Extract symptoms from history
            symptoms = []
            if include_history:
                symptoms = self._extract_symptoms_from_history(patient_id, 20)
            
            # Step 3: Build patient profile for search
            profile_parts = []
            
            if symptoms:
                profile_parts.append(f"Patient symptoms: {', '.join(symptoms[:5])}")
            
            if vitals_analysis.get('concerns'):
                concerns_text = "; ".join([
                    f"{c['vital']}: {c['issue']}" 
                    for c in vitals_analysis['concerns'][:3]
                ])
                profile_parts.append(f"Health concerns: {concerns_text}")
            
            patient_profile = ". ".join(profile_parts) if profile_parts else "General health assessment"
            
            # Step 4: Search medical knowledge base with EVIDENCE TRACKING
            relevant_conditions = self._search_relevant_conditions(patient_profile, 3)
            
            # LOG EVIDENCE: Show what was retrieved from Qdrant
            if EVIDENCE_LOGGER_AVAILABLE and relevant_conditions:
                evidence_logger = get_evidence_logger()
                # Track medical knowledge retrieval
                if hasattr(self, '_last_search_results'):
                    evidence_logger.log_vector_retrieval(
                        collection_name="medical_knowledge",
                        query_type="text",
                        query_embedding=self._last_query_embedding if hasattr(self, '_last_query_embedding') else [],
                        search_results=self._last_search_results,
                        decision_type="recommendation_generation",
                        reasoning=f"Found {len(relevant_conditions)} relevant conditions from medical knowledge base. "
                                 f"Top match: {relevant_conditions[0]['name']} (confidence: {relevant_conditions[0]['confidence_score']:.2f}). "
                                 f"These conditions guided recommendation categories: lifestyle, medication, and monitoring.",
                        influence_score=0.85,
                        confidence=max(c['confidence_score'] for c in relevant_conditions)
                    )
            
            # Step 5: Generate recommendations by category
            all_recommendations = []
            
            # Lifestyle recommendations
            lifestyle_recs = self._generate_lifestyle_recommendations(
                relevant_conditions,
                vitals_analysis.get('concerns', [])
            )
            all_recommendations.extend(lifestyle_recs)
            
            # Medication recommendations
            medication_recs = self._generate_medication_recommendations(relevant_conditions)
            all_recommendations.extend(medication_recs)
            
            # Monitoring recommendations
            monitoring_recs = self._generate_monitoring_recommendations(
                relevant_conditions,
                vitals_analysis.get('concerns', [])
            )
            all_recommendations.extend(monitoring_recs)
            
            # Step 6: Add critical alerts if needed
            for concern in vitals_analysis.get('concerns', []):
                if concern['severity'] == 'high':
                    all_recommendations.insert(0, {
                        'text': f"⚠️ ALERT: {concern['issue']} - Consult your healthcare provider",
                        'category': self.CATEGORY_MONITORING,
                        'condition': 'Critical vital alert',
                        'priority': self.PRIORITY_CRITICAL,
                        'evidence_level': 'high',
                        'requires_consultation': True
                    })
            
            # Step 7: Deduplicate and rank
            unique_recs = self._deduplicate_recommendations(all_recommendations)
            ranked_recs = self._rank_recommendations(unique_recs)
            
            # Step 8: Limit to max recommendations
            final_recs = ranked_recs[:max_recommendations]
            
            # Step 9: Add recommendation IDs and timestamps
            timestamp = datetime.now().isoformat()
            for i, rec in enumerate(final_recs):
                rec['recommendation_id'] = str(uuid.uuid4())
                rec['generated_at'] = timestamp
                rec['rank'] = i + 1
            
            # Step 10: Store recommendations in Qdrant
            self._store_recommendations(patient_id, final_recs, patient_profile)
            
            # Build response
            response = {
                'success': True,
                'patient_id': patient_id,
                'generated_at': timestamp,
                'analysis': {
                    'vitals_concerns': vitals_analysis.get('concerns', []),
                    'symptoms_identified': symptoms,
                    'relevant_conditions': [
                        {
                            'name': c['name'],
                            'confidence': c['confidence_score'],
                            'category': c['category']
                        }
                        for c in relevant_conditions
                    ],
                    'total_readings': vitals_analysis.get('total_readings', 0)
                },
                'recommendations': final_recs,
                'summary': {
                    'total_recommendations': len(final_recs),
                    'by_priority': {
                        self.PRIORITY_CRITICAL: len([r for r in final_recs if r['priority'] == self.PRIORITY_CRITICAL]),
                        self.PRIORITY_HIGH: len([r for r in final_recs if r['priority'] == self.PRIORITY_HIGH]),
                        self.PRIORITY_MEDIUM: len([r for r in final_recs if r['priority'] == self.PRIORITY_MEDIUM]),
                        self.PRIORITY_LOW: len([r for r in final_recs if r['priority'] == self.PRIORITY_LOW])
                    },
                    'by_category': {
                        category: len([r for r in final_recs if r['category'] == category])
                        for category in [
                            self.CATEGORY_LIFESTYLE, self.CATEGORY_MEDICATION,
                            self.CATEGORY_MONITORING, self.CATEGORY_DIET,
                            self.CATEGORY_EXERCISE, self.CATEGORY_MENTAL_HEALTH,
                            self.CATEGORY_PREVENTIVE
                        ]
                    },
                    'requires_consultation': len([r for r in final_recs if r.get('requires_consultation', False)])
                }
            }
            
            logger.info(f"✅ Generated {len(final_recs)} recommendations for patient {patient_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }
    
    def _store_recommendations(self, patient_id: str, recommendations: List[Dict], profile: str):
        """Store recommendations in Qdrant for history tracking"""
        try:
            # Create embedding from profile
            embedding = self._generate_embedding(profile)
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'patient_id': patient_id,
                    'timestamp': datetime.now().isoformat(),
                    'profile': profile,
                    'recommendations': recommendations,
                    'total_count': len(recommendations)
                }
            )
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing recommendations: {e}")
    
    def get_recommendation_history(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get past recommendations for a patient"""
        try:
            # Search for patient's recommendations
            results = self.client.scroll(
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
            
            history = []
            for point in results[0]:
                history.append({
                    'timestamp': point.payload.get('timestamp'),
                    'profile': point.payload.get('profile'),
                    'recommendations': point.payload.get('recommendations', []),
                    'total_count': point.payload.get('total_count', 0)
                })
            
            # Sort by timestamp descending
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Error retrieving recommendation history: {e}")
            return []
    
    def delete_patient_recommendations(self, patient_id: str) -> int:
        """Delete all recommendations for a patient (GDPR compliance)"""
        try:
            # Get all points for patient
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="patient_id",
                            match=MatchValue(value=patient_id)
                        )
                    ]
                ),
                limit=1000
            )
            
            point_ids = [point.id for point in results[0]]
            
            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
            
            logger.info(f"🗑️ Deleted {len(point_ids)} recommendation records for patient {patient_id}")
            return len(point_ids)
            
        except Exception as e:
            logger.error(f"❌ Error deleting recommendations: {e}")
            return 0


# Singleton instance
_recommendation_engine = None

def get_recommendation_engine() -> RecommendationEngine:
    """Get or create the singleton RecommendationEngine instance"""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine
