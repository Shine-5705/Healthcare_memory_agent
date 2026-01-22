# 🚀 Healthcare Memory Agent - Complete Setup Guide

**Version:** 1.0  
**Last Updated:** January 2026  
**Estimated Setup Time:** 15-20 minutes

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start (5 Minutes)](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [API Keys Configuration](#api-keys-configuration)
5. [Running the Application](#running-the-application)
6. [Verifying Installation](#verifying-installation)
7. [Common Issues & Solutions](#troubleshooting)
8. [Optional: Qdrant Cloud Setup](#qdrant-cloud-optional)

---

## 🖥️ System Requirements

### Minimum Requirements:
- **Operating System:** Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python:** 3.11 or higher
- **Node.js:** 16.x or higher
- **RAM:** 8 GB minimum (16 GB recommended for AI features)
- **Storage:** 2 GB free space
- **Internet:** Required for API calls and package installation

### Supported Browsers:
- Chrome 90+ (recommended)
- Firefox 88+
- Edge 90+
- Safari 14+

---

## ⚡ Quick Start (5 Minutes)

For experienced developers who want to get running immediately:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/healthcare-memory-agent.git
cd healthcare-memory-agent/project

# 2. Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python app.py

# 3. Frontend setup (new terminal)
cd ..
npm install
npm run dev

# 4. Open browser
# Frontend: http://localhost:5173
# Backend: http://localhost:5000
```

⚠️ **Important:** You need API keys for full functionality. See [API Keys Configuration](#api-keys-configuration).

---

## 📦 Detailed Installation

### Step 1: Install Prerequisites

#### Python 3.11+

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer and **check "Add Python to PATH"**
3. Verify: Open Command Prompt and type:
   ```bash
   python --version
   ```
   Should show: `Python 3.11.x` or higher

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3.11 --version
```

#### Node.js 16+

**Windows:**
1. Download from [nodejs.org](https://nodejs.org/)
2. Run installer (LTS version recommended)
3. Verify:
   ```bash
   node --version
   npm --version
   ```

**macOS:**
```bash
brew install node
node --version
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version
```

#### Git (Optional but Recommended)

**Windows:** Download from [git-scm.com](https://git-scm.com/)  
**macOS:** `brew install git`  
**Linux:** `sudo apt install git`

---

### Step 2: Download Project

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/yourusername/healthcare-memory-agent.git
cd healthcare-memory-agent/project
```

**Option B: Download ZIP**
1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Open terminal in `healthcare-memory-agent/project` folder

---

### Step 3: Backend Setup

#### 3.1 Navigate to Backend Directory
```bash
cd backend
```

#### 3.2 Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

#### 3.3 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected packages (19 total):**
- Flask 2.3.3 - Web framework
- Flask-CORS 4.0.0 - Cross-origin support
- qdrant-client 1.7.0 - Vector database
- sentence-transformers 2.7.0 - Text embeddings
- transformers 4.36.0 - AI models
- librosa 0.10.1 - Audio processing
- torch, torchvision - Deep learning
- requests, Pillow, python-dotenv - Utilities

**Installation time:** 3-5 minutes depending on internet speed.

#### 3.4 Configure Environment Variables

**Create .env file:**
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

**Or create manually:**
```bash
# Backend API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

# Optional: Qdrant Cloud (leave empty for in-memory mode)
QDRANT_URL=
QDRANT_API_KEY=
```

---

### Step 4: Frontend Setup

#### 4.1 Navigate to Project Root
```bash
# From backend directory
cd ..

# Or directly
cd /path/to/healthcare-memory-agent/project
```

#### 4.2 Install Node Dependencies
```bash
npm install
```

**Expected packages:**
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- React Router - Navigation
- Recharts - Data visualization
- FullCalendar - Appointment scheduling
- TensorFlow.js - Client-side ML

**Installation time:** 2-3 minutes.

---

## 🔑 API Keys Configuration

You need API keys for full functionality. Here's how to get them:

### 1. AssemblyAI (Speech-to-Text)

**Purpose:** Voice input in 15+ languages  
**Free Tier:** 5 hours/month

**Steps:**
1. Go to [assemblyai.com](https://www.assemblyai.com/)
2. Sign up for free account
3. Navigate to Dashboard → API Keys
4. Copy your API key
5. Add to `backend/.env`:
   ```
   ASSEMBLYAI_API_KEY=abc123...
   ```

### 2. Groq (AI Chat)

**Purpose:** Health assistant conversation  
**Free Tier:** 14,400 requests/day (Llama 3 70B)

**Steps:**
1. Go to [console.groq.com](https://console.groq.com/)
2. Create account (GitHub login supported)
3. Go to API Keys section
4. Create new API key
5. Add to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_...
   ```

### 3. Google Gemini AI (Medical Analysis)

**Purpose:** Skin condition analysis  
**Free Tier:** 60 requests/minute

**Steps:**
1. Go to [ai.google.dev](https://ai.google.dev/)
2. Click "Get API Key in Google AI Studio"
3. Create new project or select existing
4. Generate API key
5. Add to `backend/.env`:
   ```
   GEMINI_API_KEY=AIza...
   ```

### Testing API Keys

After adding keys, test them:

**Option 1: Run backend**
```bash
cd backend
python app.py
```

Look for:
```
🔑 AssemblyAI API Key: ✅ Set
🔑 Groq API Key: ✅ Set
```

**Option 2: Quick test script**
```bash
cd backend
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'AssemblyAI: {'✅' if os.getenv('ASSEMBLYAI_API_KEY') else '❌'}')
print(f'Groq: {'✅' if os.getenv('GROQ_API_KEY') else '❌'}')
print(f'Gemini: {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}')
"
```

---

## ▶️ Running the Application

### Method 1: Two Terminals (Recommended)

**Terminal 1 - Backend:**
```bash
cd project/backend

# If using virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Start server
python app.py
```

**Expected output:**
```
✅ Skin analysis history module loaded
✅ Patient memory system loaded successfully
✅ Medical knowledge base loaded successfully
🔑 AssemblyAI API Key: ✅ Set
🔑 Groq API Key: ✅ Set
🚀 Starting CareMate Backend Server...
📍 Server will run on: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

**Terminal 2 - Frontend:**
```bash
cd project

# Start development server
npm run dev
```

**Expected output:**
```
VITE v5.x.x ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

### Method 2: Using Start Script (Windows)

Create `start.bat` in project root:
```batch
@echo off
start cmd /k "cd backend && .venv\Scripts\activate && python app.py"
timeout /t 3
start cmd /k "npm run dev"
start http://localhost:5173
```

Double-click to run both servers.

### Method 3: Using Start Script (macOS/Linux)

Create `start.sh` in project root:
```bash
#!/bin/bash
cd backend && source .venv/bin/activate && python app.py &
sleep 3
npm run dev &
sleep 2
open http://localhost:5173  # macOS
# xdg-open http://localhost:5173  # Linux
```

Make executable and run:
```bash
chmod +x start.sh
./start.sh
```

---

## ✅ Verifying Installation

### 1. Check Backend Health

Open browser: `http://localhost:5000/health`

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "modules": {
    "patient_memory": "loaded",
    "skin_analysis": "loaded",
    "audio_analysis": "loaded",
    "vitals_tracker": "loaded",
    "medical_knowledge": "loaded"
  },
  "api_keys": {
    "assemblyai": "configured",
    "groq": "configured",
    "gemini": "configured"
  }
}
```

### 2. Check Frontend

Open browser: `http://localhost:5173`

**Expected:** Landing page with "Healthcare Memory Agent" and "Get Started" button.

### 3. Test Login

**Demo Credentials:**
- **Email:** `demo@patient.com`
- **Password:** `demo123`
- **Role:** Patient

**Or:**
- **Email:** `demo@doctor.com`
- **Password:** `demo123`
- **Role:** Healthcare Provider

### 4. Test AI Chat

1. Click "AI Health Assistant"
2. Type: "Hello, I have a headache"
3. Should get response in ~2-3 seconds

### 5. Test Qdrant Integration

**Check Qdrant Stats Panel:**
1. Go to Dashboard
2. Scroll down to "Qdrant Vector Database Stats"
3. Should show:
   - 6 collections
   - Collection names and dimensions
   - "In-memory mode" status

**Check Console Logs:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Send a chat message
4. Look for:
   ```
   🔍 Searching patient memory...
   ✅ Retrieved 3 conversations (similarity: 0.87, 0.82, 0.79)
   💾 Stored conversation with ID: conv_abc123
   ```

### 6. Run Test Suite

**Backend tests:**
```bash
cd backend

# Test multimodal embeddings
python test_multimodal.py

# Test patient memory
python test_patient_memory.py

# Test evidence traceability
python test_evidence_traceability.py
```

**Expected:** All tests pass with ✅ checkmarks.

---

## 🔧 Troubleshooting

### Issue 1: Port Already in Use

**Error:** `Address already in use: 5000` or `5173`

**Solution:**

**Windows:**
```bash
# Find process using port
netstat -ano | findstr :5000
# Kill process (replace PID)
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
# Find and kill process
lsof -ti:5000 | xargs kill -9
```

**Or use different ports:**

Backend (`backend/app.py`):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

Frontend (`vite.config.ts`):
```typescript
export default defineConfig({
  server: { port: 5174 }  // Changed to 5174
})
```

### Issue 2: Module Not Found Errors

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Cause:** Virtual environment not activated or packages not installed.

**Solution:**
```bash
# Activate virtual environment
cd backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Reinstall packages
pip install -r requirements.txt
```

### Issue 3: Python Version Too Old

**Error:** `Python 3.11 is required`

**Solution:** Install Python 3.11+ and create new virtual environment:

```bash
# Check current version
python --version

# Windows: Download from python.org
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11

# Create new venv with correct version
python3.11 -m venv .venv
```

### Issue 4: Qdrant "No module named 'librosa'"

**Error:** `⚠️ Multimodal embeddings not available: No module named 'librosa'`

**Solution:**
```bash
# Make sure virtual environment is activated
cd backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install librosa
pip install librosa soundfile
```

### Issue 5: CORS Errors in Browser

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Cause:** Backend not running or wrong URL.

**Solution:**
1. Ensure backend is running on `http://localhost:5000`
2. Check `src/api/*.ts` files have correct `BACKEND_API_URL`
3. Verify Flask-CORS is installed: `pip show flask-cors`

### Issue 6: API Key Errors

**Error:** `Invalid Groq API key` or `401 Unauthorized`

**Cause:** Invalid or expired API keys.

**Solution:**
1. Regenerate API keys from provider dashboards
2. Ensure no extra spaces in `.env` file
3. Restart backend after updating `.env`
4. Test keys with curl:

```bash
# Test Groq API
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3-70b-8192","messages":[{"role":"user","content":"Hi"}]}'
```

### Issue 7: TensorFlow.js Errors

**Error:** `WebGL not supported` or `WASM backend failed`

**Cause:** Browser doesn't support required APIs.

**Solution:**
1. Update browser to latest version
2. Enable hardware acceleration in browser settings
3. Try different browser (Chrome recommended)
4. Disable browser extensions temporarily

### Issue 8: Slow Response Times

**Cause:** Large model downloads on first run.

**Solution:**
- First-time setup downloads CLIP, Wav2Vec2 models (~1-2 GB)
- Subsequent runs are fast (models cached)
- Wait 5-10 minutes for initial model downloads
- Check terminal for download progress

---

## ☁️ Qdrant Cloud Setup (Optional)

By default, the app uses **Qdrant in-memory mode** (data lost on restart). For production, use Qdrant Cloud.

### Step 1: Create Qdrant Cloud Account

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io/)
2. Sign up (free tier available)
3. Create new cluster:
   - Name: `healthcare-memory-agent`
   - Region: Choose nearest
   - Tier: Free (1 GB storage, 1M vectors)

### Step 2: Get Connection Details

1. Click on your cluster
2. Copy **Cluster URL** (e.g., `https://xyz-abc.aws.qdrant.io:6333`)
3. Go to **API Keys** → Generate new key
4. Copy API key

### Step 3: Update Configuration

Edit `backend/.env`:
```bash
QDRANT_URL=https://xyz-abc.aws.qdrant.io:6333
QDRANT_API_KEY=your_api_key_here
```

### Step 4: Restart Backend

```bash
cd backend
python app.py
```

Look for:
```
🔗 Connecting to Qdrant server at https://xyz-abc.aws...
✅ Qdrant connection successful
```

### Step 5: Verify Collections

Visit: `http://localhost:5000/api/qdrant/collections`

Should show:
```json
{
  "collections": [
    "patient_conversations",
    "skin_analysis_history",
    "audio_health_history",
    "similar_cases",
    "medical_knowledge",
    "vitals_tracking"
  ]
}
```

---

## 📚 Next Steps

### 1. Explore Features

**Recommended order:**
1. ✅ Dashboard - See health metrics and Qdrant stats
2. ✅ AI Health Assistant - Test conversational memory
3. ✅ AI Skin Analysis - Upload image, see multimodal embeddings
4. ✅ Cough Analysis - Record audio, test acoustic embeddings
5. ✅ Vitals Tracking - Log health data
6. ✅ EcoFit Game - Try AR fitness

### 2. Review Documentation

- **HACKATHON_SUBMISSION.md** - Complete feature overview
- **COMPLETE_DEMO_SCRIPT_WITH_QDRANT.md** - Detailed walkthrough
- **WHERE_TO_SEE_QDRANT_UI.md** - Qdrant visibility guide
- **Backend README.md** - API documentation

### 3. Development

**Enable debug mode:**

Frontend (`src/config/apiKeys.ts`):
```typescript
export const DEBUG_MODE = true;
```

Backend (already enabled in development):
```python
app.run(debug=True)  # Auto-reload on code changes
```

**Recommended VS Code Extensions:**
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

### 4. Testing

**Run comprehensive tests:**
```bash
cd backend

# All tests
python -m pytest test_*.py -v

# Specific test
python test_multimodal.py
python test_evidence_traceability.py
```

### 5. Production Deployment

**Frontend (Vercel/Netlify):**
```bash
npm run build
# Deploy 'dist' folder
```

**Backend (Railway/Heroku):**
```bash
# Ensure requirements.txt is up to date
pip freeze > requirements.txt

# Create Procfile
echo "web: python app.py" > Procfile
```

---

## 🎓 Learning Resources

### Qdrant Documentation
- [Official Docs](https://qdrant.tech/documentation/)
- [Named Vectors Guide](https://qdrant.tech/documentation/concepts/vectors/#named-vectors)
- [Python Client](https://github.com/qdrant/qdrant-client)

### AI Models Used
- **CLIP**: [OpenAI CLIP](https://github.com/openai/CLIP)
- **Wav2Vec2**: [Hugging Face](https://huggingface.co/facebook/wav2vec2-base)
- **Sentence Transformers**: [SBERT](https://www.sbert.net/)

### APIs
- [Groq API Docs](https://console.groq.com/docs)
- [AssemblyAI Docs](https://www.assemblyai.com/docs)
- [Gemini AI Docs](https://ai.google.dev/docs)

---

## 💬 Support

### Get Help

**Issues or Questions:**
- GitHub Issues: [github.com/yourrepo/issues](https://github.com/yourrepo/issues)
- Email: support@yourdomain.com

**Common Questions:**
- "How do I reset the database?" → Delete Qdrant data folder and restart
- "Can I use different AI models?" → Yes, modify `backend/multimodal_embeddings.py`
- "Is this HIPAA compliant?" → Evidence traceability helps, but consult legal team
- "How do I add more languages?" → Update `language_names` dict in backend files

---

## 📄 License

This project is open-source under the MIT License. See LICENSE file for details.

---

## ✨ You're All Set!

Your Healthcare Memory Agent is now ready to use. Key URLs:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/health
- **API Docs:** http://localhost:5000/api/docs (if enabled)

**Demo Credentials:**
- Patient: `demo@patient.com` / `demo123`
- Doctor: `demo@doctor.com` / `demo123`

Enjoy building the future of healthcare AI! 🚀🏥

---

**Questions?** Check the troubleshooting section or open an issue on GitHub.
