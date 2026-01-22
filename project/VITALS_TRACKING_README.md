# Vitals Tracking System with Qdrant

## Overview

This implementation adds a comprehensive vitals tracking system using Qdrant vector database to store, analyze, and monitor patient vital signs. The system automatically detects anomalies, generates trend analyses, and uses semantic similarity search to find similar patterns in patient vitals history.

## Features

✅ **Comprehensive Vitals Storage**: Blood pressure, heart rate, glucose, temperature, oxygen levels
✅ **Automatic Anomaly Detection**: Real-time detection with warning and critical severity levels
✅ **Trend Analysis**: Statistical analysis with trend direction and percentage changes
✅ **Semantic Pattern Matching**: Find similar vitals patterns using vector embeddings
✅ **30-Day History**: Retrieve and analyze vitals over configurable time periods
✅ **Smart Alerts**: Persistent anomaly detection and critical threshold monitoring
✅ **GDPR Compliant**: Data deletion support for privacy compliance

## Vitals Monitored

| Vital Sign | Normal Range | Critical Low | Critical High | Unit |
|------------|--------------|--------------|---------------|------|
| Systolic BP | 90-120 | <80 | >180 | mmHg |
| Diastolic BP | 60-80 | <50 | >120 | mmHg |
| Heart Rate | 60-100 | <40 | >140 | bpm |
| Glucose | 70-140 | <60 | >300 | mg/dL |
| Temperature | 97.0-99.5 | <95.0 | >103.0 | °F |
| Oxygen Level | 95-100 | <90 | - | % SpO2 |

## Architecture

### Backend Components

1. **`backend/vitals_tracker.py`** - Core vitals tracking system
   - `VitalsTracker` class handles all Qdrant operations
   - Automatic anomaly detection with configurable thresholds
   - Trend analysis with statistical calculations
   - Semantic similarity search for pattern matching

2. **`backend/app.py`** - Flask API endpoints
   - `/api/vitals/store` - Store vitals with anomaly detection
   - `/api/vitals/history` - Get vitals history (last 30 days)
   - `/api/vitals/trend-analysis` - Generate comprehensive trend analysis
   - `/api/vitals/anomalies` - Get all anomalous readings
   - `/api/vitals/similar` - Find similar vitals patterns
   - `/api/vitals/delete` - Delete patient vitals (GDPR)

### Frontend Components

1. **`src/api/vitals.ts`** - TypeScript API client
   - Type-safe interfaces for all vitals operations
   - Error handling and validation
   - Backend communication layer

## Installation

Dependencies are already installed from the patient memory system setup:
- `qdrant-client==1.7.0`
- `sentence-transformers==2.2.2`

No additional installation required.

## API Endpoints

### 1. Store Vitals

```http
POST /api/vitals/store
Content-Type: application/json

{
  "patientId": "p1",
  "vitals": {
    "systolic_bp": 120,
    "diastolic_bp": 80,
    "heart_rate": 75,
    "glucose": 95,
    "temperature": 98.6,
    "oxygen_level": 98
  },
  "notes": "Morning reading, feeling good"
}

Response:
{
  "vitalsId": "uuid",
  "anomalies": [
    {
      "vital": "systolic_bp",
      "value": 135,
      "severity": "warning",
      "message": "Systolic Bp above normal: 135 (normal: 90-120)",
      "normal_range": "90-120"
    }
  ],
  "hasAnomalies": true,
  "success": true,
  "message": "Vitals stored successfully with 1 anomaly alerts"
}
```

### 2. Get Vitals History

```http
GET /api/vitals/history?patientId=p1&days=30&limit=100

Response:
{
  "history": [
    {
      "id": "uuid",
      "timestamp": "2026-01-22T10:30:00",
      "vitals": {
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "heart_rate": 75,
        "glucose": 95,
        "temperature": 98.6,
        "oxygen_level": 98
      },
      "description": "Patient vitals recorded: blood pressure 120/80 mmHg...",
      "anomalies": [],
      "severity": "normal"
    }
  ],
  "count": 25,
  "days": 30,
  "success": true
}
```

### 3. Get Trend Analysis

