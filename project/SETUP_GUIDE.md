# 🚀 Healthcare Memory Agent - Complete Setup Guide

**Get up and running in under 10 minutes!**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [API Keys Configuration](#api-keys-configuration)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Deployment](#deployment)

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

| Software | Version | Download Link |
|----------|---------|---------------|
| **Node.js** | 18.x or higher | https://nodejs.org/ |
| **Python** | 3.11 or higher | https://www.python.org/ |
| **Git** | Latest | https://git-scm.com/ |
| **npm** | 9.x or higher | Comes with Node.js |
| **pip** | Latest | Comes with Python |

### Verify Installations

```bash
# Check Node.js version
node --version
# Should show: v18.x.x or higher

# Check Python version
python --version
# Should show: Python 3.11.x or higher

# Check npm version
npm --version
# Should show: 9.x.x or higher

# Check pip version
pip --version
# Should show: pip 23.x.x or higher
```

### API Keys Required

You'll need accounts and API keys from these services:

1. **Groq API** (AI Chat) - Free tier available
   - Sign up: https://console.groq.com/
   - Get your API key from dashboard

2. **Google Gemini API** (Medical Analysis) - Free tier available
   - Sign up: https://makersuite.google.com/app/apikey
   - Create API key

3. **AssemblyAI** (Speech Recognition) - Free trial available
   - Sign up: https://www.assemblyai.com/
   - Get API key from dashboard

---

## ⚡ Quick Start

**For experienced developers who want to get running fast:**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/healthcare-memory-agent.git
cd healthcare-memory-agent/project

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install backend dependencies
cd backend
pip install -r requirements.txt

# 5. Create .env file with your API keys
echo "GROQ_API_KEY=your_groq_key_here" > .env
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
echo "ASSEMBLYAI_API_KEY=your_assemblyai_key_here" >> .env

# 6. Start backend (in backend directory)
python app.py
# Backend runs on http://localhost:5000

# 7. In a NEW terminal, install frontend dependencies
cd ..
npm install

# 8. Start frontend
npm run dev
# Frontend runs on http://localhost:5173

# 9. Open browser and navigate to http://localhost:5173
```

**Done! 🎉** The application should now be running.

---

## 📦 Detailed Installation

### Step 1: Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/yourusername/healthcare-memory-agent.git

# Or using SSH
git clone git@github.com:yourusername/healthcare-memory-agent.git

# Navigate to project directory
cd healthcare-memory-agent/project
```

### Step 2: Backend Setup

#### Create Python Virtual Environment

**Why?** Isolates project dependencies from your system Python.

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.\.venv\Scripts\activate.bat

# macOS/Linux:
source .venv/bin/activate

# You should see (.venv) in your terminal prompt
```

#### Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Upgrade pip (recommended)
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# This will install:
# - Flask 2.3.3 (Web framework)
# - Qdrant-client 1.7.0 (Vector database)
# - Sentence-transformers 2.7.0 (Text embeddings)
# - Transformers 4.36.0 (CLIP, Wav2Vec2)
# - torch (PyTorch for ML models)
# - librosa 0.10.1 (Audio processing)
# - Pillow (Image processing)
# - And more...
```

**Expected output:**
```
Successfully installed Flask-2.3.3 qdrant-client-1.7.0 ...
```

#### Verify Installation

```bash
# Test imports
python -c "import flask; import qdrant_client; import sentence_transformers; print('✅ All imports successful')"
```

### Step 3: Frontend Setup

```bash
# Navigate back to project root
cd ..

# Install Node.js dependencies
npm install

# This will install:
# - React 18
# - TypeScript
# - Tailwind CSS
# - React Router
# - Recharts
# - And more...
```

**Expected output:**
```
added 1234 packages in 45s
```

#### Verify Installation

```bash
# Check if node_modules exists
ls node_modules

# Test TypeScript compilation
npm run build

# Should complete without errors
```

---

## 🔑 API Keys Configuration

### Backend Configuration (.env file)

**Location:** `project/backend/.env`

Create the `.env` file in the `backend` directory:

```bash
cd backend
```

**On Windows (PowerShell):**
```powershell
New-Item -Path .env -ItemType File
notepad .env
```

**On macOS/Linux:**
```bash
touch .env
nano .env  # or use your preferred editor
```

**Add the following content:**

```env
# Backend API Keys

# Groq API for conversational AI
GROQ_API_KEY=gsk_your_groq_api_key_here

# Google Gemini API for medical image analysis
GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here

# AssemblyAI for speech-to-text
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# Optional: Qdrant Cloud (if using cloud instead of in-memory)
# QDRANT_URL=https://your-cluster.qdrant.io
# QDRANT_API_KEY=your_qdrant_api_key
```

**Save and close the file.**

### Where to Get API Keys

#### 1. Groq API Key (Required)

1. Go to https://console.groq.com/
2. Sign up or log in
3. Navigate to "API Keys" section
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)
6. Paste in `.env` file

