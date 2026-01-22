# Medical Knowledge Base Documentation

## Overview

The Medical Knowledge Base is a searchable database of 21+ chronic medical conditions powered by Qdrant vector database and semantic search. It enables users to ask natural language health questions and receive relevant medical information with confidence scores.

**Last Updated**: December 2024  
**Status**: ✅ Fully Operational

---

## Features

### ✨ Core Capabilities

1. **Semantic Search** - Ask natural language questions and get relevant medical conditions
2. **Confidence Scoring** - Each result includes a confidence score (0-1) and relevance level
3. **Comprehensive Information** - Each condition includes:
   - Symptoms
   - Risk factors
   - Treatments
   - Care guidelines
   - Complications
4. **Category Filtering** - Browse conditions by medical category
5. **Detailed Condition Views** - Get in-depth information about specific conditions

### 🏥 Medical Conditions Included (21 Total)

#### Metabolic & Endocrine
- Type 2 Diabetes
- Hypothyroidism

#### Cardiovascular
- Hypertension (High Blood Pressure)
- Congestive Heart Failure
- Stroke

#### Respiratory
- COPD (Chronic Obstructive Pulmonary Disease)
- Asthma
- Obstructive Sleep Apnea

#### Musculoskeletal & Autoimmune
- Rheumatoid Arthritis
- Osteoarthritis
- Fibromyalgia
- Systemic Lupus Erythematosus (SLE)
- Psoriasis

#### Mental Health
- Major Depressive Disorder
- Generalized Anxiety Disorder

#### Neurological
- Parkinson's Disease
- Alzheimer's Disease
- Migraine

#### Gastrointestinal & Renal
- GERD (Gastroesophageal Reflux Disease)
- IBS (Irritable Bowel Syndrome)
- Chronic Kidney Disease

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (TypeScript)                     │
│  src/api/medical-knowledge.ts - API Client                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────────┐
│                    Backend (Flask)                           │
│  app.py - 4 API Endpoints                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            Medical Knowledge Base Module                     │
│  medical_knowledge_base.py                                  │
│  - MedicalKnowledgeBase class                               │
│  - 21 chronic conditions with embeddings                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Qdrant Vector Database                       │
│  - Collection: medical_knowledge                            │
│  - 384-dimensional embeddings (all-MiniLM-L6-v2)           │
│  - Cosine similarity search                                 │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Vector Database**: Qdrant (in-memory mode for development)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Backend Framework**: Flask with Python 3.12.5
- **API**: RESTful endpoints
- **Frontend**: TypeScript with type-safe interfaces

---

## API Reference

### Base URL
```
http://localhost:5000/api/knowledge
```

### Endpoints

#### 1. Semantic Search
```http
GET /api/knowledge/search?query={query}&limit={limit}
```

**Query Parameters:**
- `query` (required): Natural language health question
- `limit` (optional): Number of results to return (default: 3)

**Example Request:**
```bash
curl "http://localhost:5000/api/knowledge/search?query=how%20to%20manage%20high%20blood%20sugar&limit=3"
```

**Example Response:**
```json
{
  "success": true,
  "query": "how to manage high blood sugar",
  "results_count": 3,
  "results": [
    {
      "condition_key": "diabetes_type2",
      "name": "Type 2 Diabetes",
      "category": "Metabolic Disorder",
      "description": "A chronic condition affecting...",
      "symptoms": ["Increased thirst and frequent urination", "..."],
      "risk_factors": ["Being overweight or obese", "..."],
      "treatments": ["Blood sugar monitoring - Regular glucose testing", "..."],
      "care_guidelines": ["Monitor blood sugar levels as recommended", "..."],
      "complications": ["Heart disease and stroke", "..."],
      "confidence_score": 0.545,
      "relevance": "medium"
    }
  ]
}
```

**Confidence Scores:**
- `high`: > 0.7 (Strong match)
- `medium`: 0.5 - 0.7 (Good match)
- `low`: < 0.5 (Weak match)

---

#### 2. List All Conditions
```http
GET /api/knowledge/conditions
```

**Example Request:**
```bash
curl "http://localhost:5000/api/knowledge/conditions"
```

**Example Response:**
```json
{
  "success": true,
  "total_conditions": 21,
  "conditions": [
    {
      "key": "diabetes_type2",
      "name": "Type 2 Diabetes",
      "category": "Metabolic Disorder",
      "description": "A chronic condition affecting..."
    }
  ]
}
```

