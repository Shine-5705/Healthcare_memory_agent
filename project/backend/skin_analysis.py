import google.generativeai as genai
from PIL import Image
import pyttsx3
import threading
import time
from googletrans import Translator
import io
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import skin analysis history
try:
    from skin_analysis_history import get_skin_analysis_history
    HISTORY_AVAILABLE = True
    print("✅ Skin analysis history module loaded")
except ImportError as e:
    print(f"⚠️ Skin analysis history not available: {e}")
    HISTORY_AVAILABLE = False

# Load environment variables
load_dotenv()

# ===== Setup Gemini API =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully")
else:
    print("❌ Gemini API key not found in environment variables")

# ===== Setup Text-to-Speech =====
try:
    engine = pyttsx3.init()
    speech_lock = threading.Lock()
    print("✅ Text-to-speech engine initialized")
except Exception as e:
    print(f"⚠️ Text-to-speech initialization failed: {e}")
    engine = None
    speech_lock = None

def speak(text, lang='en'):
    """Convert text to speech in specified language"""
    if not engine:
        return None
        
    try:
        voices = engine.getProperty('voices')
        # Try to find a voice for the specified language
        for voice in voices:
            if hasattr(voice, 'languages') and lang in voice.languages:
                engine.setProperty('voice', voice.id)
                break
            elif hasattr(voice, 'id') and lang in voice.id:
                engine.setProperty('voice', voice.id)
                break
        
        def _speak():
            with speech_lock:
                engine.say(text)
                engine.runAndWait()
        
        thread = threading.Thread(target=_speak)
        thread.start()
        return thread
    except Exception as e:
        print(f"Speech error: {e}")
        return None

def stop_speech():
    """Stop ongoing speech"""
    if engine and speech_lock:
        with speech_lock:
            engine.stop()

# ===== Setup Translator =====
translator = Translator()

def translate_text(text, target_lang='en'):
    """Translate text to target language"""
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

def detect_language(text):
    """Detect language of input text"""
    try:
        result = translator.detect(text)
        return result.lang
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'en'  # Default to English