**Free Tier:** 30 requests/minute

#### 2. Google Gemini API Key (Required)

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the key (starts with `AIzaSy`)
6. Paste in `.env` file

**Free Tier:** 60 requests/minute

#### 3. AssemblyAI API Key (Required)

1. Go to https://www.assemblyai.com/
2. Sign up for free account
3. Go to dashboard: https://www.assemblyai.com/app/
4. Copy your API key
5. Paste in `.env` file

**Free Tier:** 5 hours of transcription

### Frontend Configuration (Optional)

**Location:** `project/.env` or `project/.env.local`

For local development, you can also add frontend environment variables:

```env
# Frontend Environment Variables (optional)

# API base URL (default: http://localhost:5000)
VITE_API_BASE_URL=http://localhost:5000

# Optional: Frontend copies of API keys for direct API calls
VITE_GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here
VITE_GROQ_API_KEY=gsk_your_groq_api_key_here
```

**Note:** For production, use environment variables provided by your hosting platform.

---

## 🚀 Running the Application

### Start Backend Server

**Terminal 1:**

```bash
# Navigate to backend directory
cd project/backend

# Make sure virtual environment is activated
# You should see (.venv) in prompt
# If not, activate it:
..\.venv\Scripts\activate  # Windows
source ../.venv/bin/activate  # macOS/Linux

# Start Flask server
python app.py
```

**Expected output:**
```
✅ Skin analysis history module loaded
✅ Gemini API configured successfully
✅ Text-to-speech engine initialized
✅ Patient memory system loaded successfully
✅ Vitals tracker loaded successfully
✅ Medical knowledge base loaded successfully
✅ AI recommendation engine loaded successfully
✅ Similar cases engine loaded successfully
✅ Audio health history loaded successfully
🔑 AssemblyAI API Key: ✅ Set
🔑 Groq API Key: ✅ Set
🚀 Starting CareMate Backend Server...
📍 Server will run on: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

**Keep this terminal running!**

### Start Frontend Development Server

**Terminal 2 (New terminal window):**

```bash
# Navigate to project directory
cd project

# Start Vite dev server
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Keep this terminal running!**

### Access the Application

1. **Open your browser**
2. **Navigate to:** http://localhost:5173
3. **You should see the landing page**

#### Demo Credentials

For testing without signup:

**Patient Account:**
- Email: `patient@demo.com`
- Password: `demo123`

**Doctor Account:**
- Email: `doctor@demo.com`
- Password: `demo123`

---

## 🧪 Testing

### Backend Tests

Run comprehensive test suites to verify everything works:

```bash
cd project/backend

# Test 1: Multimodal embeddings
python test_multimodal.py
# Expected: All 9 tests pass ✅

# Test 2: Evidence traceability
python test_evidence_traceability.py
# Expected: All 6 tests pass ✅

# Test 3: Patient memory
python test_patient_memory.py
# Expected: All tests pass ✅

# Test 4: Skin analysis
python test_skin_analysis_history.py
# Expected: All tests pass ✅

# Test 5: Similar cases
python test_similar_cases.py
# Expected: All tests pass ✅

# Test 6: Vitals tracking
python test_vitals_tracker.py
# Expected: All tests pass ✅
```