---

#### 3. Get Condition Details
```http
GET /api/knowledge/condition/{condition_key}
```

**Path Parameters:**
- `condition_key`: Condition identifier (e.g., `diabetes_type2`, `hypertension`)

**Example Request:**
```bash
curl "http://localhost:5000/api/knowledge/condition/diabetes_type2"
```

**Example Response:**
```json
{
  "success": true,
  "condition": {
    "name": "Type 2 Diabetes",
    "category": "Metabolic Disorder",
    "description": "A chronic condition affecting how the body processes blood sugar...",
    "symptoms": [
      "Increased thirst and frequent urination",
      "Increased hunger",
      "Unintended weight loss"
    ],
    "risk_factors": [
      "Being overweight or obese",
      "Family history of diabetes"
    ],
    "treatments": [
      "Blood sugar monitoring - Regular glucose testing",
      "Metformin - First-line medication to control blood sugar"
    ],
    "care_guidelines": [
      "Monitor blood sugar levels as recommended by doctor",
      "Take medications as prescribed"
    ],
    "complications": [
      "Heart disease and stroke",
      "Kidney disease (nephropathy)"
    ]
  }
}
```

---

#### 4. Search by Category
```http
GET /api/knowledge/category/{category}
```

**Path Parameters:**
- `category`: Medical category name (e.g., `Mental Health`, `Cardiovascular`)

**Available Categories:**
- Metabolic Disorder
- Cardiovascular
- Respiratory
- Autoimmune/Musculoskeletal
- Musculoskeletal
- Mental Health
- Renal
- Neurological
- Endocrine
- Gastrointestinal
- Musculoskeletal/Chronic Pain
- Autoimmune
- Autoimmune/Dermatological
- Respiratory/Sleep Disorder

**Example Request:**
```bash
curl "http://localhost:5000/api/knowledge/category/Mental%20Health"
```

**Example Response:**
```json
{
  "success": true,
  "category": "Mental Health",
  "total_conditions": 2,
  "conditions": [
    {
      "key": "depression",
      "name": "Major Depressive Disorder",
      "category": "Mental Health",
      "description": "A mood disorder causing persistent feelings..."
    },
    {
      "key": "anxiety_disorder",
      "name": "Generalized Anxiety Disorder",
      "category": "Mental Health",
      "description": "A mental health condition characterized by..."
    }
  ]
}
```

---

## Frontend Integration

### TypeScript API Client

Import the medical knowledge API client:

```typescript
import {
  searchMedicalKnowledge,
  getAllConditions,
  getConditionDetails,
  searchByCategory,
  getAvailableCategories,
  formatConfidenceScore,
  getRelevanceBadgeColor,
  getCategoryIcon,
  isMedicalKnowledgeAvailable
} from '@/api/medical-knowledge';
```

### Usage Examples

#### 1. Semantic Search
```typescript
// Search for conditions related to a health question
const searchResults = await searchMedicalKnowledge(
  'how to manage high blood sugar',
  3 // limit
);

console.log(`Found ${searchResults.results_count} conditions`);
searchResults.results.forEach(result => {
  console.log(`${result.name} - Confidence: ${result.confidence_score}`);
  console.log(`Relevance: ${result.relevance}`);
});
```

#### 2. List All Conditions
```typescript
const { conditions, total_conditions } = await getAllConditions();
console.log(`Total: ${total_conditions} conditions`);
conditions.forEach(c => console.log(`${c.name} (${c.category})`));
```

#### 3. Get Condition Details
```typescript
const { condition } = await getConditionDetails('diabetes_type2');
console.log(`Condition: ${condition.name}`);
console.log(`Treatments: ${condition.treatments.length}`);
condition.symptoms.forEach(s => console.log(`- ${s}`));
```

#### 4. Search by Category
```typescript
const { conditions } = await searchByCategory('Mental Health');
console.log(`Mental Health Conditions: ${conditions.length}`);
```

#### 5. Utility Functions
```typescript
// Format confidence score
const score = 0.703;
console.log(formatConfidenceScore(score)); // "70%"

// Get badge color for UI
const color = getRelevanceBadgeColor('high');
// Returns: "bg-green-100 text-green-800 border-green-200"

// Get category icon
const icon = getCategoryIcon('Cardiovascular');
console.log(icon); // "❤️"

// Check availability
const isAvailable = await isMedicalKnowledgeAvailable();
console.log(isAvailable); // true
```