def analyze_skin_with_gemini(image_data, user_language='en', patient_id=None, store_history=True):
    """
    Analyze skin condition using Google Gemini AI with historical case comparison
    
    Args:
        image_data: PIL Image object or image bytes
        user_language: Target language for response
        patient_id: Patient identifier for history tracking (optional)
        store_history: Whether to store analysis in history (default: True)
    
    Returns:
        dict: Analysis results with diagnosis, recommendations, and similar cases
    """
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key not configured")
    
    try:
        # Convert image data to PIL Image if needed
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            # Handle base64 encoded images
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            image = image_data
        
        # Enhanced medical prompt for comprehensive analysis
        prompt = f"""
You are an expert AI dermatologist and medical assistant. Analyze this skin image comprehensively and provide detailed medical guidance.

Please analyze the image and provide a JSON response with the following structure:

{{
    "condition": "Primary skin condition identified",
    "confidence": 0.85,
    "severity": "mild|moderate|severe",
    "description": "Detailed medical description of observed condition",
    "symptoms_observed": ["List of visible symptoms"],
    "possible_causes": ["Likely causes of this condition"],
    "immediate_first_aid": ["Step-by-step first aid instructions"],
    "home_remedies": ["Safe home treatment options"],
    "medications": ["Over-the-counter treatment suggestions"],
    "when_to_see_doctor": ["Warning signs requiring medical attention"],
    "prevention_tips": ["How to prevent recurrence"],
    "healing_timeline": "Expected recovery timeframe",
    "urgency_level": "low|medium|high|emergency",
    "additional_notes": "Any other important medical information"
}}

Focus on:
1. **Injury Assessment**: If this is an injury (cut, burn, bruise, etc.), provide detailed first aid
2. **Infection Signs**: Look for redness, swelling, pus, or other infection indicators
3. **Melanoma Screening**: Check for ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolution)
4. **Severity Assessment**: Determine if this requires immediate medical attention
5. **Cultural Sensitivity**: Consider treatments appropriate for diverse populations
6. **Safety First**: Only recommend safe, proven treatments

CRITICAL: If you detect signs of melanoma, severe infection, or emergency conditions, set urgency_level to "emergency" and emphasize immediate medical care.

Provide practical, actionable advice that a layperson can understand and follow safely.
"""

        # Use Gemini 1.5 Flash model for analysis
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🔍 Analyzing image with Gemini AI...")
        response = model.generate_content([prompt, image])
        
        diagnosis_output = response.text
        print("✅ Gemini analysis completed")
        
        # Try to parse JSON response
        try:
            # Extract JSON from response
            json_start = diagnosis_output.find('{')
            json_end = diagnosis_output.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = diagnosis_output[json_start:json_end]
                analysis_result = json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                analysis_result = parse_text_response(diagnosis_output)
        
        except json.JSONDecodeError:
            # Fallback parsing if JSON format is not perfect
            analysis_result = parse_text_response(diagnosis_output)
        
        # Translate to user's preferred language if not English
        if user_language != 'en':
            print(f"🌐 Translating to {user_language}...")
            analysis_result = translate_analysis_result(analysis_result, user_language)
        
        # Add original English text for reference
        analysis_result['original_english_text'] = diagnosis_output
        analysis_result['user_language'] = user_language
        
        # Store in history and find similar cases
        if HISTORY_AVAILABLE and store_history:
            try:
                history = get_skin_analysis_history()
                
                # Extract affected areas from symptoms if available
                affected_areas = []
                symptoms = analysis_result.get('symptoms_observed', [])
                body_parts = ['face', 'hands', 'arms', 'legs', 'torso', 'scalp', 'feet', 'neck', 'back']
                for symptom in symptoms:
                    for part in body_parts:
                        if part in symptom.lower():
                            affected_areas.append(part)
                
                # Store this analysis WITH IMAGE EMBEDDING
                if patient_id:
                    print("📸 Storing analysis with image embedding in Qdrant...")
                    case_id = history.store_analysis(
                        patient_id=patient_id,
                        diagnosis=analysis_result.get('condition', 'Unknown'),
                        severity=analysis_result.get('severity', 'unknown'),
                        confidence=analysis_result.get('confidence', 0.75),
                        recommendations=(
                            analysis_result.get('home_remedies', []) +
                            analysis_result.get('medications', [])
                        ),
                        image_data=image,  # PASS IMAGE DATA FOR MULTIMODAL STORAGE!
                        affected_areas=affected_areas if affected_areas else None,
                        additional_observations=analysis_result.get('description', ''),
                        follow_up_needed=analysis_result.get('urgency_level') in ['high', 'emergency']
                    )
                    analysis_result['case_id'] = case_id
                    print(f"✅ Stored with case_id: {case_id}")
                
                # Find similar historical cases (TEXT-BASED)
                similar_cases = history.find_similar_cases(
                    diagnosis=analysis_result.get('condition', ''),
                    severity=analysis_result.get('severity', 'unknown'),
                    recommendations=(
                        analysis_result.get('home_remedies', []) +
                        analysis_result.get('medications', [])
                    ),
                    affected_areas=affected_areas if affected_areas else None,
                    top_k=3,
                    min_confidence=0.6
                )
                
                analysis_result['similar_cases'] = similar_cases
                analysis_result['similar_cases_count'] = len(similar_cases)
                
                # ALSO find visually similar cases (IMAGE-BASED)
                print("🔍 Searching for visually similar skin conditions...")
                visually_similar = history.find_similar_images(
                    image_data=image,
                    top_k=5
                )
                analysis_result['visually_similar_cases'] = visually_similar
                analysis_result['visually_similar_count'] = len(visually_similar)
                
                if similar_cases:
                    print(f"✅ Found {len(similar_cases)} text-similar and {len(visually_similar)} visually-similar cases")
                    # Add pattern insights
                    analysis_result['pattern_insights'] = _generate_pattern_insights(similar_cases)
                else:
                    analysis_result['similar_cases'] = []
                    analysis_result['similar_cases_count'] = 0
                    analysis_result['pattern_insights'] = "No similar historical cases found for comparison"
                    
            except Exception as e:
                print(f"⚠️ Error with history: {e}")
                analysis_result['similar_cases'] = []
                analysis_result['similar_cases_count'] = 0
        else:
            analysis_result['similar_cases'] = []
            analysis_result['similar_cases_count'] = 0
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ Gemini analysis error: {e}")
        raise Exception(f"Failed to analyze image with Gemini: {str(e)}")

def parse_text_response(text_response):
    """Parse text response into structured format when JSON parsing fails"""
    return {
        "condition": "Skin Condition Detected",
        "confidence": 0.75,
        "severity": "moderate",
        "description": text_response[:300] + "..." if len(text_response) > 300 else text_response,
        "symptoms_observed": ["Visible skin changes", "Possible irritation"],
        "possible_causes": ["Various factors may contribute to this condition"],
        "immediate_first_aid": [
            "Keep the area clean and dry",
            "Avoid touching with unwashed hands",
            "Monitor for changes"
        ],
        "home_remedies": [
            "Apply cool compress if swollen",
            "Use gentle, fragrance-free products",
            "Keep area moisturized"
        ],
        "medications": [
            "Over-the-counter antihistamine for itching",
            "Gentle antiseptic if needed",
            "Consult pharmacist for recommendations"
        ],
        "when_to_see_doctor": [
            "If condition worsens or doesn't improve in 7-10 days",
            "If you develop fever or signs of infection",
            "If you have concerns about the appearance"
        ],
        "prevention_tips": [
            "Maintain good hygiene",
            "Avoid known irritants",
            "Protect skin from excessive sun exposure"
        ],
        "healing_timeline": "1-2 weeks with proper care",
        "urgency_level": "medium",
        "additional_notes": "Please consult a healthcare provider for proper diagnosis and treatment."
    }