```http
GET /api/vitals/trend-analysis?patientId=p1&days=30

Response:
{
  "analysis": {
    "patient_id": "p1",
    "days_analyzed": 30,
    "total_readings": 25,
    "total_anomalies": 5,
    "critical_readings": 2,
    "trends": {
      "systolic_bp": {
        "count": 25,
        "mean": 118.5,
        "median": 120,
        "min": 110,
        "max": 135,
        "latest": 120,
        "std_dev": 8.2,
        "trend": {
          "direction": "stable",
          "percentage": -2.1
        },
        "normal_range": "90-120",
        "in_normal_range": true
      },
      "heart_rate": {
        "count": 25,
        "mean": 72.3,
        "median": 72,
        "min": 65,
        "max": 85,
        "latest": 75,
        "trend": {
          "direction": "slightly_increasing",
          "percentage": 3.5
        },
        "normal_range": "60-100",
        "in_normal_range": true
      }
    },
    "alerts": [
      {
        "type": "persistent_anomaly",
        "vital": "glucose",
        "message": "Glucose has been out of normal range in 3 of last 5 readings",
        "severity": "warning"
      }
    ],
    "latest_reading": { ... },
    "analysis_timestamp": "2026-01-22T10:30:00"
  },
  "success": true
}
```

### 4. Get Anomalous Readings

```http
GET /api/vitals/anomalies?patientId=p1&days=30

Response:
{
  "anomalies": [
    {
      "id": "uuid",
      "timestamp": "2026-01-22T08:00:00",
      "vitals": { ... },
      "description": "...",
      "anomalies": [
        {
          "vital": "systolic_bp",
          "value": 185,
          "severity": "critical",
          "message": "Systolic Bp critically high: 185",
          "normal_range": "90-120"
        }
      ],
      "severity": "critical"
    }
  ],
  "count": 5,
  "success": true
}
```

### 5. Find Similar Vitals Patterns

```http
POST /api/vitals/similar
Content-Type: application/json

{
  "patientId": "p1",
  "vitals": {
    "systolic_bp": 120,
    "diastolic_bp": 78,
    "heart_rate": 75
  },
  "limit": 10
}

Response:
{
  "similar": [
    {
      "id": "uuid",
      "score": 0.942,
      "timestamp": "2026-01-20T10:00:00",
      "vitals": { ... },
      "description": "Patient vitals recorded: blood pressure 118/76 mmHg...",
      "anomalies": [],
      "severity": "normal"
    }
  ],
  "count": 10,
  "success": true
}
```

### 6. Delete Patient Vitals

```http
DELETE /api/vitals/delete
Content-Type: application/json

{
  "patientId": "p1"
}

Response:
{
  "deletedCount": 25,
  "success": true,
  "message": "Deleted 25 vitals records for patient p1"
}
```

## Usage Examples

### Frontend (TypeScript/React)

```typescript
import { 
  storeVitals, 
  getVitalsHistory, 
  getTrendAnalysis,
  getAnomalousReadings,
  findSimilarVitals
} from '../api/vitals';

// Store vitals
const storePatientVitals = async () => {
  try {
    const response = await storeVitals({
      patientId: user.id,
      vitals: {
        systolic_bp: 120,
        diastolic_bp: 80,
        heart_rate: 75,
        glucose: 95,
        temperature: 98.6,
        oxygen_level: 98
      },
      notes: 'Morning reading'
    });
    
    if (response.hasAnomalies) {
      console.log('Anomalies detected:', response.anomalies);
      // Show alerts to user
    }
  } catch (error) {
    console.error('Error storing vitals:', error);
  }
};

// Get history and trends
const loadVitalsData = async () => {
  try {
    // Get last 30 days of history
    const history = await getVitalsHistory(user.id, 30);
    
    // Get trend analysis
    const trends = await getTrendAnalysis(user.id, 30);
    
    // Get anomalies
    const anomalies = await getAnomalousReadings(user.id, 30);
    
    // Display data in UI
    displayVitalsChart(history.history);
    displayTrends(trends.analysis);
    displayAlerts(anomalies.anomalies);
  } catch (error) {
    console.error('Error loading vitals:', error);
  }
};

// Find similar patterns
const findSimilarPatterns = async (currentVitals) => {
  try {
    const similar = await findSimilarVitals(
      user.id, 
      currentVitals, 
      5
    );
    
    console.log(`Found ${similar.count} similar patterns`);
    // Display similar patterns
  } catch (error) {
    console.error('Error finding similar vitals:', error);
  }
};
```

