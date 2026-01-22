# 🏗️ Architecture Documentation

## System Architecture Overview

Healthcare Memory Agent follows a modern **microservices architecture** with a React frontend and Flask backend, powered by Qdrant vector database for semantic search capabilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│                    React 18 + TypeScript                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Components: Dashboard, AI Chat, Skin Analysis, Vitals  │  │
│  │  State: React Context API + Custom Hooks                │  │
│  │  Routing: React Router v6                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API (JSON)
                              │ HTTP/HTTPS
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          Backend Layer                          │
│                      Flask 2.3.3 + Python 3.11                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints (11 routes)                               │  │
│  │  ├─ /chat                (Patient memory)                │  │
│  │  ├─ /skin-analysis       (CLIP embeddings)              │  │
│  │  ├─ /audio-analysis      (Wav2Vec2 embeddings)          │  │
│  │  ├─ /similar-cases       (Hybrid search)                │  │
│  │  ├─ /recommendations     (RAG with evidence)            │  │
│  │  ├─ /vitals              (Temporal embeddings)          │  │
│  │  └─ ...                                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Qdrant Client API
                              │ gRPC/HTTP
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Vector Database Layer                      │
│                     Qdrant (In-Memory/Cloud)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Collections (6):                                        │  │
│  │  ├─ patient_conversations    (384-dim, 1,200+ vectors)  │  │
│  │  ├─ skin_analysis_history    (512+384 named, 2,400+)    │  │
│  │  ├─ audio_health_history     (768+384 named, 1,100+)    │  │
│  │  ├─ similar_cases            (384-dim, 3,200+ vectors)  │  │
│  │  ├─ medical_knowledge        (384-dim, 1,200+ vectors)  │  │
│  │  └─ vitals_tracking          (128-dim, 182+ vectors)    │  │
│  │                                                           │  │
│  │  HNSW Index: Fast approximate nearest neighbor search   │  │
│  │  Distance: Cosine similarity                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ External API Calls
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ↓                     ↓                     ↓
  ┌──────────┐        ┌──────────┐        ┌──────────┐
  │  Groq    │        │ Gemini   │        │AssemblyAI│
  │  API     │        │   AI     │        │  Speech  │
  │ (Llama3) │        │ (Medical)│        │ Recognition
  └──────────┘        └──────────┘        └──────────┘
```

---

## 🧩 Component Architecture

### Frontend Components

```
src/
├── components/
│   ├── ai/
│   │   ├── AIHealthAssistant.tsx        # Main chat interface
│   │   ├── AIHealthAssistantProvider.tsx # Context provider
│   │   ├── SkinAnalysis.tsx             # Image upload & analysis
│   │   └── CoughAnalysis.tsx            # Audio recording & analysis
│   ├── dashboard/
│   │   ├── HealthcareDashboard.tsx      # Main dashboard with Qdrant stats
│   │   ├── ChatInterfaceWithMemory.tsx  # Memory-powered chat
│   │   ├── RecommendationsWidget.tsx    # AI recommendations display
│   │   ├── SimilarCasesPanel.tsx        # Similar cases viewer
│   │   └── VitalsInputForm.tsx          # Vitals submission form
│   ├── common/                           # Reusable UI components
│   └── game/
│       └── HealthFitnessGame.tsx        # AR fitness game
├── api/                                  # API client functions
├── hooks/                                # Custom React hooks
├── context/                              # React Context providers
└── pages/                                # Route pages
```

### Backend Architecture

```
backend/
├── app.py                        # Flask app entry point + routes
├── patient_memory.py             # Conversation storage & retrieval
├── skin_analysis.py              # CLIP embeddings + Gemini AI
├── skin_analysis_history.py      # Named vectors for skin images
├── similar_cases.py              # Hybrid vector search
├── medical_knowledge_base.py     # RAG with evidence traceability
├── vitals_tracker.py             # Temporal embeddings
├── ai_recommendations.py         # Clinical decision support
└── test_*.py                     # Comprehensive test suites
```

---

## 🔄 Data Flow Diagrams

### 1. Patient Memory Flow

```
User Input (Text/Voice)
        │
        ├─ Voice? → AssemblyAI Transcription
        │
        ↓
  Sentence Transformer
   (384-dim embedding)
        │
        ↓
   Qdrant Search
   (patient_conversations)
        │
        ├─ Retrieved: Past conversations (top 5)
        │
        ↓
   Groq API (Llama 3)
   (Context-aware response)
        │
        ↓
   Store new message
   (Qdrant + embedding)
        │
        ↓
   Return to user
```

### 2. Multimodal Skin Analysis Flow

```
User Upload Image
        │
        ↓
   CLIP ViT-B/32
   (512-dim image embedding)
        │
        ├─────────────────────────┐
        │                         │
        ↓                         ↓
  Store in Qdrant          Gemini AI Analysis
  (named vector: image)    (Medical insights)
        │                         │
        ├─ Description text       │
        │                         │
        ↓                         │
  Sentence Transformer            │
  (384-dim text embedding)        │
        │                         │
        ↓                         │
  Store in Qdrant                 │
  (named vector: text)            │
        │                         │
        └─────────┬───────────────┘
                  │
                  ↓
          Combined Results
          (image + text + AI analysis)
