from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import requests
import threading
import speech_recognition as sr
from dotenv import load_dotenv
import tempfile
import datetime

# Import skin analysis module
try:
    from skin_analysis import analyze_skin_with_gemini, generate_audio_response
    SKIN_ANALYSIS_AVAILABLE = True
    print("✅ Skin analysis module loaded successfully")
except ImportError as e:
    print(f"⚠️ Skin analysis module not available: {e}")
    SKIN_ANALYSIS_AVAILABLE = False

# Import patient memory system
try:
    from patient_memory import get_memory_system
    PATIENT_MEMORY_AVAILABLE = True
    print("✅ Patient memory system loaded successfully")
except ImportError as e:
    print(f"⚠️ Patient memory system not available: {e}")
    PATIENT_MEMORY_AVAILABLE = False

# Import vitals tracker
try:
    from vitals_tracker import get_vitals_tracker
    VITALS_TRACKER_AVAILABLE = True
    print("✅ Vitals tracker loaded successfully")
except ImportError as e:
    print(f"⚠️ Vitals tracker not available: {e}")
    VITALS_TRACKER_AVAILABLE = False

# Import medical knowledge base
try:
    from medical_knowledge_base import get_medical_knowledge_base
    MEDICAL_KNOWLEDGE_AVAILABLE = True
    print("✅ Medical knowledge base loaded successfully")
except ImportError as e:
    print(f"⚠️ Medical knowledge base not available: {e}")
    MEDICAL_KNOWLEDGE_AVAILABLE = False

# Import AI recommendation engine
try:
    from ai_recommendations import get_recommendation_engine
    AI_RECOMMENDATIONS_AVAILABLE = True
    print("✅ AI recommendation engine loaded successfully")
except ImportError as e:
    print(f"⚠️ AI recommendation engine not available: {e}")
    AI_RECOMMENDATIONS_AVAILABLE = False

# Import similar cases engine
try:
    from similar_cases import get_similar_cases_engine
    SIMILAR_CASES_AVAILABLE = True
    print("✅ Similar cases engine loaded successfully")
except ImportError as e:
    print(f"⚠️ Similar cases engine not available: {e}")
    SIMILAR_CASES_AVAILABLE = False

# Import skin analysis history
try:
    from skin_analysis_history import get_skin_analysis_history
    SKIN_ANALYSIS_HISTORY_AVAILABLE = True
    print("✅ Skin analysis history loaded successfully")
except ImportError as e:
    print(f"⚠️ Skin analysis history not available: {e}")
    SKIN_ANALYSIS_HISTORY_AVAILABLE = False

# Import audio health history (NEW - for multimodal audio)
try:
    from audio_health_history import get_audio_health_history
    AUDIO_HEALTH_HISTORY_AVAILABLE = True
    print("✅ Audio health history loaded successfully")
except ImportError as e:
    print(f"⚠️ Audio health history not available: {e}")
    AUDIO_HEALTH_HISTORY_AVAILABLE = False

# Import multimodal embeddings (NEW)
try:
    from multimodal_embeddings import get_embedding_generator
    MULTIMODAL_EMBEDDINGS_AVAILABLE = True
    print("✅ Multimodal embeddings loaded successfully")
except ImportError as e:
    print(f"⚠️ Multimodal embeddings not available: {e}")
    MULTIMODAL_EMBEDDINGS_AVAILABLE = False

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print(f"🔑 AssemblyAI API Key: {'✅ Set' if ASSEMBLYAI_API_KEY else '❌ Missing'}")
print(f"🔑 Groq API Key: {'✅ Set' if GROQ_API_KEY else '❌ Missing'}")

if not ASSEMBLYAI_API_KEY or not GROQ_API_KEY:
    print("❌ Missing API keys in .env file!")
    print("Please add your API keys to backend/.env file")

def transcribe_audio_file(audio_data):
    """Transcribe audio using AssemblyAI"""
    if not ASSEMBLYAI_API_KEY:
        raise Exception("AssemblyAI API key not configured")
        
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    
    try:
        # Upload audio
        print("📤 Uploading audio to AssemblyAI...")
        response = requests.post(
            "https://api.assemblyai.com/v2/upload", 
            headers=headers, 
            data=audio_data,
            timeout=30
        )
        response.raise_for_status()
        audio_url = response.json()['upload_url']
        print(f"✅ Audio uploaded: {audio_url}")

        # Request transcription
        print("🎯 Requesting transcription...")
        res = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={
                'authorization': ASSEMBLYAI_API_KEY, 
                'content-type': 'application/json'
            },
            json={'audio_url': audio_url},
            timeout=30
        )
        res.raise_for_status()
        transcript_id = res.json()['id']
        print(f"📝 Transcription ID: {transcript_id}")

        # Poll for completion
        print("⏳ Waiting for transcription...")
        for attempt in range(60):  # Increased attempts
            poll_res = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers={'authorization': ASSEMBLYAI_API_KEY},
                timeout=30
            )
            poll_res.raise_for_status()
            result = poll_res.json()
            
            print(f"📊 Status: {result['status']} (attempt {attempt + 1})")
            
            if result['status'] == 'completed':
                print("✅ Transcription completed!")
                return result['text']
            elif result['status'] == 'error':
                raise Exception(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
            
            time.sleep(2)

        raise Exception("❌ Transcription timed out after 2 minutes")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Network error with AssemblyAI: {str(e)}")
    except Exception as e:
        raise Exception(f"❌ AssemblyAI error: {str(e)}")

def call_health_assistant(messages):
    """Call Groq API for health assistance"""
    if not GROQ_API_KEY:
        raise Exception("Groq API key not configured")
        
    GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
    MODEL_NAME = "llama3-70b-8192"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
        "top_p": 0.9
    }

    try:
        print("🤖 Calling Groq API...")
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 401:
            raise Exception("Invalid Groq API key")
        elif response.status_code == 429:
            raise Exception("Groq API rate limit exceeded")
        elif response.status_code >= 500:
            raise Exception("Groq API server error")
            
        response.raise_for_status()
        result = response.json()

        if "choices" in result and result["choices"]:
            ai_response = result["choices"][0]["message"]["content"].strip()
            print("✅ Got response from Groq")
            return ai_response
        elif "error" in result:
            print(f"❌ Groq API error: {result['error']}")
            raise Exception(f"Groq API error: {result['error']}")
        else:
            raise Exception("Invalid response format from Groq")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error with Groq: {str(e)}")
    except Exception as e:
        raise Exception(f"Groq error: {str(e)}")