---

## Component Example

### React Component with Medical Knowledge Search

```typescript
import React, { useState } from 'react';
import {
  searchMedicalKnowledge,
  SearchResult,
  formatConfidenceScore,
  getRelevanceBadgeColor,
  getCategoryIcon
} from '@/api/medical-knowledge';

export function MedicalKnowledgeSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await searchMedicalKnowledge(query, 3);
      setResults(response.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a health question..."
          className="flex-1 px-4 py-2 border rounded"
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="space-y-4">
        {results.map((result, index) => (
          <div key={index} className="border rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">
                  {getCategoryIcon(result.category)}
                </span>
                <div>
                  <h3 className="text-lg font-semibold">{result.name}</h3>
                  <p className="text-sm text-gray-600">{result.category}</p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span
                  className={`px-2 py-1 text-xs rounded border ${getRelevanceBadgeColor(
                    result.relevance
                  )}`}
                >
                  {result.relevance.toUpperCase()}
                </span>
                <span className="text-sm text-gray-600">
                  {formatConfidenceScore(result.confidence_score)}
                </span>
              </div>
            </div>

            <p className="text-sm text-gray-700 mb-3">
              {result.description}
            </p>

            <div className="space-y-2">
              <div>
                <h4 className="font-semibold text-sm mb-1">Key Symptoms:</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {result.symptoms.slice(0, 3).map((symptom, i) => (
                    <li key={i} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{symptom}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-sm mb-1">Treatments:</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {result.treatments.slice(0, 3).map((treatment, i) => (
                    <li key={i} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{treatment}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Testing

### Run Tests

```bash
cd backend
python test_medical_knowledge.py
```

### Test Coverage

The test suite validates:

1. ✅ **Initialization** - Knowledge base loads with 21 conditions
2. ✅ **List All Conditions** - Retrieves complete condition list
3. ✅ **Semantic Search** - 5 different health queries:
   - Blood sugar management
   - Heart disease symptoms
   - Mental health concerns
   - Joint pain
   - Breathing problems
4. ✅ **Confidence Scores** - Verifies relevance ranking (high/medium/low)
5. ✅ **Condition Details** - Retrieves specific condition information
6. ✅ **Category Filtering** - Filters by medical category
7. ✅ **Confidence Analysis** - Tests varied query types

### Test Results

```
✅ ALL TESTS COMPLETED SUCCESSFULLY!

📊 Test Summary:
  • Total conditions in knowledge base: 21
  • Semantic search tests: 5 passed
  • Condition retrieval: 1 passed
  • Category filtering: 2 passed
  • Confidence score analysis: 1 passed

💡 Key Features Verified:
  ✓ Semantic search with confidence scores
  ✓ Comprehensive condition information
  ✓ Category-based filtering
  ✓ Relevance ranking (high/medium/low)
  ✓ Top 3 results with detailed information
  ✓ 21+ chronic conditions available
```

---

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# Qdrant Configuration (optional - defaults to in-memory)
QDRANT_URL=http://localhost:6333  # For Qdrant server
QDRANT_API_KEY=your-api-key       # If using Qdrant Cloud
```

### In-Memory Mode (Default)

The knowledge base uses Qdrant in-memory mode by default, which is perfect for:
- Development
- Testing
- Single-instance deployments
- Small to medium workloads

### Production Mode with Qdrant Server

For production, use a Qdrant server:

1. **Install Qdrant**:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **Configure environment**:
   ```bash
   QDRANT_URL=http://localhost:6333
   ```

3. **Restart backend**:
   ```bash
   python app.py
   ```

---

## Performance

### Metrics

- **Initialization Time**: ~6 seconds (includes model loading and 21 embeddings)
- **Search Speed**: 40-140 queries/second
- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Memory Usage**: ~500MB (includes model + vectors)
- **Database Size**: 21 conditions with full embeddings

### Optimization Tips

1. **Singleton Pattern**: Knowledge base uses singleton to avoid re-initialization
2. **Batch Embeddings**: All conditions embedded during initialization
3. **In-Memory Search**: Fast cosine similarity without disk I/O
4. **Result Limiting**: Default limit of 3 results reduces overhead

---

## Error Handling