def _generate_pattern_insights(similar_cases):
    """
    Generate pattern insights from similar historical cases
    
    Args:
        similar_cases: List of similar historical cases
        
    Returns:
        String with pattern insights
    """
    if not similar_cases:
        return "No historical patterns available for comparison"
    
    insights = []
    
    # Count severity distribution
    severity_counts = {}
    for case in similar_cases:
        severity = case.get('severity', 'unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    most_common_severity = max(severity_counts.items(), key=lambda x: x[1])[0]
    insights.append(f"Similar cases typically showed {most_common_severity} severity")
    
    # Check for common recommendations
    all_recommendations = []
    for case in similar_cases:
        all_recommendations.extend(case.get('recommendations', []))
    
    if all_recommendations:
        # Find most common recommendation
        from collections import Counter
        common_recs = Counter(all_recommendations).most_common(2)
        if common_recs:
            insights.append(f"Common treatments included: {common_recs[0][0]}")
    
    # Follow-up patterns
    follow_up_needed = sum(1 for case in similar_cases if case.get('follow_up_needed', False))
    if follow_up_needed > len(similar_cases) / 2:
        insights.append("Follow-up was frequently needed in similar cases")
    
    # High similarity match
    if similar_cases[0].get('similarity_score', 0) > 0.8:
        insights.append(f"Highly similar to previous case: {similar_cases[0].get('pattern_match', '')}")
    
    return ". ".join(insights) + "."

def translate_analysis_result(analysis_result, target_language):
    """Translate analysis result to target language"""
    try:
        translatable_fields = [
            'condition', 'description', 'symptoms_observed', 'possible_causes',
            'immediate_first_aid', 'home_remedies', 'medications', 
            'when_to_see_doctor', 'prevention_tips', 'healing_timeline',
            'additional_notes'
        ]
        
        translated_result = analysis_result.copy()
        
        for field in translatable_fields:
            if field in analysis_result:
                if isinstance(analysis_result[field], list):
                    translated_result[field] = [
                        translate_text(item, target_language) 
                        for item in analysis_result[field]
                    ]
                elif isinstance(analysis_result[field], str):
                    translated_result[field] = translate_text(
                        analysis_result[field], target_language
                    )
        
        return translated_result
        
    except Exception as e:
        print(f"Translation error: {e}")
        return analysis_result  # Return original if translation fails

def generate_audio_response(analysis_result, language='en'):
    """Generate audio response for the analysis"""
    try:
        # Create a summary for audio
        summary_parts = [
            f"Skin analysis complete. Condition identified: {analysis_result.get('condition', 'Unknown')}.",
            f"Severity: {analysis_result.get('severity', 'Unknown')}.",
            f"Urgency level: {analysis_result.get('urgency_level', 'Unknown')}."
        ]
        
        # Add first aid if available
        first_aid = analysis_result.get('immediate_first_aid', [])
        if first_aid:
            summary_parts.append("Immediate first aid steps: " + ". ".join(first_aid[:3]))
        
        # Add doctor consultation advice
        when_to_see_doctor = analysis_result.get('when_to_see_doctor', [])
        if when_to_see_doctor:
            summary_parts.append("See a doctor if: " + ". ".join(when_to_see_doctor[:2]))
        
        summary_text = " ".join(summary_parts)
        
        # Generate speech
        speech_thread = speak(summary_text, language)
        
        return {
            'audio_summary': summary_text,
            'speech_generated': speech_thread is not None
        }
        
    except Exception as e:
        print(f"Audio generation error: {e}")
        return {
            'audio_summary': '',
            'speech_generated': False
        }

# Test function for development
def test_skin_analysis():
    """Test function for skin analysis"""
    try:
        # Create a test image (you can replace with actual image path)
        test_image = Image.new('RGB', (224, 224), color='red')
        
        result = analyze_skin_with_gemini(test_image, 'en')
        print("✅ Test analysis successful:")
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    # Run test
    print("🧪 Testing Gemini skin analysis...")
    test_skin_analysis()