### Frontend Tests

```bash
cd project

# Run TypeScript type checking
npm run build
# Should complete without errors

# Check for linting issues
npm run lint
# Should show no errors
```

### Manual Testing Checklist

Once the application is running, test these features:

- [ ] **Landing Page** loads correctly
- [ ] **Login** with demo credentials works
- [ ] **Dashboard** displays with health vitals
- [ ] **AI Health Assistant** responds to messages
- [ ] **Voice Input** works (allow microphone access)
- [ ] **Skin Analysis** accepts image upload
- [ ] **Cough Analysis** records and analyzes audio
- [ ] **Vitals Tracking** form submits and chart updates
- [ ] **Appointments** calendar displays
- [ ] **Messages** page loads
- [ ] **Settings** page accessible
- [ ] **Qdrant Stats Panel** shows on dashboard

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue 1: "ModuleNotFoundError: No module named 'X'"

**Cause:** Python dependencies not installed or wrong environment

**Solution:**
```bash
# Make sure virtual environment is activated
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall
```

#### Issue 2: "AssertionError: Torch not compiled with CUDA"

**Cause:** PyTorch CPU-only version installed (normal for most setups)

**Solution:**
This is a **warning, not an error**. The application works fine with CPU. To silence it:
- Qdrant operations don't require GPU
- CLIP/Wav2Vec2 models work on CPU (just slower)
- For GPU support, install CUDA-enabled PyTorch from https://pytorch.org/

#### Issue 3: "Port 5000 is already in use"

**Cause:** Another application using port 5000

**Solution:**
```bash
# Option 1: Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Option 2: Change port in backend/app.py
# Edit: app.run(debug=True, port=5001)
```

#### Issue 4: "Groq API error: Invalid API key"

**Cause:** API key not set correctly or expired

**Solution:**
```bash
# Check .env file exists
cd backend
cat .env  # macOS/Linux
type .env  # Windows

# Verify API key format
# Should start with: gsk_

# Test API key manually
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROQ_API_KEY'))"
```

#### Issue 5: "'query_points' object has no attribute"

**Cause:** Qdrant client API mismatch (already fixed in latest code)

**Solution:**
Ensure you have the latest code where `query_points` is replaced with `search`:
```bash
git pull origin main
```

#### Issue 6: "No module named 'librosa'"

**Cause:** librosa not installed in virtual environment

**Solution:**
```bash
# Activate virtual environment first!
.\.venv\Scripts\activate

# Install librosa
pip install librosa soundfile
```

#### Issue 7: Frontend shows "Network Error"

**Cause:** Backend not running or wrong URL

**Solution:**
1. Verify backend is running: http://localhost:5000/api/health
2. Check browser console for CORS errors
3. Ensure `.env` has correct `VITE_API_BASE_URL`

#### Issue 8: "npm install" fails

**Cause:** npm cache corruption or version mismatch

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json  # macOS/Linux
Remove-Item -Recurse -Force node_modules, package-lock.json  # Windows

# Reinstall
npm install
```

### Getting Help

If you're still stuck:

1. **Check GitHub Issues:** https://github.com/yourusername/healthcare-memory-agent/issues
2. **Create New Issue:** Provide error logs, OS, Python/Node versions
3. **Check Documentation:** `HACKATHON_SUBMISSION.md`, module READMEs
4. **Review Console Logs:** Both browser and terminal for detailed errors

---

## 🌐 Deployment

### Option 1: Vercel + Railway (Recommended)

**Frontend (Vercel):**

1. Push code to GitHub
2. Go to https://vercel.com/
3. Click "New Project" → Import from GitHub
4. Select repository
5. Set build command: `npm run build`
6. Set output directory: `dist`
7. Add environment variables:
   - `VITE_API_BASE_URL`: Your backend URL
8. Deploy!

**Backend (Railway):**

1. Go to https://railway.app/
2. Click "New Project" → Deploy from GitHub
3. Select repository
4. Set start command: `python backend/app.py`
5. Add environment variables:
   - `GROQ_API_KEY`
   - `GEMINI_API_KEY`
   - `ASSEMBLYAI_API_KEY`
6. Deploy!
7. Copy the generated URL and update Vercel's `VITE_API_BASE_URL`

### Option 2: Netlify + Heroku

**Frontend (Netlify):**

```bash
# Build production bundle
npm run build

# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

**Backend (Heroku):**

```bash
# Install Heroku CLI
# Then:
heroku login
heroku create your-app-name
git push heroku main
heroku config:set GROQ_API_KEY=your_key
heroku config:set GEMINI_API_KEY=your_key
heroku config:set ASSEMBLYAI_API_KEY=your_key
```

### Option 3: Docker Deployment

**Create `Dockerfile` in backend:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

**Build and run:**

```bash
# Build image
docker build -t healthcare-backend .

# Run container
docker run -p 5000:5000 \
  -e GROQ_API_KEY=your_key \
  -e GEMINI_API_KEY=your_key \
  -e ASSEMBLYAI_API_KEY=your_key \
  healthcare-backend
```

### Qdrant Cloud (Optional)

For production-scale vector database:

1. Sign up: https://cloud.qdrant.io/
2. Create cluster
3. Get cluster URL and API key
4. Update backend `.env`:
   ```env
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key
   ```

---

## 📊 Performance Optimization

### Production Checklist

- [ ] **Environment variables** set correctly
- [ ] **API rate limits** understood and monitored
- [ ] **CORS** configured for your domain
- [ ] **HTTPS** enabled (required for camera/microphone)
- [ ] **Qdrant Cloud** for persistent vector storage
- [ ] **CDN** for static assets (Vercel/Netlify handles this)
- [ ] **Error monitoring** (Sentry, LogRocket)
- [ ] **Analytics** (Google Analytics, Mixpanel)

### Recommended Resources

**For Development:**
- Backend: 512MB RAM, 1 vCPU
- Frontend: Static hosting
- Qdrant: In-memory mode

**For Production:**
- Backend: 2GB RAM, 2 vCPU
- Frontend: CDN (Vercel/Netlify)
- Qdrant: Cloud cluster (1GB+ RAM)

---

## 🎉 Success Checklist

You're all set if you can:

- [x] Backend server running on http://localhost:5000
- [x] Frontend running on http://localhost:5173
- [x] Login with demo credentials
- [x] See dashboard with Qdrant Stats Panel
- [x] Send message in AI Health Assistant
- [x] Upload image for skin analysis
- [x] Record audio for cough analysis
- [x] All test suites pass
- [x] No errors in browser console
- [x] No errors in terminal logs

**Congratulations! 🎊 You're ready to explore the Healthcare Memory Agent!**

---

## 📚 Next Steps

1. **Explore Features:** Try all modules (skin analysis, audio health, vitals tracking)
2. **Read Documentation:** Check `HACKATHON_SUBMISSION.md` for detailed feature overview
3. **Review Video Script:** See `COMPLETE_DEMO_SCRIPT_WITH_QDRANT.md` for guided tour
4. **Check Code:** Explore backend modules in `backend/*.py`
5. **Customize:** Modify UI, add features, enhance AI prompts
6. **Deploy:** Follow deployment guide above
7. **Star on GitHub:** ⭐ https://github.com/yourusername/healthcare-memory-agent

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🆘 Support

- **Documentation:** See `/project/backend/README.md` and module-specific READMEs
- **GitHub Issues:** https://github.com/yourusername/healthcare-memory-agent/issues
- **Email:** support@yourproject.com
- **Discord:** [Your Discord invite link]

---

**Built with ❤️ for the Qdrant Hackathon**

*Showcasing the power of multimodal vector search in healthcare AI*