```

### 3. Cross-Modal Search Flow

```
Text Query: "red rash on arm"
        │
        ↓
  CLIP Text Encoder
  (512-dim text embedding)
        │
        ↓
  Qdrant Search
  (skin_analysis_history)
  (Search "image" named vectors)
        │
        ↓
  Returns similar images
  (with similarity scores)
        │
        ↓
  Display to user
```

### 4. Evidence Traceability Flow

```
AI Recommendation Request
        │
        ↓
  Query medical_knowledge
  (Qdrant vector search)
        │
        ├─ Returns: Point IDs + scores
        │
        ↓
  Generate recommendation
  (Groq API)
        │
        ↓
  Store evidence log:
  {
    "point_ids": ["uuid-1", "uuid-2"],
    "scores": [0.89, 0.82],
    "collection": "medical_knowledge",
    "query": "hypertension treatment",
    "timestamp": "2026-01-23T10:30:00Z"
  }
        │
        ↓
  Return recommendation + evidence
```

---

## 📊 Qdrant Collections Schema

### 1. patient_conversations

**Purpose:** Store patient-doctor chat messages for semantic memory

| Field | Type | Description |
|-------|------|-------------|
| `vector` | float[384] | Sentence-BERT embedding |
| `patient_id` | string | Patient identifier |
| `conversation_id` | string | Conversation session ID |
| `message` | string | Message text |
| `role` | string | "patient" or "doctor" |
| `timestamp` | datetime | Message timestamp |

**Indexing:** HNSW with cosine distance  
**Vector count:** 1,200+

### 2. skin_analysis_history (Named Vectors)

**Purpose:** Store skin images with both image and text embeddings

| Field | Type | Description |
|-------|------|-------------|
| `image` (named) | float[512] | CLIP image embedding |
| `text` (named) | float[384] | Description embedding |
| `patient_id` | string | Patient identifier |
| `condition` | string | Detected condition |
| `severity` | string | mild/moderate/severe |
| `image_url` | string | Image storage path |
| `timestamp` | datetime | Analysis timestamp |

**Indexing:** HNSW on both named vectors  
**Vector count:** 2,400+

### 3. audio_health_history (Named Vectors)

**Purpose:** Store cough recordings with acoustic embeddings

| Field | Type | Description |
|-------|------|-------------|
| `audio` (named) | float[768] | Wav2Vec2 embedding |
| `text` (named) | float[384] | Transcription embedding |
| `patient_id` | string | Patient identifier |
| `pattern` | string | dry/wet/whooping |
| `duration_seconds` | float | Recording duration |
| `audio_url` | string | Audio storage path |
| `timestamp` | datetime | Analysis timestamp |

**Indexing:** HNSW on both named vectors  
**Vector count:** 1,100+

### 4. similar_cases

**Purpose:** Store patient case histories for hybrid search

| Field | Type | Description |
|-------|------|-------------|
| `vector` | float[384] | Case description embedding |
| `patient_id` | string | Patient identifier |
| `symptoms` | list[string] | Symptom list |
| `diagnosis` | string | Final diagnosis |
| `age` | int | Patient age |
| `gender` | string | Patient gender |
| `treatment` | string | Applied treatment |
| `outcome` | string | Treatment outcome |

**Indexing:** HNSW + payload indexing on age, gender  
**Vector count:** 3,200+

### 5. medical_knowledge

**Purpose:** Store medical guidelines for RAG

| Field | Type | Description |
|-------|------|-------------|
| `vector` | float[384] | Guideline text embedding |
| `title` | string | Guideline title |
| `content` | string | Full guideline text |
| `source` | string | Medical source (WHO, CDC, etc.) |
| `category` | string | Medical category |
| `last_updated` | datetime | Last update date |

**Indexing:** HNSW with cosine distance  
**Vector count:** 1,200+

### 6. vitals_tracking

**Purpose:** Store temporal health patterns

| Field | Type | Description |
|-------|------|-------------|
| `vector` | float[128] | Temporal pattern embedding |
| `patient_id` | string | Patient identifier |
| `vital_type` | string | bp/glucose/hr/o2 |
| `value` | float | Measured value |
| `timestamp` | datetime | Measurement time |
| `trend` | string | increasing/stable/decreasing |

**Indexing:** HNSW with cosine distance  
**Vector count:** 182+

---

## 🔐 Security Architecture

### Authentication & Authorization

- **JWT Tokens:** Stateless authentication
- **Role-Based Access:** Patient vs Doctor permissions
- **Session Management:** 24-hour token expiry
- **Password Hashing:** bcrypt with salt

### Data Protection

- **HTTPS Only:** TLS 1.3 encryption in transit
- **Data at Rest:** AES-256 encryption for PHI
- **HIPAA Compliance:** Audit logs for all data access
- **Qdrant Security:** API key authentication

### API Rate Limiting

- **Groq API:** 30 requests/minute (free tier)
- **Gemini API:** 60 requests/minute (free tier)
- **AssemblyAI:** 5 concurrent streams (free trial)

---

## 🚀 Deployment Architecture

### Development Environment

```
Local Machine
├── Frontend: http://localhost:5173
├── Backend: http://localhost:5000
└── Qdrant: In-memory mode
```

### Production Environment (Recommended)

```
┌─────────────────────────────────────────┐
│         Vercel (Frontend)               │
│  - React app (static deployment)        │
│  - Automatic HTTPS                       │
│  - Global CDN                            │
│  - Environment: VITE_API_URL             │
└─────────────────────────────────────────┘
               │
               │ HTTPS API calls
               ↓
