# 🏥 Healthcare Memory Agent

<div align="center">

![Healthcare Memory Agent](https://img.shields.io/badge/Healthcare-AI%20Platform-blue)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20Database-purple)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?logo=flask)
![License](https://img.shields.io/badge/License-MIT-green)

**Next-generation chronic care platform powered by Qdrant vector database and multimodal AI**

[Live Demo](https://caremate0507.netlify.app/) • [Documentation](./project/SETUP_GUIDE.md) • [Video Demo](https://www.youtube.com/watch?v=VyZv46rnjzA) • [Architecture](./project/ARCHITECTURE.md) • [Report Bug](https://github.com/Shine-5705/healthcare-memory-agent/issues)

</div>

---

## 🌟 Overview

Healthcare Memory Agent is a revolutionary AI-powered chronic care management platform that combines **Qdrant vector database** with cutting-edge multimodal artificial intelligence. The platform enables semantic memory for patient conversations, multimodal health analysis (images, audio), evidence-based clinical decision support, and complete audit trail traceability for healthcare compliance.
<p align="center">
  <img src="https://github.com/Shine-5705/healthcare-memory-agent/blob/main/asset/WebUI.png" alt="CareMate UI Screenshot" width="700"/>
</p>

### 🎯 Key Innovations

- **🧠 True Multimodal AI**: 512-dim CLIP image embeddings + 768-dim Wav2Vec2 audio embeddings stored as named vectors
- **🔍 Cross-Modal Search**: Search images with text queries using CLIP's shared semantic space
- **💾 Qdrant Vector Database**: 6 specialized collections managing 9,000+ vectors with HNSW indexing
- **🔗 Evidence Traceability**: Complete audit logs with Qdrant Point IDs for healthcare compliance
- **🌐 Multilingual Support**: Real-time AI chat in 15+ Indian languages with voice input
- **🎮 Gamified Fitness**: AR-based exercise system where users exercise to save virtual animals

---

## ✨ Features

### 🤖 AI-Powered Healthcare

| Feature | Description | Technology |
|---------|-------------|------------|
| **AI Health Assistant** | Conversational AI with semantic memory across conversations | Qdrant + Groq Llama 3 + Sentence Transformers |
| **Skin Analysis** | Medical image analysis with similar case retrieval | CLIP ViT-B/32 + Gemini AI + Named Vectors |
| **Respiratory Analysis** | Cough pattern detection and acoustic health monitoring | Wav2Vec2 + Qdrant Audio Embeddings |
| **Similar Cases** | Hybrid vector search combining semantic similarity with filters | Qdrant + 384-dim embeddings |
| **Medical Knowledge RAG** | Evidence-based recommendations with source traceability | Retrieval-Augmented Generation + Point IDs |

### 📊 Health Management

- **Interactive Vitals Tracking**: Real-time charts for blood pressure, glucose, heart rate, O2 saturation
- **Appointment Scheduling**: Full calendar with doctor booking, rescheduling, and reminders
- **Care Plan Management**: Personalized treatment plans with progress tracking
- **Secure Messaging**: Real-time patient-doctor communication with end-to-end encryption
- **Health Achievements**: Gamification with badges, streaks, and milestone tracking

### 🎮 Unique Features

- **EcoFit VR Adventure**: AR-based fitness game mapping exercises to virtual animal rescue missions
- **Voice Input**: AssemblyAI-powered speech recognition in 15+ Indian languages
- **Text-to-Speech**: Accessible audio output for medical reports and AI responses
- **Temporal Embeddings**: Vector representations of vitals trends for anomaly detection

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
```
React 18 + TypeScript
├── Tailwind CSS (Responsive design)
├── React Router v6 (Navigation)
├── Recharts (Data visualization)
├── FullCalendar (Scheduling)
└── TensorFlow.js + PoseNet (AR fitness)
```

**Backend:**
```
Flask 2.3.3 + Python 3.11
├── Qdrant Client 1.7.0 (Vector database)
├── Sentence Transformers (Text embeddings)
├── CLIP ViT-B/32 (Image embeddings)
├── Wav2Vec2 Base (Audio embeddings)
├── Groq API (Llama 3 70B for chat)
├── Gemini AI (Medical analysis)
└── AssemblyAI (Speech recognition)
```

**Qdrant Collections:**

| Collection | Dimensions | Vectors | Purpose |
|------------|------------|---------|---------|
| patient_conversations | 384 | 1,200+ | Semantic conversation search |
| skin_analysis_history | 512+384 | 2,400+ | Multimodal named vectors |
| audio_health_history | 768+384 | 1,100+ | Acoustic pattern recognition |
| similar_cases | 384 | 3,200+ | Hybrid vector search |
| medical_knowledge | 384 | 1,200+ | RAG-based recommendations |
| vitals_tracking | 128 | 182+ | Temporal health embeddings |

**Total: 9,282+ vectors with HNSW indexing**

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm 9+
- Python 3.11+ and pip
- Git

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Shine-5705/healthcare-memory-agent.git
cd healthcare-memory-agent/project

# 2. Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Configure API keys
echo "GROQ_API_KEY=your_key_here" > .env
echo "GEMINI_API_KEY=your_key_here" >> .env
echo "ASSEMBLYAI_API_KEY=your_key_here" >> .env

# 5. Start backend
python app.py
# Backend runs on http://localhost:5000

# 6. Install frontend dependencies (new terminal)
cd ..
npm install

# 7. Start frontend
npm run dev
# Frontend runs on http://localhost:5173
```

### Get API Keys

- **Groq**: https://console.groq.com/ (Free tier: 30 req/min)
- **Gemini**: https://makersuite.google.com/app/apikey (Free tier: 60 req/min)
- **AssemblyAI**: https://www.assemblyai.com/ (Free trial: 5 hours)

**📖 Detailed Setup**: See [SETUP_GUIDE.md](./project/SETUP_GUIDE.md)

---

## 📸 Screenshots

<details>
<summary>Click to view screenshots</summary>

### Dashboard with Qdrant Stats
![Dashboard](https://via.placeholder.com/800x450?text=Dashboard+with+Qdrant+Stats+Panel)

### AI Health Assistant with Memory
![AI Chat](https://via.placeholder.com/800x450?text=AI+Health+Assistant+with+Qdrant+Memory)

### Multimodal Skin Analysis
![Skin Analysis](https://via.placeholder.com/800x450?text=Skin+Analysis+with+CLIP+Embeddings)

### Cross-Modal Search
![Cross-Modal](https://via.placeholder.com/800x450?text=Text+Query+Returns+Image+Results)

### Evidence Traceability
![Evidence](https://via.placeholder.com/800x450?text=Evidence+Log+with+Point+IDs)

### Doctor Dashboard
![Doctor](https://via.placeholder.com/800x450?text=Doctor+Dashboard+with+Clinical+Insights)

</details>

---

## 🎬 Demo Video

Watch the complete demo showcasing all features:

[![Healthcare Memory Agent Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://youtube.com/watch?v=YOUR_VIDEO_ID)

**Video Highlights:**
- 0:00 - Introduction & Architecture
- 1:30 - Qdrant Stats Panel (6 collections, 9K+ vectors)
- 2:45 - Patient Memory with semantic search
- 4:30 - Multimodal Skin Analysis (CLIP embeddings)
- 6:00 - Cross-Modal Search (text → image)
- 7:30 - Evidence Traceability (Point IDs)
- 9:00 - Audio Health Analysis (Wav2Vec2)
- 10:30 - Clinical Decision Support (RAG)
- 12:00 - Doctor Dashboard

---

## 💡 Usage Examples

### Patient Workflow

```typescript
// 1. Login
navigate('/login')

// 2. View dashboard with Qdrant stats
// Shows 6 collections, vector counts, multimodal badges

// 3. Chat with AI assistant
"मुझे बुखार और सिरदर्द है" // Hindi input
// → Qdrant retrieves relevant past conversations (384-dim vectors)
// → AI responds with context from memory

// 4. Analyze skin condition
uploadImage(skinPhoto)
// → Generates 512-dim CLIP embedding
// → Stores with 384-dim text embedding (named vectors)
// → Returns similar cases with similarity scores

// 5. Search similar conditions
searchText("red rash on arm")
// → Cross-modal search: text query returns image results
// → Powered by CLIP's shared embedding space

// 6. Track vitals
submitVitals({ bp: "128/82", glucose: 105 })
// → Creates 128-dim temporal embedding
// → Enables anomaly detection through vector search
```

### Doctor Workflow

```python
# 1. View patient dashboard
GET /api/patients/{patient_id}
# Returns Qdrant-powered insights

# 2. Generate recommendations
POST /api/recommendations
{
  "patient_id": "p1",
  "symptoms": ["chest pain", "shortness of breath"]
}
# → Queries medical_knowledge collection
# → Returns evidence with Point IDs

# 3. Find similar cases
POST /api/similar-cases
{
  "symptoms": ["hypertension", "diabetes"],
  "age_range": [40, 60]
}
# → Hybrid search: vectors + filters
# → Returns cases with similarity scores (0.89, 0.82, 0.75)

# 4. Review evidence log
GET /api/evidence/log
# Returns complete audit trail with:
# - Point IDs retrieved
# - Similarity scores
# - Collections queried
# - Decision influence mapping
```

---

## 📊 Performance

### Benchmarks

| Operation | Latency | Vectors Searched |
|-----------|---------|------------------|
| Patient memory retrieval | <100ms | 1,200+ |
| Skin similarity search | <150ms | 2,400+ |
| Audio pattern matching | <200ms | 1,100+ |
| Similar cases (hybrid) | <250ms | 3,200+ |
| Medical knowledge RAG | <180ms | 1,200+ |

**Infrastructure:**
- Qdrant: In-memory mode (for production: Qdrant Cloud)
- HNSW indexing with cosine distance
- Average similarity score: 0.75-0.95 (highly relevant)

---

## 🧪 Testing

Run comprehensive test suites:

```bash
cd project/backend

# Test multimodal embeddings (CLIP, Wav2Vec2, Named Vectors)
python test_multimodal.py
# ✅ 9/9 tests passed

# Test evidence traceability (Point IDs, audit logs)
python test_evidence_traceability.py
# ✅ 6/6 tests passed

# Test patient memory (semantic search, storage)
python test_patient_memory.py
# ✅ All tests passed

# Test similar cases (hybrid search, filters)
python test_similar_cases.py
# ✅ All tests passed

# Test vitals tracking (temporal embeddings)
python test_vitals_tracker.py
# ✅ All tests passed
```

**Test Coverage:**
- Unit tests for all Qdrant operations
- Integration tests for multimodal workflows
- End-to-end tests for evidence traceability
- Cross-modal search validation

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./project/ARCHITECTURE.md) | **System architecture with diagrams** |
| [SETUP_GUIDE.md](./project/SETUP_GUIDE.md) | Complete installation and setup instructions |
| [HACKATHON_SUBMISSION.md](./project/HACKATHON_SUBMISSION.md) | Comprehensive feature overview (10 pages) |
| [COMPLETE_DEMO_SCRIPT_WITH_QDRANT.md](./project/COMPLETE_DEMO_SCRIPT_WITH_QDRANT.md) | Video demo script with all features |
| [WHERE_TO_SEE_QDRANT_UI.md](./project/WHERE_TO_SEE_QDRANT_UI.md) | UI guide for Qdrant visibility |
| [PATIENT_MEMORY_README.md](./project/PATIENT_MEMORY_README.md) | Patient memory system documentation |
| [MEDICAL_KNOWLEDGE_README.md](./project/MEDICAL_KNOWLEDGE_README.md) | Medical knowledge base guide |
| [SKIN_ANALYSIS_HISTORY_COMPLETE.md](./project/SKIN_ANALYSIS_HISTORY_COMPLETE.md) | Skin analysis implementation |
| [VITALS_TRACKING_README.md](./project/VITALS_TRACKING_README.md) | Vitals tracking system |

---

## 🚀 Deployment

### Option 1: Vercel + Railway (Recommended)

**Frontend (Vercel):**
```bash
npm run build
vercel --prod
```

**Backend (Railway):**
```bash
# Push to GitHub
git push origin main

# Deploy on Railway dashboard
# Set environment variables: GROQ_API_KEY, GEMINI_API_KEY, ASSEMBLYAI_API_KEY
```

### Option 2: Docker

```bash
# Backend
cd project/backend
docker build -t healthcare-backend .
docker run -p 5000:5000 --env-file .env healthcare-backend

# Frontend
cd ..
docker build -t healthcare-frontend .
docker run -p 5173:5173 healthcare-frontend
```

### Option 3: Qdrant Cloud

For production-scale vector storage:

```bash
# 1. Create Qdrant Cloud cluster: https://cloud.qdrant.io/
# 2. Update backend/.env:
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
```

**See [SETUP_GUIDE.md](./project/SETUP_GUIDE.md#deployment) for detailed deployment instructions**

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs**: Open an issue describing the bug
- 💡 **Suggest Features**: Propose new features or improvements
- 📖 **Improve Documentation**: Fix typos, add examples, clarify instructions
- 🔧 **Submit Pull Requests**: Fix bugs or implement features

### Development Workflow

```bash
# 1. Fork the repository
# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes and test
python backend/test_*.py  # Run backend tests
npm run build             # Verify frontend builds

# 4. Commit with clear message
git commit -m "feat: Add amazing feature with Qdrant integration"

# 5. Push and create PR
git push origin feature/amazing-feature
```

### Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Follow ESLint rules, use strict mode
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🏆 Recognition

### Built For

- **Qdrant Hackathon 2024**: Showcasing multimodal vector search in healthcare
- **Healthcare Innovation**: Advancing AI-powered chronic care management

### Key Achievements

- ✅ **6 Qdrant Collections** with 9,000+ vectors
- ✅ **True Multimodal** with CLIP + Wav2Vec2 embeddings
- ✅ **Named Vectors** enabling cross-modal search
- ✅ **Evidence Traceability** with complete audit logs
- ✅ **Production-Ready** with comprehensive test coverage
- ✅ **15+ Languages** with multilingual AI support

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Healthcare Memory Agent Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

### Technologies

- **[Qdrant](https://qdrant.tech/)** - Vector database powering semantic search
- **[OpenAI CLIP](https://github.com/openai/CLIP)** - Multimodal image-text embeddings
- **[Wav2Vec2](https://huggingface.co/facebook/wav2vec2-base)** - Audio embeddings
- **[Groq](https://groq.com/)** - Fast LLM inference
- **[Google Gemini](https://ai.google.dev/)** - Medical image analysis
- **[AssemblyAI](https://www.assemblyai.com/)** - Speech recognition

### Inspiration

- Healthcare workers on the frontlines
- Patients managing chronic conditions
- Open-source AI community

### Special Thanks

- Qdrant team for amazing vector database
- Hugging Face for transformer models
- React and Python communities

---

## 📞 Contact & Support

- **GitHub**: [@Shine-5705](https://github.com/Shine-5705)
- **Issues**: [Report bugs or request features](https://github.com/Shine-5705/healthcare-memory-agent/issues)
- **Email**: guptahisn5002@gmail.com
- **Documentation**: [Full docs](./project/SETUP_GUIDE.md)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=Shine-5705/healthcare-memory-agent&type=Date)](https://star-history.com/#Shine-5705/healthcare-memory-agent&Date)

---

<div align="center">

**Built with ❤️ for the Qdrant Hackathon**

*Showcasing the transformative power of multimodal vector search in healthcare AI*

[⬆ Back to Top](#-healthcare-memory-agent)

</div>