### Common Errors

#### 1. Knowledge Base Not Available
```json
{
  "error": "Medical knowledge base not available",
  "success": false
}
```
**Solution**: Ensure `sentence-transformers` is installed and backend is running

#### 2. Condition Not Found
```json
{
  "error": "Condition 'invalid_key' not found",
  "success": false
}
```
**Solution**: Use valid condition keys from the conditions list

#### 3. Missing Query Parameter
```json
{
  "error": "Query parameter is required",
  "success": false
}
```
**Solution**: Include `query` parameter in search requests

---

## Extending the Knowledge Base

### Adding New Conditions

Edit `backend/medical_knowledge_base.py`:

```python
MEDICAL_CONDITIONS = {
    # ... existing conditions ...
    
    "new_condition_key": {
        "name": "Condition Name",
        "category": "Category",
        "description": "Full description...",
        "symptoms": ["Symptom 1", "Symptom 2"],
        "risk_factors": ["Risk 1", "Risk 2"],
        "treatments": ["Treatment 1", "Treatment 2"],
        "care_guidelines": ["Guideline 1", "Guideline 2"],
        "complications": ["Complication 1", "Complication 2"]
    }
}
```

The knowledge base will automatically:
1. Generate embeddings for the new condition
2. Add it to the Qdrant collection
3. Make it searchable via semantic search
4. Include it in category filtering

---

## Best Practices

### 1. Query Optimization
- Use natural language questions
- Be specific about symptoms or concerns
- Examples:
  - ✅ "What are symptoms of high blood pressure?"
  - ✅ "How to manage joint pain in the morning?"
  - ❌ "heart" (too vague)

### 2. Result Interpretation
- **High confidence (>0.7)**: Strong match, highly relevant
- **Medium confidence (0.5-0.7)**: Good match, relevant
- **Low confidence (<0.5)**: Weak match, may not be relevant

### 3. Error Handling
Always wrap API calls in try-catch:
```typescript
try {
  const results = await searchMedicalKnowledge(query);
  // Handle results
} catch (error) {
  // Handle error
  console.error('Search failed:', error);
}
```

### 4. User Experience
- Show confidence scores to users
- Use relevance badges (high/medium/low)
- Display category icons for visual context
- Limit results to top 3 for clarity

---

## Troubleshooting

### Issue: Slow Search Performance

**Symptoms**: Searches take >1 second

**Solutions**:
1. Use Qdrant server instead of in-memory
2. Reduce result limit
3. Check system resources (CPU/RAM)

---

### Issue: Low Confidence Scores

**Symptoms**: All results have confidence <0.5

**Solutions**:
1. Rephrase query to be more specific
2. Use medical terminology when appropriate
3. Try different phrasings

---

### Issue: No Results Found

**Symptoms**: Empty results array

**Solutions**:
1. Check if knowledge base is initialized
2. Verify backend is running
3. Try broader query terms

---

## Security & Privacy

### Data Storage
- All medical conditions are **static knowledge** (not patient data)
- No user queries are stored by default
- No personally identifiable information (PII)

### Compliance
- Medical information is **educational only**
- Not a substitute for professional medical advice
- Encourage users to consult healthcare providers

### Recommendations
- Add disclaimer in UI about medical advice
- Log queries only if necessary and with consent
- Implement rate limiting for public APIs

---

## Support & Maintenance

### Regular Updates
- Review medical information quarterly
- Update treatments with new medical guidelines
- Add new chronic conditions as needed

### Monitoring
- Track query patterns for common health questions
- Monitor confidence score distributions
- Identify gaps in medical coverage

---

## Related Documentation

- [Patient Memory System](PATIENT_MEMORY_README.md) - Conversation history and context
- [Vitals Tracking](VITALS_TRACKING_README.md) - Health metrics monitoring
- [Backend API](backend/README.md) - Complete API documentation

---

## Version History

### v1.0.0 (December 2024)
- ✅ Initial release with 21 chronic conditions
- ✅ Semantic search with confidence scores
- ✅ Category filtering
- ✅ Full TypeScript API client
- ✅ Comprehensive test coverage

---

## License

Part of CareMate healthcare application.  
For internal use only.

---

## Contact

For questions or issues with the medical knowledge base:
- Technical: See backend logs
- Medical Content: Consult healthcare professionals
- Feature Requests: Contact development team