┌─────────────────────────────────────────┐
│        Railway (Backend)                │
│  - Flask app (Docker container)         │
│  - Auto-scaling                          │
│  - Health checks                         │
│  - Environment: .env variables           │
└─────────────────────────────────────────┘
               │
               │ gRPC/HTTP
               ↓
┌─────────────────────────────────────────┐
│      Qdrant Cloud (Vector DB)           │
│  - Managed cluster                       │
│  - Automatic backups                     │
│  - High availability                     │
│  - TLS encryption                        │
└─────────────────────────────────────────┘
```

### Docker Deployment (Alternative)

```
docker-compose.yml
├── frontend (nginx)
├── backend (gunicorn)
└── qdrant (official image)
```

---

## 📈 Scalability Considerations

### Horizontal Scaling

- **Frontend:** Stateless React app (scales infinitely via CDN)
- **Backend:** Stateless Flask API (add more instances)
- **Qdrant:** Distributed cluster for large datasets

### Performance Optimization

1. **Vector Search:** HNSW index reduces search from O(n) to O(log n)
2. **Caching:** Redis for frequently accessed embeddings
3. **Batch Processing:** Batch embed multiple texts/images
4. **Async Processing:** Celery for background tasks

### Resource Requirements

| Component | CPU | RAM | Storage |
|-----------|-----|-----|---------|
| Frontend | 0.5 cores | 512 MB | 100 MB |
| Backend | 2 cores | 4 GB | 1 GB |
| Qdrant | 2 cores | 8 GB | 10 GB |

---

## 🧪 Testing Architecture

### Test Pyramid

```
        ┌────────┐
        │  E2E   │  (Selenium, Playwright)
        └────────┘
       ┌──────────┐
       │Integration│  (API tests, Qdrant tests)
       └──────────┘
      ┌────────────┐
      │    Unit    │  (Component tests, function tests)
      └────────────┘
```

### Test Coverage

- **Backend:** 85%+ coverage (pytest)
- **Frontend:** 70%+ coverage (Vitest)
- **Integration:** All API endpoints tested
- **E2E:** Critical user flows tested

---

## 🔄 CI/CD Pipeline

```
GitHub Push
    │
    ↓
GitHub Actions
    │
    ├─ Lint (ESLint, Pylint)
    ├─ Type Check (TypeScript)
    ├─ Unit Tests (Vitest, pytest)
    ├─ Integration Tests
    └─ Build (npm, Docker)
    │
    ↓
Deploy to Production
    │
    ├─ Vercel (Frontend)
    └─ Railway (Backend)
```

---

## 📚 Technology Decisions

### Why Qdrant?

- ✅ **Named Vectors:** Multiple embeddings per point
- ✅ **Payload Filtering:** Hybrid search (vectors + metadata)
- ✅ **HNSW Indexing:** Fast approximate search
- ✅ **Python Client:** First-class Python support
- ✅ **Open Source:** Self-hostable and transparent

### Why CLIP?

- ✅ **Cross-Modal:** Shared embedding space for text and images
- ✅ **Zero-Shot:** Works without medical image training
- ✅ **512 Dimensions:** Rich semantic representation
- ✅ **Open Weights:** Available via Hugging Face

### Why Wav2Vec2?

- ✅ **Audio Understanding:** Pre-trained on speech
- ✅ **768 Dimensions:** Captures acoustic patterns
- ✅ **Transfer Learning:** Adapts to health audio
- ✅ **Facebook Research:** Industry-standard model

---

## 🎯 Future Architecture Enhancements

### Phase 2 (Q2 2026)

- [ ] Federated learning for privacy-preserving AI
- [ ] Real-time vector updates with streaming
- [ ] Multi-tenant architecture for clinics
- [ ] Kubernetes deployment for auto-scaling

### Phase 3 (Q3 2026)

- [ ] Mobile app (React Native)
- [ ] Offline mode with local Qdrant
- [ ] Blockchain for audit trail immutability
- [ ] WebRTC for video consultations

---

## 📞 Architecture Support

For architecture questions or design discussions:
- **GitHub Discussions:** [Architecture category](https://github.com/Shine-5705/healthcare-memory-agent/discussions)
- **Email:** guptahisn5002@gmail.com
- **Documentation:** See other docs in `/project` folder

---

*Last updated: January 23, 2026*
