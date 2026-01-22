"""
Vitals Tracking System using Qdrant Vector Database
Stores and analyzes patient vitals: blood pressure, heart rate, glucose, temperature, oxygen levels
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, Range
from sentence_transformers import SentenceTransformer
import logging
import statistics

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VitalsTracker:
    """Manages patient vitals tracking using Qdrant vector database"""
    
    # Normal ranges for vitals (for anomaly detection)
    NORMAL_RANGES = {
        'systolic_bp': (90, 120),      # mmHg
        'diastolic_bp': (60, 80),      # mmHg
        'heart_rate': (60, 100),       # bpm
        'glucose': (70, 140),          # mg/dL (fasting: 70-100, post-meal: up to 140)
        'temperature': (97.0, 99.5),   # °F
        'oxygen_level': (95, 100)      # % SpO2
    }
    
    # Critical thresholds for alerts
    CRITICAL_THRESHOLDS = {
        'systolic_bp': {'low': 80, 'high': 180},
        'diastolic_bp': {'low': 50, 'high': 120},
        'heart_rate': {'low': 40, 'high': 140},
        'glucose': {'low': 60, 'high': 300},
        'temperature': {'low': 95.0, 'high': 103.0},
        'oxygen_level': {'low': 90, 'high': 100}
    }
    
    def __init__(self, collection_name: str = "patient_vitals"):
        """
        Initialize the Vitals Tracker
        
        Args:
            collection_name: Name of the Qdrant collection to use
        """
        self.collection_name = collection_name
        
        # Initialize Qdrant client
        qdrant_url = os.getenv("QDRANT_URL", None)
        qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        
        if qdrant_url:
            logger.info(f"🔗 Connecting to Qdrant server at {qdrant_url}")
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            logger.info("💾 Using Qdrant in-memory mode for vitals")
            self.client = QdrantClient(":memory:")
        
        # Initialize embedding model
        logger.info("🤖 Loading sentence transformer model for vitals...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384
        
        # Create collection if it doesn't exist
        self._setup_collection()
        logger.info("✅ Vitals Tracker initialized")
    
    def _setup_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"📦 Creating vitals collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info("✅ Vitals collection created successfully")
            else:
                logger.info(f"✅ Vitals collection '{self.collection_name}' already exists")
                
        except Exception as e:
            logger.error(f"❌ Error setting up vitals collection: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            raise
    
    def _create_vitals_description(self, vitals: Dict) -> str:
        """Create a natural language description of vitals for embedding"""
        parts = []
        
        if 'systolic_bp' in vitals and 'diastolic_bp' in vitals:
            parts.append(f"blood pressure {vitals['systolic_bp']}/{vitals['diastolic_bp']} mmHg")
        
        if 'heart_rate' in vitals:
            parts.append(f"heart rate {vitals['heart_rate']} bpm")
        
        if 'glucose' in vitals:
            parts.append(f"glucose {vitals['glucose']} mg/dL")
        
        if 'temperature' in vitals:
            parts.append(f"temperature {vitals['temperature']}°F")
        
        if 'oxygen_level' in vitals:
            parts.append(f"oxygen saturation {vitals['oxygen_level']}%")
        
        description = f"Patient vitals recorded: {', '.join(parts)}"
        
        # Add notes if present
        if 'notes' in vitals and vitals['notes']:
            description += f". Notes: {vitals['notes']}"
        
        return description
    
    def _check_anomalies(self, vitals: Dict) -> List[Dict]:
        """
        Check for anomalous readings
        
        Returns:
            List of anomaly alerts with severity levels
        """
        anomalies = []
        
        for vital_name, value in vitals.items():
            if vital_name not in self.NORMAL_RANGES:
                continue
            
            normal_min, normal_max = self.NORMAL_RANGES[vital_name]
            critical = self.CRITICAL_THRESHOLDS.get(vital_name, {})
            
            severity = "normal"
            message = ""
            
            # Check critical levels first
            if critical.get('low') and value < critical['low']:
                severity = "critical"
                message = f"{vital_name.replace('_', ' ').title()} critically low: {value}"
            elif critical.get('high') and value > critical['high']:
                severity = "critical"
                message = f"{vital_name.replace('_', ' ').title()} critically high: {value}"
            # Check abnormal but not critical
            elif value < normal_min:
                severity = "warning"
                message = f"{vital_name.replace('_', ' ').title()} below normal: {value} (normal: {normal_min}-{normal_max})"
            elif value > normal_max:
                severity = "warning"
                message = f"{vital_name.replace('_', ' ').title()} above normal: {value} (normal: {normal_min}-{normal_max})"
            
            if severity != "normal":
                anomalies.append({
                    "vital": vital_name,
                    "value": value,
                    "severity": severity,
                    "message": message,
                    "normal_range": f"{normal_min}-{normal_max}"
                })
        
        return anomalies
    
    def store_vitals(
        self,
        patient_id: str,
        vitals: Dict,
        timestamp: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Store patient vitals in Qdrant
        
        Args:
            patient_id: Unique identifier for the patient
            vitals: Dictionary of vitals (systolic_bp, diastolic_bp, heart_rate, glucose, temperature, oxygen_level)
            timestamp: Timestamp of measurement (defaults to now)
            notes: Optional notes about the reading
            
        Returns:
            Tuple of (vitals_id, list of anomaly alerts)
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Add notes to vitals if provided
            if notes:
                vitals['notes'] = notes
            
            # Check for anomalies
            anomalies = self._check_anomalies(vitals)
            
            # Create description for semantic search
            description = self._create_vitals_description(vitals)
            
            # Generate embedding
            embedding = self._generate_embedding(description)
            
            # Create unique ID
            vitals_id = str(uuid.uuid4())
            
            # Prepare payload
            payload = {
                "patient_id": patient_id,
                "timestamp": timestamp.isoformat(),
                "vitals": vitals,
                "description": description,
                "anomalies": anomalies,
                "has_anomalies": len(anomalies) > 0,
                "severity": max([a['severity'] for a in anomalies], default='normal', 
                              key=lambda x: ['normal', 'warning', 'critical'].index(x))
            }
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=vitals_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"✅ Stored vitals for patient {patient_id} with {len(anomalies)} anomalies")
            return vitals_id, anomalies
            
        except Exception as e:
            logger.error(f"❌ Error storing vitals: {e}")
            raise
    
    def get_vitals_history(
        self,
        patient_id: str,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get vitals history for a patient
        
        Args:
            patient_id: Unique identifier for the patient
            days: Number of days to look back (default: 30)
            limit: Maximum number of records to retrieve
            
        Returns:
            List of vitals records sorted by timestamp (most recent first)
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)
            
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
            
            # Filter by date and format
            vitals_list = []
            for record in records:
                timestamp_str = record.payload.get("timestamp", "")
                try:
                    record_time = datetime.fromisoformat(timestamp_str)
                    if record_time >= cutoff_date:
                        vitals_list.append({
                            "id": record.id,
                            "timestamp": timestamp_str,
                            "vitals": record.payload.get("vitals", {}),
                            "description": record.payload.get("description", ""),
                            "anomalies": record.payload.get("anomalies", []),
                            "severity": record.payload.get("severity", "normal")
                        })
                except ValueError:
                    continue
            
            # Sort by timestamp (most recent first)
            vitals_list.sort(key=lambda x: x["timestamp"], reverse=True)
            
            logger.info(f"✅ Retrieved {len(vitals_list)} vitals records for patient {patient_id} (last {days} days)")
            return vitals_list
            
        except Exception as e:
            logger.error(f"❌ Error retrieving vitals history: {e}")
            return []
    
    def find_similar_vitals(
        self,
        patient_id: str,
        current_vitals: Dict,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find similar vitals patterns using semantic search
        
        Args:
            patient_id: Unique identifier for the patient
            current_vitals: Current vitals to compare against
            limit: Number of similar records to retrieve
            
        Returns:
            List of similar vitals records with similarity scores
        """
        try:
            # Create description for current vitals
            description = self._create_vitals_description(current_vitals)
            
            # Generate embedding
            query_embedding = self._generate_embedding(description)
            
            # Search for similar vitals
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
            similar_vitals = []
            for result in search_results.points:
                similar_vitals.append({
                    "id": result.id,
                    "score": result.score,
                    "timestamp": result.payload.get("timestamp", ""),
                    "vitals": result.payload.get("vitals", {}),
                    "description": result.payload.get("description", ""),
                    "anomalies": result.payload.get("anomalies", []),
                    "severity": result.payload.get("severity", "normal")
                })
            
            logger.info(f"✅ Found {len(similar_vitals)} similar vitals patterns for patient {patient_id}")
            return similar_vitals
            
        except Exception as e:
            logger.error(f"❌ Error finding similar vitals: {e}")
            return []
    
    def generate_trend_analysis(
        self,
        patient_id: str,
        days: int = 30
    ) -> Dict:
        """
        Generate comprehensive trend analysis for patient vitals
        
        Args:
            patient_id: Unique identifier for the patient
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis, statistics, and alerts
        """
        try:
            # Get vitals history
            history = self.get_vitals_history(patient_id, days=days, limit=1000)
            
            if not history:
                return {
                    "patient_id": patient_id,
                    "days_analyzed": days,
                    "total_readings": 0,
                    "message": "No vitals data available for analysis"
                }
            
            # Aggregate vitals data
            vitals_data = {}
            for record in history:
                for vital_name, value in record['vitals'].items():
                    if vital_name == 'notes':
                        continue
                    if vital_name not in vitals_data:
                        vitals_data[vital_name] = []
                    vitals_data[vital_name].append({
                        'value': value,
                        'timestamp': record['timestamp']
                    })
            
            # Calculate statistics and trends for each vital
            trends = {}
            alerts = []
            
            for vital_name, values_list in vitals_data.items():
                if not values_list:
                    continue
                
                values = [v['value'] for v in values_list]
                
                # Calculate statistics
                stats = {
                    "count": len(values),
                    "mean": round(statistics.mean(values), 2),
                    "median": round(statistics.median(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[0] if values else None  # Most recent first
                }
                
                if len(values) > 1:
                    stats["std_dev"] = round(statistics.stdev(values), 2)
                    
                    # Calculate trend (simple linear trend)
                    # Compare recent half vs older half
                    mid_point = len(values) // 2
                    recent_avg = statistics.mean(values[:mid_point]) if mid_point > 0 else values[0]
                    older_avg = statistics.mean(values[mid_point:]) if len(values[mid_point:]) > 0 else values[-1]
                    
                    trend_direction = "stable"
                    trend_percentage = 0
                    
                    if older_avg != 0:
                        trend_percentage = round(((recent_avg - older_avg) / older_avg) * 100, 2)
                        
                        if abs(trend_percentage) > 10:
                            trend_direction = "increasing" if trend_percentage > 0 else "decreasing"
                        elif abs(trend_percentage) > 5:
                            trend_direction = "slightly_increasing" if trend_percentage > 0 else "slightly_decreasing"
                    
                    stats["trend"] = {
                        "direction": trend_direction,
                        "percentage": trend_percentage
                    }
                
                # Check if current values are in normal range
                if vital_name in self.NORMAL_RANGES:
                    normal_min, normal_max = self.NORMAL_RANGES[vital_name]
                    stats["normal_range"] = f"{normal_min}-{normal_max}"
                    stats["in_normal_range"] = normal_min <= stats["latest"] <= normal_max
                    
                    # Check for persistent anomalies
                    recent_values = values[:5] if len(values) >= 5 else values
                    out_of_range = sum(1 for v in recent_values if v < normal_min or v > normal_max)
                    
                    if out_of_range >= 3:
                        alerts.append({
                            "type": "persistent_anomaly",
                            "vital": vital_name,
                            "message": f"{vital_name.replace('_', ' ').title()} has been out of normal range in {out_of_range} of last {len(recent_values)} readings",
                            "severity": "warning"
                        })
                
                trends[vital_name] = stats
            
            # Count anomalies
            total_anomalies = sum(1 for r in history if r.get('anomalies', []))
            critical_readings = sum(1 for r in history if r.get('severity') == 'critical')
            
            analysis = {
                "patient_id": patient_id,
                "days_analyzed": days,
                "total_readings": len(history),
                "total_anomalies": total_anomalies,
                "critical_readings": critical_readings,
                "trends": trends,
                "alerts": alerts,
                "latest_reading": history[0] if history else None,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Generated trend analysis for patient {patient_id}: {len(history)} readings, {total_anomalies} anomalies")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error generating trend analysis: {e}")
            return {
                "patient_id": patient_id,
                "error": str(e)
            }
    
    def get_anomalous_readings(
        self,
        patient_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get all anomalous readings for a patient
        
        Args:
            patient_id: Unique identifier for the patient
            days: Number of days to look back
            
        Returns:
            List of anomalous vitals records
        """
        try:
            # Get history
            history = self.get_vitals_history(patient_id, days=days)
            
            # Filter for anomalies
            anomalous = [r for r in history if r.get('anomalies', [])]
            
            # Sort by severity
            severity_order = {'critical': 0, 'warning': 1, 'normal': 2}
            anomalous.sort(key=lambda x: (
                severity_order.get(x.get('severity', 'normal'), 3),
                x['timestamp']
            ), reverse=True)
            
            logger.info(f"✅ Found {len(anomalous)} anomalous readings for patient {patient_id}")
            return anomalous
            
        except Exception as e:
            logger.error(f"❌ Error getting anomalous readings: {e}")
            return []
    
    def delete_patient_vitals(self, patient_id: str) -> int:
        """
        Delete all vitals data for a patient (GDPR compliance)
        
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
                limit=10000
            )
            
            # Delete all records
            point_ids = [record.id for record in records]
            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
            
            logger.info(f"✅ Deleted {len(point_ids)} vitals records for patient {patient_id}")
            return len(point_ids)
            
        except Exception as e:
            logger.error(f"❌ Error deleting patient vitals: {e}")
            return 0


# Singleton instance
_vitals_tracker = None

def get_vitals_tracker() -> VitalsTracker:
    """Get or create the singleton VitalsTracker instance"""
    global _vitals_tracker
    if _vitals_tracker is None:
        _vitals_tracker = VitalsTracker()
    return _vitals_tracker