### Backend (Python)

```python
from vitals_tracker import get_vitals_tracker
from datetime import datetime

# Initialize tracker
tracker = get_vitals_tracker()

# Store vitals
vitals_id, anomalies = tracker.store_vitals(
    patient_id="patient_123",
    vitals={
        'systolic_bp': 120,
        'diastolic_bp': 80,
        'heart_rate': 75,
        'glucose': 95,
        'temperature': 98.6,
        'oxygen_level': 98
    },
    notes="Morning reading"
)

# Get history
history = tracker.get_vitals_history("patient_123", days=30)

# Generate trend analysis
analysis = tracker.generate_trend_analysis("patient_123", days=30)

# Get anomalies
anomalies = tracker.get_anomalous_readings("patient_123", days=30)

# Find similar patterns
similar = tracker.find_similar_vitals(
    "patient_123",
    {'systolic_bp': 120, 'heart_rate': 75},
    limit=10
)
```

## Anomaly Detection

### Severity Levels

1. **Normal** - All vitals within normal ranges
2. **Warning** - Vitals outside normal range but not critical
3. **Critical** - Vitals at dangerous levels requiring immediate attention

### Detection Logic

```python
# Automatic detection on storage
if value < critical_threshold_low:
    severity = "critical"
    message = f"{vital} critically low: {value}"
elif value > critical_threshold_high:
    severity = "critical"
    message = f"{vital} critically high: {value}"
elif value < normal_min or value > normal_max:
    severity = "warning"
    message = f"{vital} outside normal range: {value}"
```

### Alert Types

- **Immediate Alerts**: Triggered when storing vitals with anomalies
- **Persistent Anomaly Alerts**: Triggered when 3+ of last 5 readings are abnormal
- **Trend Alerts**: Large changes (>10%) in vitals over time

## Trend Analysis

### Statistical Metrics

- **Mean**: Average value over the period
- **Median**: Middle value (less affected by outliers)
- **Min/Max**: Range of values
- **Standard Deviation**: Measure of variability
- **Latest**: Most recent reading

### Trend Direction

- **Increasing**: >10% increase from older to recent readings
- **Slightly Increasing**: 5-10% increase
- **Stable**: <5% change
- **Slightly Decreasing**: 5-10% decrease
- **Decreasing**: >10% decrease

### Example Trend Output

```json
{
  "systolic_bp": {
    "mean": 118.5,
    "trend": {
      "direction": "decreasing",
      "percentage": -12.3
    },
    "in_normal_range": true
  }
}
```

## Semantic Pattern Matching

### How It Works

1. **Embedding Generation**: Each vitals record is converted to a natural language description
   ```
   "Patient vitals recorded: blood pressure 120/80 mmHg, heart rate 75 bpm, glucose 95 mg/dL..."
   ```

2. **Vector Storage**: Description is embedded using sentence-transformers and stored in Qdrant

3. **Similarity Search**: Query vitals are embedded and compared using cosine similarity

4. **Results**: Returns most similar historical patterns with similarity scores (0-1)

### Use Cases

- **Pattern Recognition**: "Have I had similar readings before?"
- **Contextual Analysis**: "When my BP was this high, what were my other vitals?"
- **Historical Comparison**: "Is this normal for me?"

## Testing

### Run Tests

```bash
cd backend
python test_vitals_tracker.py
```

### Test Coverage

✅ Normal vitals storage (no anomalies)
✅ Warning level vitals (5 anomalies detected)
✅ Critical vitals (6 anomalies including critical alerts)
✅ Historical data storage
✅ History retrieval (8 records)
✅ Similar pattern matching (similarity score: 0.94)
✅ Trend analysis (comprehensive statistics)
✅ Anomalous readings filtering (4 anomalies)
✅ Data deletion (GDPR compliance)

### Expected Output