def detect_language(text):
    """Simple language detection for Indian languages"""
    if not text:
        return 'en'
        
    # Hindi/Devanagari
    if any('\u0900' <= char <= '\u097F' for char in text):
        return 'hi'
    # Bengali
    elif any('\u0980' <= char <= '\u09FF' for char in text):
        return 'bn'
    # Telugu
    elif any('\u0C00' <= char <= '\u0C7F' for char in text):
        return 'te'
    # Tamil
    elif any('\u0B80' <= char <= '\u0BFF' for char in text):
        return 'ta'
    # Gujarati
    elif any('\u0A80' <= char <= '\u0AFF' for char in text):
        return 'gu'
    # Kannada
    elif any('\u0C80' <= char <= '\u0CFF' for char in text):
        return 'kn'
    # Malayalam
    elif any('\u0D00' <= char <= '\u0D7F' for char in text):
        return 'ml'
    # Punjabi
    elif any('\u0A00' <= char <= '\u0A7F' for char in text):
        return 'pa'
    # Odia
    elif any('\u0B00' <= char <= '\u0B7F' for char in text):
        return 'or'
    # Urdu/Arabic
    elif any('\u0600' <= char <= '\u06FF' for char in text):
        return 'ur'
    else:
        return 'en'

@app.route('/api/health-chat', methods=['POST'])
def health_chat():
    """Main health chat endpoint with patient memory integration"""
    try:
        print("💬 Received chat request")
        data = request.json
        message = data.get('message', '').strip()
        language = data.get('language', 'en')
        chat_history = data.get('chatHistory', [])
        patient_id = data.get('patientId', 'default_patient')  # Should come from auth in production
        
        if not message:
            return jsonify({
                'error': 'Message is required',
                'success': False
            }), 400
        
        print(f"📝 Message: {message}")
        print(f"🌐 Language: {language}")
        print(f"👤 Patient ID: {patient_id}")
        
        # Detect language if not provided or auto
        if not language or language == 'auto':
            language = detect_language(message)
            print(f"🔍 Detected language: {language}")
        
        # Initialize context from memory
        relevant_context = ""
        
        # Retrieve relevant conversations from Qdrant if available
        if PATIENT_MEMORY_AVAILABLE:
            try:
                memory_system = get_memory_system()
                
                # Retrieve last 5 relevant conversations based on semantic similarity
                relevant_conversations = memory_system.retrieve_relevant_conversations(
                    patient_id=patient_id,
                    query=message,
                    limit=5
                )
                
                if relevant_conversations:
                    relevant_context = memory_system.format_context_for_prompt(relevant_conversations)
                    print(f"🧠 Retrieved {len(relevant_conversations)} relevant past conversations")
                else:
                    print("📝 No previous conversations found for this patient")
                    
            except Exception as e:
                print(f"⚠️ Error retrieving patient memory: {e}")
                # Continue without memory if there's an error
        
        # Prepare system prompt based on language
        language_names = {
            'hi': 'Hindi',
            'en': 'English',
            'bn': 'Bengali',
            'te': 'Telugu',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'or': 'Odia',
            'as': 'Assamese',
            'ur': 'Urdu',
            'ne': 'Nepali',
            'si': 'Sinhala'
        }
        
        lang_name = language_names.get(language, 'English')
        
        # Enhanced system prompt with context
        system_content = f"""You are CareMate, a multilingual AI health assistant focused on helping Indian users understand their symptoms and health concerns.

CRITICAL INSTRUCTIONS:
- Respond ONLY in {lang_name} language
- If the user writes in {lang_name}, respond in {lang_name}
- Provide empathetic, culturally sensitive responses
- Ask follow-up questions to understand symptoms better
- Suggest safe home remedies when appropriate (like hydration, steam inhalation, rest)
- Clearly explain when they should consult a doctor immediately
- Consider Indian healthcare context and accessibility
- Be supportive and understanding of health anxieties

ALWAYS provide:
- Empathetic responses that acknowledge their concerns
- Safe home care suggestions when appropriate
- Clear guidance on when to see a doctor (red flags)
- Cultural sensitivity for Indian healthcare context
- Follow-up questions to better understand their condition

ALWAYS end with: "Would you like me to continue checking your symptoms or do you need help connecting to a doctor?"

Remember: You are not replacing medical diagnosis but helping users understand their symptoms and when to seek professional help."""

        # Add relevant context if available
        if relevant_context:
            system_content += f"\n\nPATIENT CONTEXT (Previous relevant interactions):\n{relevant_context}\n\nUse this context to provide continuity in care and remember previous symptoms or conditions discussed."
        
        system_prompt = {
            "role": "system",
            "content": system_content
        }
        
        # Prepare messages for API
        api_messages = [system_prompt]
        
        # Add recent chat history (last 5 messages to avoid token limits)
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        for msg in recent_history:
            if msg.get('role') in ['user', 'assistant']:
                api_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current user message
        api_messages.append({"role": "user", "content": message})
        
        print(f"📤 Sending {len(api_messages)} messages to Groq")
        
        # Get AI response
        reply = call_health_assistant(api_messages)
        
        print("✅ Successfully got AI response")
        
        # Store conversation in Qdrant for future context
        if PATIENT_MEMORY_AVAILABLE:
            try:
                memory_system = get_memory_system()
                
                # Extract symptoms from user message
                symptoms = memory_system.extract_symptoms(message)
                
                # Store the conversation
                conversation_id = memory_system.store_conversation(
                    patient_id=patient_id,
                    user_message=message,
                    assistant_response=reply,
                    language=language,
                    symptoms=symptoms,
                    metadata={
                        "timestamp": datetime.datetime.now().isoformat(),
                        "has_relevant_context": bool(relevant_context)
                    }
                )
                
                print(f"💾 Stored conversation with ID: {conversation_id}")
                
            except Exception as e:
                print(f"⚠️ Error storing conversation: {e}")
                # Continue even if storage fails
        
        return jsonify({
            'response': reply,
            'language': language,
            'success': True,
            'timestamp': datetime.datetime.now().isoformat(),
            'contextUsed': bool(relevant_context)
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error in health_chat: {error_msg}")
        
        # Return language-specific error messages
        error_messages = {
            'hi': 'क्षमा करें, मुझे अभी कनेक्ट करने में समस्या हो रही है। कृपया कुछ देर बाद पुनः प्रयास करें।',
            'en': 'Sorry, I\'m having trouble connecting right now. Please try again in a moment.',
            'bn': 'দুঃখিত, আমি এখন সংযোগ করতে সমস্যা হচ্ছে। অনুগ্রহ করে একটু পরে আবার চেষ্টা করুন।',
            'te': 'క్షమించండి, నేను ఇప్పుడు కనెక్ట్ చేయడంలో సమస్య ఎదుర్కొంటున్నాను। దయచేసి కొంత సమయం తర్వాత మళ్లీ ప్రయత్నించండి।'
        }
        
        language = data.get('language', 'en') if 'data' in locals() else 'en'
        error_response = error_messages.get(language, error_messages['en'])
        
        return jsonify({
            'error': error_response,
            'technical_error': error_msg,
            'success': False
        }), 500

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Audio transcription endpoint"""
    try:
        print("🎤 Received transcription request")
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided', 'success': False}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected', 'success': False}), 400
            
        print(f"📁 Audio file: {audio_file.filename}, Size: {len(audio_file.read())} bytes")
        audio_file.seek(0)  # Reset file pointer
        
        audio_data = audio_file.read()
        
        if len(audio_data) == 0:
            return jsonify({'error': 'Empty audio file', 'success': False}), 400
        
        # Transcribe audio
        transcript = transcribe_audio_file(audio_data)
        
        if not transcript or transcript.strip() == '':
            return jsonify({
                'transcript': '',
                'language': 'en',
                'success': True,
                'message': 'No speech detected'
            })
        
        # Detect language
        language = detect_language(transcript)
        
        print(f"✅ Transcription successful: {transcript[:50]}...")
        
        return jsonify({
            'transcript': transcript,
            'language': language,
            'success': True
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Transcription error: {error_msg}")
        return jsonify({
            'error': f'Transcription failed: {error_msg}',
            'success': False
        }), 500

@app.route('/api/analyze-skin', methods=['POST'])
def analyze_skin():
    """Enhanced skin analysis endpoint using Google Gemini AI"""
    try:
        print("🔍 Received skin analysis request")
        
        if not SKIN_ANALYSIS_AVAILABLE:
            return jsonify({
                'error': 'Skin analysis service not available',
                'success': False
            }), 503
        
        # Check if image is provided
        if 'image' not in request.files and 'imageData' not in request.json:
            return jsonify({
                'error': 'No image provided',
                'success': False
            }), 400
        
        # Get user language preference
        user_language = request.form.get('language', 'en')
        if request.json:
            user_language = request.json.get('language', 'en')
        
        # Get patient ID if provided (for history tracking)
        patient_id = request.form.get('patient_id')
        if request.json:
            patient_id = request.json.get('patient_id')
        
        # Get store_history preference
        store_history = request.form.get('store_history', 'true').lower() == 'true'
        if request.json:
            store_history = request.json.get('store_history', True)
        
        print(f"🌐 User language: {user_language}")
        if patient_id:
            print(f"👤 Patient ID: {patient_id}")
        print(f"💾 Store in history: {store_history}")
        
        # Handle image data
        image_data = None
        if 'image' in request.files:
            # Handle file upload
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({
                    'error': 'No image file selected',
                    'success': False
                }), 400
            
            image_data = image_file.read()
            print(f"📁 Image file uploaded: {len(image_data)} bytes")
            
        elif request.json and 'imageData' in request.json:
            # Handle base64 image data
            image_data = request.json['imageData']
            print("📷 Base64 image data received")
        
        if not image_data:
            return jsonify({
                'error': 'Invalid image data',
                'success': False
            }), 400
        
        # Analyze with Gemini AI (with history integration)
        print("🧠 Starting Gemini AI analysis...")
        analysis_result = analyze_skin_with_gemini(
            image_data, 
            user_language,
            patient_id=patient_id,
            store_history=store_history
        )
        
        # Generate audio response if requested
        generate_audio = request.form.get('generateAudio', 'false').lower() == 'true'
        if request.json:
            generate_audio = request.json.get('generateAudio', False)
        
        audio_response = None
        if generate_audio:
            print("🔊 Generating audio response...")
            audio_response = generate_audio_response(analysis_result, user_language)
        
        print("✅ Skin analysis completed successfully")
        
        response_data = {
            'analysis': analysis_result,
            'language': user_language,
            'success': True,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if audio_response:
            response_data['audio'] = audio_response
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Skin analysis error: {error_msg}")
        
        return jsonify({
            'error': f'Skin analysis failed: {error_msg}',
            'success': False
        }), 500

@app.route('/api/detect-language', methods=['POST'])
def detect_lang():
    """Language detection endpoint"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required', 'success': False}), 400
        
        language = detect_language(text)
        
        return jsonify({
            'language': language,
            'confidence': 0.9,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/patient/history', methods=['GET'])
def get_patient_history():
    """Get patient conversation history"""
    try:
        patient_id = request.args.get('patientId', 'default_patient')
        limit = int(request.args.get('limit', 10))
        
        if not PATIENT_MEMORY_AVAILABLE:
            return jsonify({
                'error': 'Patient memory system not available',
                'success': False
            }), 503
        
        memory_system = get_memory_system()
        history = memory_system.get_patient_history(patient_id, limit)
        
        return jsonify({
            'history': history,
            'count': len(history),
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error retrieving patient history: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/patient/relevant-context', methods=['POST'])
def get_relevant_context():
    """Get relevant conversation context for a query"""
    try:
        data = request.json
        patient_id = data.get('patientId', 'default_patient')
        query = data.get('query', '')
        limit = int(data.get('limit', 5))
        
        if not query:
            return jsonify({
                'error': 'Query is required',
                'success': False
            }), 400
        
        if not PATIENT_MEMORY_AVAILABLE:
            return jsonify({
                'error': 'Patient memory system not available',
                'success': False
            }), 503
        
        memory_system = get_memory_system()
        relevant_conversations = memory_system.retrieve_relevant_conversations(
            patient_id, query, limit
        )
        
        context = memory_system.format_context_for_prompt(relevant_conversations)
        
        return jsonify({
            'conversations': relevant_conversations,
            'formattedContext': context,
            'count': len(relevant_conversations),
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error retrieving relevant context: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/patient/delete', methods=['DELETE'])
def delete_patient_data():
    """Delete all patient data (GDPR compliance)"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        
        if not patient_id:
            return jsonify({
                'error': 'Patient ID is required',
                'success': False
            }), 400
        
        if not PATIENT_MEMORY_AVAILABLE:
            return jsonify({
                'error': 'Patient memory system not available',
                'success': False
            }), 503
        
        memory_system = get_memory_system()
        deleted_count = memory_system.delete_patient_data(patient_id)
        
        return jsonify({
            'deletedCount': deleted_count,
            'success': True,
            'message': f'Deleted {deleted_count} records for patient {patient_id}'
        })
        
    except Exception as e:
        print(f"❌ Error deleting patient data: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/vitals/store', methods=['POST'])
def store_vitals():
    """Store patient vitals"""
    try:
        data = request.json
        patient_id = data.get('patientId', 'default_patient')
        vitals = data.get('vitals', {})
        notes = data.get('notes', None)
        
        if not vitals:
            return jsonify({
                'error': 'Vitals data is required',
                'success': False
            }), 400
        
        if not VITALS_TRACKER_AVAILABLE:
            return jsonify({
                'error': 'Vitals tracker not available',
                'success': False
            }), 503
        
        tracker = get_vitals_tracker()
        vitals_id, anomalies = tracker.store_vitals(
            patient_id=patient_id,
            vitals=vitals,
            notes=notes
        )
        
        return jsonify({
            'vitalsId': vitals_id,
            'anomalies': anomalies,
            'hasAnomalies': len(anomalies) > 0,
            'success': True,
            'message': f'Vitals stored successfully with {len(anomalies)} anomaly alerts'
        })
        
    except Exception as e:
        print(f"❌ Error storing vitals: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/vitals/history', methods=['GET'])
def get_vitals_history():
    """Get patient vitals history"""
    try:
        patient_id = request.args.get('patientId', 'default_patient')
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 100))
        
        if not VITALS_TRACKER_AVAILABLE:
            return jsonify({
                'error': 'Vitals tracker not available',
                'success': False
            }), 503
        
        tracker = get_vitals_tracker()
        history = tracker.get_vitals_history(patient_id, days=days, limit=limit)
        
        return jsonify({
            'history': history,
            'count': len(history),
            'days': days,
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error retrieving vitals history: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/vitals/trend-analysis', methods=['GET'])
def get_trend_analysis():
    """Get vitals trend analysis"""
    try:
        patient_id = request.args.get('patientId', 'default_patient')
        days = int(request.args.get('days', 30))
        
        if not VITALS_TRACKER_AVAILABLE:
            return jsonify({
                'error': 'Vitals tracker not available',
                'success': False
            }), 503
        
        tracker = get_vitals_tracker()
        analysis = tracker.generate_trend_analysis(patient_id, days=days)
        
        return jsonify({
            'analysis': analysis,
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error generating trend analysis: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/vitals/anomalies', methods=['GET'])
def get_anomalous_readings():
    """Get anomalous vitals readings"""
    try:
        patient_id = request.args.get('patientId', 'default_patient')
        days = int(request.args.get('days', 30))
        
        if not VITALS_TRACKER_AVAILABLE:
            return jsonify({
                'error': 'Vitals tracker not available',
                'success': False
            }), 503
        
        tracker = get_vitals_tracker()
        anomalies = tracker.get_anomalous_readings(patient_id, days=days)
        
        return jsonify({
            'anomalies': anomalies,
            'count': len(anomalies),
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error retrieving anomalies: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/vitals/similar', methods=['POST'])
def find_similar_vitals():
    """Find similar vitals patterns"""
    try:
        data = request.json
        patient_id = data.get('patientId', 'default_patient')
        current_vitals = data.get('vitals', {})
        limit = int(data.get('limit', 10))
        
        if not current_vitals:
            return jsonify({
                'error': 'Current vitals are required',
                'success': False
            }), 400
        
        if not VITALS_TRACKER_AVAILABLE:
            return jsonify({
                'error': 'Vitals tracker not available',
                'success': False
            }), 503
        
        tracker = get_vitals_tracker()
        similar = tracker.find_similar_vitals(patient_id, current_vitals, limit=limit)
        
        return jsonify({
            'similar': similar,
            'count': len(similar),
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error finding similar vitals: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/vitals/delete', methods=['DELETE'])
def delete_patient_vitals():
    """Delete all vitals for a patient (GDPR compliance)"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        
        if not patient_id:
            return jsonify({
                'error': 'Patient ID is required',
                'success': False
            }), 400
        
        if not VITALS_TRACKER_AVAILABLE:
            return jsonify({
                'error': 'Vitals tracker not available',
                'success': False
            }), 503
        
        tracker = get_vitals_tracker()
        deleted_count = tracker.delete_patient_vitals(patient_id)
        
        return jsonify({
            'deletedCount': deleted_count,
            'success': True,
            'message': f'Deleted {deleted_count} vitals records for patient {patient_id}'
        })
        
    except Exception as e:
        print(f"❌ Error deleting patient vitals: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# ==================== Medical Knowledge Base Endpoints ====================

@app.route('/api/knowledge/search', methods=['GET'])
def search_medical_knowledge():
    """
    Search medical knowledge base with semantic search
    Query params: query (required), limit (optional, default: 3)
    """
    if not MEDICAL_KNOWLEDGE_AVAILABLE:
        return jsonify({
            'error': 'Medical knowledge base not available',
            'success': False
        }), 503
    
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({
                'error': 'Query parameter is required',
                'success': False
            }), 400
        
        limit = int(request.args.get('limit', 3))
        
        # Search knowledge base
        medical_kb = get_medical_knowledge_base()
        results = medical_kb.search_medical_knowledge(query, limit)
        
        return jsonify({
            'success': True,
            'query': query,
            'results_count': len(results),
            'results': results
        })
        
    except Exception as e:
        print(f"❌ Error searching medical knowledge: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/knowledge/conditions', methods=['GET'])
def get_all_conditions():
    """Get list of all available medical conditions"""
    if not MEDICAL_KNOWLEDGE_AVAILABLE:
        return jsonify({
            'error': 'Medical knowledge base not available',
            'success': False
        }), 503
    
    try:
        medical_kb = get_medical_knowledge_base()
        conditions = medical_kb.list_all_conditions()
        
        return jsonify({
            'success': True,
            'total_conditions': len(conditions),
            'conditions': conditions
        })
        
    except Exception as e:
        print(f"❌ Error retrieving conditions: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/knowledge/condition/<condition_key>', methods=['GET'])
def get_condition_details(condition_key: str):
    """Get detailed information about a specific condition"""
    if not MEDICAL_KNOWLEDGE_AVAILABLE:
        return jsonify({
            'error': 'Medical knowledge base not available',
            'success': False
        }), 503
    
    try:
        medical_kb = get_medical_knowledge_base()
        condition = medical_kb.get_condition_details(condition_key)
        
        if not condition:
            return jsonify({
                'error': f'Condition "{condition_key}" not found',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'condition': condition
        })
        
    except Exception as e:
        print(f"❌ Error retrieving condition details: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/knowledge/category/<category>', methods=['GET'])
def search_by_category(category: str):
    """Get all conditions in a specific category"""
    if not MEDICAL_KNOWLEDGE_AVAILABLE:
        return jsonify({
            'error': 'Medical knowledge base not available',
            'success': False
        }), 503
    
    try:
        medical_kb = get_medical_knowledge_base()
        conditions = medical_kb.search_by_category(category)
        
        return jsonify({
            'success': True,
            'category': category,
            'total_conditions': len(conditions),
            'conditions': conditions
        })
        
    except Exception as e:
        print(f"❌ Error searching by category: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# ==================== AI Recommendation System Endpoints ====================

@app.route('/api/recommendations/generate', methods=['POST'])
def generate_recommendations():
    """
    Generate personalized health recommendations for a patient
    Body: { patient_id, include_vitals, include_history, max_recommendations }
    """
    if not AI_RECOMMENDATIONS_AVAILABLE:
        return jsonify({
            'error': 'AI recommendation engine not available',
            'success': False
        }), 503
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({
                'error': 'patient_id is required',
                'success': False
            }), 400
        
        include_vitals = data.get('include_vitals', True)
        include_history = data.get('include_history', True)
        max_recommendations = data.get('max_recommendations', 15)
        
        # Generate recommendations
        engine = get_recommendation_engine()
        result = engine.generate_recommendations(
            patient_id=patient_id,
            include_vitals=include_vitals,
            include_history=include_history,
            max_recommendations=max_recommendations
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/recommendations/history', methods=['GET'])
def get_recommendation_history():
    """
    Get past recommendations for a patient
    Query params: patient_id (required), limit (optional, default: 10)
    """
    if not AI_RECOMMENDATIONS_AVAILABLE:
        return jsonify({
            'error': 'AI recommendation engine not available',
            'success': False
        }), 503
    
    try:
        patient_id = request.args.get('patient_id')
        if not patient_id:
            return jsonify({
                'error': 'patient_id parameter is required',
                'success': False
            }), 400
        
        limit = int(request.args.get('limit', 10))
        
        # Get history
        engine = get_recommendation_engine()
        history = engine.get_recommendation_history(patient_id, limit)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'total_records': len(history),
            'history': history
        })
        
    except Exception as e:
        print(f"❌ Error retrieving recommendation history: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/recommendations/delete', methods=['DELETE'])
def delete_patient_recommendations():
    """
    Delete all recommendations for a patient (GDPR compliance)
    Body: { patient_id }
    """
    if not AI_RECOMMENDATIONS_AVAILABLE:
        return jsonify({
            'error': 'AI recommendation engine not available',
            'success': False
        }), 503
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({
                'error': 'patient_id is required',
                'success': False
            }), 400
        
        # Delete recommendations
        engine = get_recommendation_engine()
        deleted_count = engine.delete_patient_recommendations(patient_id)
        
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} recommendation records for patient {patient_id}',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"❌ Error deleting recommendations: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/similar-cases/find', methods=['POST'])
def find_similar_cases():
    """Find similar patient cases for clinical decision support"""
    if not SIMILAR_CASES_AVAILABLE:
        return jsonify({
            'error': 'Similar cases engine not available',
            'success': False
        }), 503
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        top_k = data.get('top_k', 5)
        min_similarity = data.get('min_similarity', 0.3)
        
        if not patient_id:
            return jsonify({
                'error': 'patient_id is required',
                'success': False
            }), 400
        
        # Find similar cases
        engine = get_similar_cases_engine()
        similar_cases = engine.find_similar_cases(
            patient_id=patient_id,
            top_k=top_k,
            min_similarity=min_similarity
        )
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'total_cases_found': len(similar_cases),
            'similar_cases': similar_cases,
            'search_params': {
                'top_k': top_k,
                'min_similarity': min_similarity
            }
        })
        
    except Exception as e:
        print(f"❌ Error finding similar cases: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/similar-cases/index', methods=['POST'])
def index_patient_case():
    """Index a patient case for future similarity searches"""
    if not SIMILAR_CASES_AVAILABLE:
        return jsonify({
            'error': 'Similar cases engine not available',
            'success': False
        }), 503
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        case_date = data.get('case_date')
        symptoms = data.get('symptoms', [])
        conditions = data.get('conditions', [])
        vitals_summary = data.get('vitals_summary', {})
        demographics = data.get('demographics', {})
        treatments = data.get('treatments', [])
        outcome = data.get('outcome')
        case_notes = data.get('case_notes')
        
        if not patient_id or not case_date:
            return jsonify({
                'error': 'patient_id and case_date are required',
                'success': False
            }), 400
        
        # Index the case
        engine = get_similar_cases_engine()
        case_id = engine.index_patient_case(
            patient_id=patient_id,
            case_date=case_date,
            symptoms=symptoms,
            conditions=conditions,
            vitals_summary=vitals_summary,
            demographics=demographics,
            treatments=treatments,
            outcome=outcome,
            case_notes=case_notes
        )
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'message': f'Case indexed successfully for patient {patient_id}'
        })
        
    except Exception as e:
        print(f"❌ Error indexing case: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/similar-cases/statistics', methods=['GET'])
def get_case_statistics():
    """Get statistics about indexed cases"""
    if not SIMILAR_CASES_AVAILABLE:
        return jsonify({
            'error': 'Similar cases engine not available',
            'success': False
        }), 503
    
    try:
        engine = get_similar_cases_engine()
        stats = engine.get_case_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        print(f"❌ Error getting case statistics: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/similar-cases/delete', methods=['DELETE'])
def delete_patient_cases():
    """Delete all cases for a patient (GDPR compliance)"""
    if not SIMILAR_CASES_AVAILABLE:
        return jsonify({
            'error': 'Similar cases engine not available',
            'success': False
        }), 503
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({
                'error': 'patient_id is required',
                'success': False
            }), 400
        
        # Delete cases
        engine = get_similar_cases_engine()
        deleted_count = engine.delete_patient_cases(patient_id)
        
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} cases for patient {patient_id}',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"❌ Error deleting cases: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/skin-analysis/similar-cases', methods=['POST'])
def find_similar_skin_cases():
    """Find similar historical skin analysis cases"""
    if not SKIN_ANALYSIS_HISTORY_AVAILABLE:
        return jsonify({
            'error': 'Skin analysis history not available',
            'success': False
        }), 503
    
    try:
        data = request.get_json()
        diagnosis = data.get('diagnosis')
        severity = data.get('severity')
        recommendations = data.get('recommendations', [])
        affected_areas = data.get('affected_areas', [])
        top_k = data.get('top_k', 5)
        min_confidence = data.get('min_confidence', 0.0)
        
        if not diagnosis:
            return jsonify({
                'error': 'diagnosis is required',
                'success': False
            }), 400
        
        history = get_skin_analysis_history()
        similar_cases = history.find_similar_cases(
            diagnosis=diagnosis,
            severity=severity,
            recommendations=recommendations,
            affected_areas=affected_areas,
            top_k=top_k,
            min_confidence=min_confidence
        )
        
        return jsonify({
            'success': True,
            'similar_cases': similar_cases,
            'total_found': len(similar_cases)
        })
        
    except Exception as e:
        print(f"❌ Error finding similar skin cases: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/skin-analysis/patient-history', methods=['GET'])
def get_patient_skin_history():
    """Get patient's skin analysis history"""
    if not SKIN_ANALYSIS_HISTORY_AVAILABLE:
        return jsonify({
            'error': 'Skin analysis history not available',
            'success': False
        }), 503
    
    try:
        patient_id = request.args.get('patient_id')
        limit = int(request.args.get('limit', 10))
        
        if not patient_id:
            return jsonify({
                'error': 'patient_id is required',
                'success': False
            }), 400
        
        history = get_skin_analysis_history()
        patient_history = history.get_patient_history(patient_id, limit)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'history': patient_history,
            'total_records': len(patient_history)
        })
        
    except Exception as e:
        print(f"❌ Error getting patient history: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/skin-analysis/statistics', methods=['GET'])
def get_skin_analysis_statistics():
    """Get skin analysis database statistics"""
    if not SKIN_ANALYSIS_HISTORY_AVAILABLE:
        return jsonify({
            'error': 'Skin analysis history not available',
            'success': False
        }), 503
    
    try:
        history = get_skin_analysis_history()
        stats = history.get_category_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/skin-analysis/delete', methods=['DELETE'])
def delete_patient_skin_analyses():
    """Delete patient's skin analysis history (GDPR)"""
    if not SKIN_ANALYSIS_HISTORY_AVAILABLE:
        return jsonify({
            'error': 'Skin analysis history not available',
            'success': False
        }), 503
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({
                'error': 'patient_id is required',
                'success': False
            }), 400
        
        history = get_skin_analysis_history()
        deleted_count = history.delete_patient_analyses(patient_id)
        
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} skin analyses for patient {patient_id}',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"❌ Error deleting analyses: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# ============================================================================
# MULTIMODAL SEARCH ENDPOINTS (NEW)
# ============================================================================

@app.route('/api/skin-analysis/search-by-image', methods=['POST'])
def search_similar_skin_images():
    """
    Image-to-image search: Upload skin image, find visually similar cases
    TRUE multimodal search using CLIP embeddings in Qdrant
    """
    try:
        print("🔍 Received image-to-image search request")
        
        if not SKIN_ANALYSIS_HISTORY_AVAILABLE:
            return jsonify({
                'error': 'Skin analysis history not available',
                'similar_images': []
            }), 503
        
        # Get request data
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        top_k = data.get('top_k', 10)
        severity_filter = data.get('severity_filter', None)
        category_filter = data.get('category_filter', None)
        
        # Search for visually similar images
        history = get_skin_analysis_history()
        similar_cases = history.find_similar_images(
            image_data=image_data,
            top_k=top_k,
            severity_filter=severity_filter,
            category_filter=category_filter
        )
        
        print(f"✅ Found {len(similar_cases)} visually similar skin conditions")
        
        return jsonify({
            'success': True,
            'query_type': 'image_to_image',
            'similar_cases': similar_cases,
            'count': len(similar_cases),
            'message': f'Found {len(similar_cases)} visually similar cases using CLIP embeddings'
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Image search error: {error_msg}")
        return jsonify({
            'error': f'Image search failed: {error_msg}',
            'similar_cases': []
        }), 500


@app.route('/api/skin-analysis/search-by-text', methods=['POST'])
def search_skin_by_text():
    """
    Cross-modal search: Text query → Image results
    Example: "Show me eczema on elbows" → Returns actual images
    """
    try:
        print("🔍 Received text-to-image search request")
        
        if not SKIN_ANALYSIS_HISTORY_AVAILABLE:
            return jsonify({
                'error': 'Skin analysis history not available',
                'results': []
            }), 503
        
        # Get request data
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'No query text provided'}), 400
        
        text_query = data['query']
        top_k = data.get('top_k', 10)
        
        # Cross-modal search
        history = get_skin_analysis_history()
        matching_cases = history.find_by_text_query(
            text_query=text_query,
            search_in_images=True,
            top_k=top_k
        )
        
        print(f"✅ Found {len(matching_cases)} images matching '{text_query}'")
        
        return jsonify({
            'success': True,
            'query': text_query,
            'query_type': 'text_to_image',
            'matching_cases': matching_cases,
            'count': len(matching_cases),
            'message': f'Cross-modal search found {len(matching_cases)} matching images'
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Text-to-image search error: {error_msg}")
        return jsonify({
            'error': f'Search failed: {error_msg}',
            'results': []
        }), 500


@app.route('/api/audio-health/store', methods=['POST'])
def store_audio_health_analysis():
    """
    Store cough/respiratory audio analysis with multimodal embeddings
    """
    try:
        print("🎵 Received audio health analysis storage request")
        
        if not AUDIO_HEALTH_HISTORY_AVAILABLE:
            return jsonify({
                'error': 'Audio health history not available'
            }), 503
        
        # Get request data
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields
        required_fields = ['patient_id', 'cough_description', 'cough_type', 'severity', 'duration_seconds', 'frequency']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Store analysis
        history = get_audio_health_history()
        case_id = history.store_audio_analysis(
            patient_id=data['patient_id'],
            audio_data=data.get('audio_data', None),  # Optional audio bytes/path
            cough_description=data['cough_description'],
            cough_type=data['cough_type'],
            severity=data['severity'],
            duration_seconds=data['duration_seconds'],
            frequency=data['frequency'],
            associated_symptoms=data.get('associated_symptoms', []),
            confidence=data.get('confidence', 0.8),
            diagnosis=data.get('diagnosis', ''),
            recommendations=data.get('recommendations', [])
        )
        
        print(f"✅ Stored audio analysis: {case_id}")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'message': 'Audio health analysis stored with multimodal embeddings'
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Audio storage error: {error_msg}")
        return jsonify({
            'error': f'Failed to store audio analysis: {error_msg}'
        }), 500


@app.route('/api/audio-health/search-by-audio', methods=['POST'])
def search_similar_audio():
    """
    Audio-to-audio search: Upload cough recording, find acoustically similar cases
    TRUE multimodal search using Wav2Vec2 embeddings in Qdrant
    """
    try:
        print("🔍 Received audio-to-audio search request")
        
        if not AUDIO_HEALTH_HISTORY_AVAILABLE:
            return jsonify({
                'error': 'Audio health history not available',
                'similar_audio': []
            }), 503
        
        # Get request data
        data = request.json
        if not data or 'audio_data' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        audio_data = data['audio_data']
        top_k = data.get('top_k', 10)
        severity_filter = data.get('severity_filter', None)
        cough_type_filter = data.get('cough_type_filter', None)
        
        # Search for acoustically similar audio
        history = get_audio_health_history()
        similar_cases = history.find_similar_audio(
            audio_data=audio_data,
            top_k=top_k,
            severity_filter=severity_filter,
            cough_type_filter=cough_type_filter
        )
        
        print(f"✅ Found {len(similar_cases)} acoustically similar coughs")
        
        return jsonify({
            'success': True,
            'query_type': 'audio_to_audio',
            'similar_cases': similar_cases,
            'count': len(similar_cases),
            'message': f'Found {len(similar_cases)} acoustically similar cases using Wav2Vec2 embeddings'
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Audio search error: {error_msg}")
        return jsonify({
            'error': f'Audio search failed: {error_msg}',
            'similar_audio': []
        }), 500


@app.route('/api/audio-health/search-by-description', methods=['POST'])
def search_audio_by_description():
    """
    Text-based search for audio cases
    Example: "persistent dry cough at night"
    """
    try:
        print("🔍 Received text-based audio search request")
        
        if not AUDIO_HEALTH_HISTORY_AVAILABLE:
            return jsonify({
                'error': 'Audio health history not available',
                'results': []
            }), 503
        
        # Get request data
        data = request.json
        if not data or 'description' not in data:
            return jsonify({'error': 'No description provided'}), 400
        
        description = data['description']
        top_k = data.get('top_k', 10)
        severity_filter = data.get('severity_filter', None)
        
        # Search by description
        history = get_audio_health_history()
        matching_cases = history.find_by_description(
            cough_description=description,
            top_k=top_k,
            severity_filter=severity_filter
        )
        
        print(f"✅ Found {len(matching_cases)} cases matching description")
        
        return jsonify({
            'success': True,
            'query': description,
            'matching_cases': matching_cases,
            'count': len(matching_cases)
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Description search error: {error_msg}")
        return jsonify({
            'error': f'Search failed: {error_msg}',
            'results': []
        }), 500


@app.route('/api/audio-health/patient-history/<patient_id>', methods=['GET'])
def get_audio_patient_history(patient_id):
    """
    Get audio health history for a specific patient
    """
    try:
        if not AUDIO_HEALTH_HISTORY_AVAILABLE:
            return jsonify({
                'error': 'Audio health history not available',
                'history': []
            }), 503
        
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        history = get_audio_health_history()
        patient_history = history.get_patient_audio_history(
            patient_id=patient_id,
            days=days,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'history': patient_history,
            'count': len(patient_history)
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error getting patient audio history: {error_msg}")
        return jsonify({
            'error': f'Failed to get history: {error_msg}',
            'history': []
        }), 500


@app.route('/api/multimodal/status', methods=['GET'])
def multimodal_status():
    """
    Check status of multimodal embedding capabilities
    """
    status = {
        'multimodal_available': MULTIMODAL_EMBEDDINGS_AVAILABLE,
        'skin_analysis_history': SKIN_ANALYSIS_HISTORY_AVAILABLE,
        'audio_health_history': AUDIO_HEALTH_HISTORY_AVAILABLE
    }
    
    if MULTIMODAL_EMBEDDINGS_AVAILABLE:
        try:
            embedding_gen = get_embedding_generator()
            status['models'] = embedding_gen.is_available()
            status['dimensions'] = embedding_gen.get_embedding_dimensions()
        except Exception as e:
            status['error'] = str(e)
    
    return jsonify(status)


# ============================================================================
# END MULTIMODAL ENDPOINTS
# ============================================================================

# ============================================================================
# EVIDENCE TRACKING ENDPOINTS - Show Qdrant Retrieval Traceability
# ============================================================================

@app.route('/api/evidence/log', methods=['GET'])
def get_evidence_log():
    """
    Get evidence log showing what was retrieved from Qdrant
    
    Query params:
        - decision_type: Filter by decision type (optional)
        - limit: Number of entries (default: 10)
    """
    try:
        from evidence_logger import get_evidence_logger
        
        decision_type = request.args.get('decision_type')
        limit = int(request.args.get('limit', 10))
        
        evidence_logger = get_evidence_logger()
        evidence = evidence_logger.get_evidence_for_decision(decision_type, limit)
        
        return jsonify({
            'success': True,
            'evidence_log': evidence,
            'count': len(evidence)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evidence/report', methods=['GET'])
def get_evidence_report():
    """
    Get comprehensive evidence report with statistics
    
    Shows:
    - Total decisions made
    - Total vector retrievals from Qdrant
    - Average similarity scores
    - Collection usage breakdown
    - Decision type distribution
    """
    try:
        from evidence_logger import get_evidence_logger
        
        evidence_logger = get_evidence_logger()
        report = evidence_logger.generate_evidence_report()
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evidence/trace/<int:decision_index>', methods=['GET'])
def get_evidence_trace(decision_index):
    """
    Get detailed trace for a specific decision
    
    Returns:
    - Complete decision info
    - All vectors retrieved from Qdrant
    - Similarity scores
    - How retrieval influenced decision
    - Visualization data (graph nodes/edges)
    """
    try:
        from evidence_logger import get_evidence_logger
        
        evidence_logger = get_evidence_logger()
        trace = evidence_logger.export_evidence_trace(decision_index)
        
        return jsonify({
            'success': True,
            'trace': trace
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evidence/clear', methods=['POST'])
def clear_evidence_log():
    """Clear evidence log (for testing)"""
    try:
        from evidence_logger import get_evidence_logger
        
        evidence_logger = get_evidence_logger()
        evidence_logger.clear_log()
        
        return jsonify({
            'success': True,
            'message': 'Evidence log cleared'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# END EVIDENCE TRACKING ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'apis': {
            'assemblyai': '✅ Configured' if ASSEMBLYAI_API_KEY else '❌ Missing',
            'groq': '✅ Configured' if GROQ_API_KEY else '❌ Missing',
            'patient_memory': '✅ Available' if PATIENT_MEMORY_AVAILABLE else '❌ Not Available',
            'vitals_tracker': '✅ Available' if VITALS_TRACKER_AVAILABLE else '❌ Not Available',
            'medical_knowledge': '✅ Available' if MEDICAL_KNOWLEDGE_AVAILABLE else '❌ Not Available',
            'ai_recommendations': '✅ Available' if AI_RECOMMENDATIONS_AVAILABLE else '❌ Not Available',
            'similar_cases': '✅ Available' if SIMILAR_CASES_AVAILABLE else '❌ Not Available',
            'skin_analysis_history': '✅ Available' if SKIN_ANALYSIS_HISTORY_AVAILABLE else '❌ Not Available',
            'audio_health_history': '✅ Available' if AUDIO_HEALTH_HISTORY_AVAILABLE else '❌ Not Available',
            'multimodal_embeddings': '✅ Available' if MULTIMODAL_EMBEDDINGS_AVAILABLE else '❌ Not Available'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting CareMate Backend Server...")
    print("📍 Server will run on: http://localhost:5000")
    print("🔧 Make sure to set your API keys in backend/.env file")
    app.run(debug=True, port=5000, host='0.0.0.0')