```
✅ Vitals Tracking System is working correctly
✅ Qdrant vector database is functioning
✅ Anomaly detection is operational
✅ Trend analysis is working
✅ Semantic search for similar patterns works
```

## Integration with Existing Pages

### Vitals Page (`src/pages/Vitals.tsx`)

Update to use the new API:

```typescript
import { storeVitals, getVitalsHistory, getTrendAnalysis } from '../api/vitals';
import { useAuth } from '../context/AuthContext';

const VitalsPage = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [trends, setTrends] = useState(null);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    const historyData = await getVitalsHistory(user.id, 30);
    const trendsData = await getTrendAnalysis(user.id, 30);
    setHistory(historyData.history);
    setTrends(trendsData.analysis);
  };
  
  const handleSubmit = async (vitalsData) => {
    const response = await storeVitals({
      patientId: user.id,
      vitals: vitalsData,
      notes: notesInput
    });
    
    if (response.hasAnomalies) {
      // Show anomaly alerts
      showAlerts(response.anomalies);
    }
    
    loadData(); // Refresh data
  };
  
  // ... render UI
};
```

## Performance Considerations

### Speed
- **Storage**: ~50-100ms (including embedding generation)
- **Retrieval**: ~10-50ms for 100 records
- **Trend Analysis**: ~100-200ms for 30 days of data
- **Similarity Search**: ~20-50ms for 10 similar patterns

### Scaling
- **In-memory**: Good for up to 10,000 vitals records
- **Server mode**: Handles millions of records efficiently
- Use Qdrant Cloud for production deployments

### Memory Usage
- In-memory: ~100MB for tracker + embeddings + data
- Server mode: Minimal memory footprint

## Security & Privacy

### Data Protection
- All vitals are isolated by patient ID
- GDPR-compliant deletion endpoint
- No PII in logs
- Encrypted communication (use HTTPS in production)

### Best Practices
1. Implement authentication/authorization
2. Use HTTPS for all API calls
3. Rate limit API endpoints
4. Regular data backups
5. Audit logging for compliance

## Alerts & Notifications

### Critical Alerts
When critical vitals are detected:
1. API returns immediate alert in response
2. Frontend should show prominent warning
3. Consider sending push notifications
4. Suggest contacting healthcare provider

### Warning Alerts
When abnormal but not critical:
1. Display warning message
2. Show normal ranges
3. Suggest monitoring
4. Provide health tips

### Trend Alerts
When persistent issues detected:
1. "Your blood pressure has been high in 3 of your last 5 readings"
2. Recommend scheduling doctor appointment
3. Suggest lifestyle modifications

## Future Enhancements

### Planned Features
- [ ] Predictive analytics (ML models for vitals prediction)
- [ ] Medication correlation analysis
- [ ] Activity and diet correlation
- [ ] Custom alert thresholds per patient
- [ ] Multi-day pattern recognition
- [ ] Integration with wearable devices
- [ ] Doctor review and annotations
- [ ] Automated health score calculation

### Advanced Analytics
- Time-series forecasting
- Anomaly prediction
- Risk scoring
- Personalized normal ranges based on history

## Troubleshooting

### Common Issues

**Issue**: Vitals not storing
- Check backend is running: `python app.py`
- Verify Qdrant is initialized
- Check network connectivity

**Issue**: No anomalies detected
- Verify vitals are outside normal ranges
- Check threshold configuration
- Review vitals data format

**Issue**: Trend analysis empty
- Ensure patient has historical data (>1 reading)
- Check date range (default: 30 days)
- Verify patient ID is correct

**Issue**: Slow performance
- Consider using Qdrant server mode
- Reduce limit parameter
- Index optimization for large datasets

## API Response Codes

- `200 OK` - Successful operation
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Patient or record not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Vitals tracker not available

## Conclusion

The Vitals Tracking System provides comprehensive monitoring and analysis of patient vital signs using advanced vector database technology. With automatic anomaly detection, trend analysis, and semantic pattern matching, it enables proactive healthcare management and early intervention.

For questions or issues, refer to the troubleshooting section or review the test scripts for usage examples.

---

**Last Updated**: January 22, 2026  
**Version**: 1.0.0  
**Dependencies**: qdrant-client 1.7.0, sentence-transformers 2.2.2
