import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    import tensorflow as tf
    from tensorflow.keras.applications import EfficientNetB0
    from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
    TF_AVAILABLE = True
except Exception as _e:
    tf = None
    EfficientNetB0 = None
    preprocess_input = None
    decode_predictions = None
    TF_AVAILABLE = False
    _tf_import_error = str(_e)

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import time
try:
    from groq import Groq
except ImportError:
    Groq = None

from PIL import Image
import os
import random
import auth  # Import authentication module
import base64
import io
import cv2
import numpy as np
import tempfile

# Initialize session state variables at the start
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ==========================================
# 0. CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="Climate Guardian: A Gamified Sustainability Awareness", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

MODEL_NAME = "qwen/qwen3.8-27b"

# Configure the Groq API key and instantiate client
_groq_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""
groq_client = None
if Groq:
    if _groq_key and _groq_key not in ['YOUR_API_KEY_HERE', 'gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE']:
        try:
            groq_client = Groq(api_key=_groq_key)
        except Exception:
            groq_client = None


# --- CUSTOM CSS FOR ECO THEME ---
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Remove Top Padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Main Background - Clean Light Professional Theme */
    .stApp {
        background: linear-gradient(135deg, #f6f9fc 0%, #eef2f3 100%);
    }
    
    /* Sidebar Styling - Light & Professional */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0f7f4 100%);
        border-right: 1px solid #e0e0e0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Sidebar Text Color */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #2c3e50 !important;
    }
    
    /* Headers - Gradient Text */
    h1, h2, h3 {
        background: linear-gradient(120deg, #00b09b, #96c93d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Buttons - Modern Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #00b09b 0%, #96c93d 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 176, 155, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 176, 155, 0.4);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 10px 15px;
        background-color: white;
        color: #333;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00b09b;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* Custom Card - Glassmorphism Light */
    .eco-card {
        padding: 30px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    .eco-card:hover {
        transform: translateY(-5px);
    }
    
    /* Game Card */
    .game-card {
        padding: 25px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-top: 5px solid #96c93d;
        text-align: center;
        transition: all 0.3s;
    }
    .game-card:hover {
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    }
    
    /* Progress Bar Custom */
    .progress-container {
        background-color: #e0e0e0;
        border-radius: 20px;
        padding: 3px;
        margin: 10px 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        height: 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-weight: bold;
        line-height: 25px;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 15px 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .user-message {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 2px;
    }
    
    .assistant-message {
        background-color: white;
        color: #333;
        margin-right: 20%;
        border-bottom-left-radius: 2px;
        border: 1px solid #e0e0e0;
    }
    
    /* KBC Style Quiz */
    .kbc-container {
        background: radial-gradient(circle, #000046 0%, #1cb5e0 100%);
        border: 4px solid #d4af37;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 30px;
        color: white;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.6);
    }
    .kbc-header {
        text-align: center;
        color: #d4af37;
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px #000;
    }
    .kbc-question-box {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #d4af37;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        font-size: 1.3em;
        margin-bottom: 20px;
        color: white;
    }
    .kbc-prize-tag {
        background-color: #d4af37;
        color: #000;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
        box-shadow: 0 0 10px #d4af37;
    }
    
    /* Logo Container */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .logo-img {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 100%);
        border-radius: 50%;
        padding: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border: 3px solid #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. SESSION STATE SETUP
# ==========================================
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "assistant", "content": "🌿 Hi! I'm EcoBot. I can generate quizzes, give tips, or help you save the planet!"}]

if 'quiz_data' not in st.session_state:
    st.session_state['quiz_data'] = []

# Game-specific session states
if 'carbon_footprint' not in st.session_state:
    st.session_state['carbon_footprint'] = 50
    
if 'eco_score' not in st.session_state:
    st.session_state['eco_score'] = 0

if 'show_chat' not in st.session_state:
    st.session_state['show_chat'] = False

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

VISION_FALLBACK_MODEL = "llama-3.3-70b-versatile"


def _extract_text_from_message_content(content):
    """Convert Groq multimodal content blocks to a plain string for text-only models."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and item.get("text"):
                    parts.append(str(item["text"]))
                elif item.get("text"):
                    parts.append(str(item["text"]))
        return "\n".join(parts)
    return str(content)


def _has_image_payload(messages):
    for message in messages or []:
        content = message.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "image_url":
                    return True
    return False


def normalize_ai_response(text):
    """Normalize noisy AI output into a clean string for reliable parsing."""
    if text is None:
        return ""
    text = str(text).strip()
    text = text.replace("```", "").replace("\r", "\n")
    text = " ".join(text.split())
    return text


def get_pipe_parts(text):
    """Return clean pipe-delimited parts from a response."""
    cleaned = normalize_ai_response(text)
    if not cleaned:
        return []
    return [p.strip() for p in cleaned.split('|') if p and p.strip()]


def debug_mission_response(resp, label="Mission"):
    """Return a cleaned response string to help parse partial or noisy AI output."""
    text = normalize_ai_response(resp)
    if not text:
        return ""
    return text.replace("VERIFIED:", "VERIFIED|").replace("REJECTED:", "REJECTED|").replace("VERIFIED_PASS:", "VERIFIED_PASS|").replace("VERIFIED_FAIL:", "VERIFIED_FAIL|")


def log_mission_debug(label, raw_response, parsed_value=None):
    """Store raw and parsed mission outputs in session state for debugging."""
    debug_logs = st.session_state.get("mission_debug_logs", [])
    debug_logs.append({
        "label": label,
        "raw_response": normalize_ai_response(raw_response),
        "parsed_value": parsed_value,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    st.session_state["mission_debug_logs"] = debug_logs[-20:]


def safe_groq_chat(messages, model, **kwargs):
    """Retry with a better-supported model for image content and show a friendly notice if the current model rejects the payload."""
    if not groq_client:
        raise RuntimeError("Groq client not initialized.")

    try:
        return groq_client.chat.completions.create(model=model, messages=messages, **kwargs)
    except Exception as e:
        error_text = str(e)
        is_content_format_error = "messages[0].content must be a string" in error_text or "content must be a string" in error_text
        is_model_missing_error = "model_not_found" in error_text.lower() or "does not exist" in error_text.lower() or "not found" in error_text.lower()

        if not is_content_format_error and not is_model_missing_error:
            raise

        if _has_image_payload(messages):
            fallback_notice = "AI model rejected image payload; retrying with a supported vision-capable model for this mission."
            try:
                if hasattr(st, 'info'):
                    st.info(fallback_notice)
            except Exception:
                pass
            if model != VISION_FALLBACK_MODEL:
                try:
                    return groq_client.chat.completions.create(model=VISION_FALLBACK_MODEL, messages=messages, **kwargs)
                except Exception as fallback_error:
                    fallback_error_text = str(fallback_error).lower()
                    if "model_not_found" in fallback_error_text or "does not exist" in fallback_error_text or "not found" in fallback_error_text:
                        pass
                    else:
                        raise

        fallback_messages = []
        for message in messages:
            fallback_messages.append({
                "role": message.get("role", "user"),
                "content": _extract_text_from_message_content(message.get("content", "")),
            })
        try:
            if hasattr(st, 'warning'):
                st.warning("AI model rejected image payload; using text-only fallback. Image missions may be less accurate on this model.")
        except Exception:
            pass

        return groq_client.chat.completions.create(model=model, messages=fallback_messages, **kwargs)


def get_groq_response(prompt, model=MODEL_NAME):
    """Get response from Groq API."""
    completion = safe_groq_chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.7,
        max_tokens=1024,
    )
    return completion.choices[0].message.content


def test_groq_connection(timeout=10):
    """Simple diagnostic call to verify Groq connectivity and API key validity.
    Returns (success: bool, message: str)"""
    api_key = st.secrets.get('GROQ_API_KEY') if hasattr(st, 'secrets') else None
    # Check against known placeholders
    if not api_key or api_key in (None, '', 'YOUR_API_KEY_HERE', 'gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE'):
        return False, 'Groq API key not configured. Put your key in .streamlit/secrets.toml.'

    try:
        test_prompt = "Say 'hello' in one short sentence."
        if not groq_client:
             return False, "Groq client failed to initialize."
             
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": test_prompt}],
            model=MODEL_NAME,
        )
        text = response.choices[0].message.content

        if text and text.strip():
            return True, text.strip()
        return False, 'Groq returned an empty response.'

    except Exception as e:
        return False, str(e)


def parse_groq_error(msg):
    """Return a short actionable suggestion based on common Groq error messages."""
    if not msg:
        return "No error message available. Try running 'Test Groq Connection' to get details."
    lm = msg.lower()
    if any(k in lm for k in ['api key not valid', 'api_key_invalid', 'invalid api key', 'invalid key', '401', '403', 'unauthorized']):
        return "Invalid or unauthorized API key. Check your key in `.streamlit/secrets.toml`."
    if 'missing key' in lm or 'missing api' in lm:
        return "API key missing — add `GROQ_API_KEY` to `.streamlit/secrets.toml`."
    if 'quota' in lm or 'rate' in lm or '429' in lm:
        return "Rate limit exceeded — wait a moment before trying again."
    return "No specific recommendation could be inferred. Copy the raw error (debug) and paste it here or share it with me for help."

def _load_local_question(difficulty=None):
    """Load a random question from local JSON bank and convert to AI-style output"""
    import json
    p = os.path.join('assets', 'questions_sustainability.json')
    try:
        with open(p, 'r', encoding='utf-8') as f:
            qbank = json.load(f)
        if not qbank:
            return None
            
        if difficulty:
            # Filter by difficulty if provided (case-insensitive)
            diff_lower = difficulty.lower()
            filtered = [q for q in qbank if q.get('difficulty', 'medium').lower() == diff_lower]
            sel = random.choice(filtered) if filtered else random.choice(qbank)
        else:
            sel = random.choice(qbank)
            
        letters = ['A', 'B', 'C', 'D']
        ans_letter = letters[sel['ans']] if 'ans' in sel and isinstance(sel['ans'], int) else 'A'
        return {
            'q': sel.get('q', 'No question'),
            'options': sel.get('options', []),
            'ans': ans_letter,
            'exp': sel.get('exp', ''),
            'difficulty': sel.get('difficulty', 'Medium')
        }
    except Exception as ex:
        # local fallback failed
        return None


def generate_ai_quiz_question(difficulty="Medium"):
    """Generates a dynamic quiz question using Groq."""
    api_key = st.secrets.get('GROQ_API_KEY') if hasattr(st, 'secrets') else None

    # If no API key configured, use local bank and set transient notice
    if not api_key or api_key in (None, '', 'YOUR_API_KEY_HERE', 'gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE'):
        q = _load_local_question(difficulty)
        if q:
            st.session_state['fallback_notice'] = 'Groq AI unavailable — using local question bank.'
            st.session_state['fallback_notice_time'] = time.time()
            return q
        else:
            st.error('AI generation unavailable and local question bank could not be loaded.')
            return None

    prompt = (
        f"Generate 1 {difficulty} difficulty multiple choice question about environmental sustainability, recycling, or climate change.\n"
        "Strictly follow this format using the pipe symbol (|) as a separator:\n"
        "Question Text | Option A | Option B | Option C | Option D | Correct Option (A/B/C/D) | Short Explanation"
    )

    try:
        text = get_groq_response(prompt, model=MODEL_NAME)

        if text:
            parts = text.split('|')
            if len(parts) >= 6:
                return {
                    "q": parts[0].strip(),
                    "options": [parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip()],
                    "ans": parts[5].strip().upper(),
                    "exp": parts[6].strip() if len(parts) > 6 else "Great job saving the planet!",
                    "difficulty": difficulty
                }

        # Unexpected or empty output - fall back to local and show brief notice
        local_q = _load_local_question(difficulty)
        if local_q:
            st.session_state['fallback_notice'] = 'AI returned unexpected format — using local question bank.'
            st.session_state['fallback_notice_time'] = time.time()
            return local_q
        return None

    except Exception as e:
        msg = str(e)
        # Common invalid-key detection
        if 'API key not valid' in msg or 'API_KEY_INVALID' in msg or 'Missing key' in msg or 'invalid' in msg.lower():
            st.session_state['fallback_notice'] = 'AI generation failed: invalid/missing Groq key — using local questions.'
            st.session_state['fallback_notice_time'] = time.time()
            local_q = _load_local_question(difficulty)
            if local_q:
                return local_q
        st.error(f'Error generating quiz: {msg}')
        local_q = _load_local_question(difficulty)
        if local_q:
            st.session_state['fallback_notice'] = 'AI generation error — using local question bank.'
            st.session_state['fallback_notice_time'] = time.time()
            return local_q
        return None

def log_action(action, points):
    """Log student action to database and persist eco score for logged-in user"""
    student_id = st.session_state.get('username', 'Student_User')
    st.session_state['eco_score'] += points

    # Persist to user database if logged in
    if st.session_state.get('username'):
        try:
            auth.update_user_score(st.session_state['username'], int(st.session_state['eco_score']))
            st.session_state['user_info'] = auth.get_user_info(st.session_state['username'])
            auth.log_activity(st.session_state['username'], action, points)
        except Exception as e:
            st.warning(f"Could not persist eco score: {e}")

def get_game_score(game_name):
    """Retrieve actual game score from session state"""
    return st.session_state.get(f'{game_name}_score', 0)

# ==========================================
# FOOD ANALYZER CONSTANTS & CLASSES
# ==========================================
# COMPOSTABLE FOODS DATABASE - ONLY THESE GET POINTS
COMPOSTABLE_FOOD_DB = {
    'banana': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 50, 'eco_points': 20, 'health_score': 9, 'carbon': 0.7},
    'mango': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 80, 'eco_points': 20, 'health_score': 10, 'carbon': 1.2},
    'apple': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 60, 'eco_points': 20, 'health_score': 9, 'carbon': 0.9},
    'orange': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 55, 'eco_points': 20, 'health_score': 9, 'carbon': 0.8},
    'strawberry': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 65, 'eco_points': 20, 'health_score': 9, 'carbon': 1.1},
    'tomato': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 30, 'eco_points': 20, 'health_score': 8, 'carbon': 1.4},
    'carrot': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 40, 'eco_points': 20, 'health_score': 9, 'carbon': 0.4},
    'broccoli': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 50, 'eco_points': 20, 'health_score': 9, 'carbon': 0.8},
    'spinach': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 35, 'eco_points': 20, 'health_score': 9, 'carbon': 0.3},
    'lettuce': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 25, 'eco_points': 20, 'health_score': 7, 'carbon': 0.2},
    'potato': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 20, 'eco_points': 20, 'health_score': 7, 'carbon': 0.5},
    'onion': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 15, 'eco_points': 20, 'health_score': 6, 'carbon': 0.3},
    'garlic': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 30, 'eco_points': 20, 'health_score': 8, 'carbon': 0.4},
    'lemon': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 20, 'eco_points': 20, 'health_score': 8, 'carbon': 0.5},
    'grapes': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 70, 'eco_points': 20, 'health_score': 9, 'carbon': 1.0},
    'watermelon': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 45, 'eco_points': 20, 'health_score': 7, 'carbon': 0.6},
    'peach': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 55, 'eco_points': 20, 'health_score': 8, 'carbon': 0.7},
    'rice': {'biodegradable': True, 'compostable': True, 'type': 'grain', 'profit': 30, 'eco_points': 20, 'health_score': 7, 'carbon': 0.4},
    'wheat': {'biodegradable': True, 'compostable': True, 'type': 'grain', 'profit': 25, 'eco_points': 20, 'health_score': 7, 'carbon': 0.3},
    'corn': {'biodegradable': True, 'compostable': True, 'type': 'grain', 'profit': 35, 'eco_points': 20, 'health_score': 7, 'carbon': 0.5},
    'fruit': {'biodegradable': True, 'compostable': True, 'type': 'fruit', 'profit': 40, 'eco_points': 20, 'health_score': 8, 'carbon': 0.5},
    'vegetable': {'biodegradable': True, 'compostable': True, 'type': 'vegetable', 'profit': 30, 'eco_points': 20, 'health_score': 8, 'carbon': 0.4},
}

# NON-COMPOSTABLE BUT FOOD ITEMS - THESE GET REJECTION
NON_COMPOSTABLE_FOOD = ['pizza', 'burger', 'hotdog', 'fries', 'chips', 'candy', 'chocolate', 'ice_cream', 'doughnut', 
                        'cake', 'cookie', 'bread', 'meat', 'chicken', 'fish', 'egg', 'dairy', 'milk', 'cheese',
                        'processed', 'cooked', 'oil', 'butter']

# NON-FOOD ITEMS - COMPLETE REJECTION
NON_FOOD_ITEMS = ['bottle', 'can', 'phone', 'laptop', 'person', 'car', 'dog', 'cat', 'bird', 'website', 'screen', 
                  'document', 'paper', 'wood', 'plastic', 'metal', 'cloth', 'furniture', 'building']

# OLD COMPATIBILITY - Maps to compostable DB
INDIAN_FOOD_DB = COMPOSTABLE_FOOD_DB
JUNK_FOOD_ITEMS = NON_COMPOSTABLE_FOOD

@st.cache_resource
def load_efficientnet():
    if not TF_AVAILABLE or EfficientNetB0 is None:
        return None
    try:
        return EfficientNetB0(weights='imagenet')
    except Exception:
        return None

class EcoFoodClassifier:
    def __init__(self):
        self.model = load_efficientnet()
        
    def preprocess_image(self, image_path):
        if not TF_AVAILABLE or tf is None or preprocess_input is None:
            return None
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return preprocess_input(img_array)
    
    def detect_ai_generated(self, image_path):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return (True, laplacian_var) if laplacian_var < 50 else (False, laplacian_var)
    
    def classify_food(self, image_path):
        """
        Classify food and verify if it's compostable.
        Only compostable foods get eco points.
        """
        if self.model is None:
            return {'is_real': True, 'is_food': True, 'is_compostable': True, 'ai_score': 100,
                    'message': 'Local classifier offline. Image accepted.'}

        is_ai, ai_score = self.detect_ai_generated(image_path)
        
        if is_ai and ai_score < 30:
            return {'is_real': False, 'is_food': False, 'is_compostable': False, 'ai_score': ai_score,
                    'message': '🤖 AI-generated image! (Not real)'}
        
        img_array = self.preprocess_image(image_path)
        predictions = self.model.predict(img_array, verbose=0)
        decoded = decode_predictions(predictions, top=20)[0]
        
        # Mapping ImageNet classes to Compostable DB keys
        imagenet_map = {
            'granny_smith': 'apple',
            'delicious': 'apple',
            'banana': 'banana',
            'strawberry': 'strawberry',
            'orange': 'orange',
            'lemon': 'lemon',
            'fig': 'fruit',
            'pineapple': 'fruit',
            'pomegranate': 'fruit',
            'corn': 'corn',
            'ear': 'corn',
            'broccoli': 'broccoli',
            'cauliflower': 'vegetable',
            'head_cabbage': 'lettuce',
            'zucchini': 'vegetable',
            'spaghetti_squash': 'vegetable',
            'acorn_squash': 'vegetable',
            'cucumber': 'vegetable',
            'bell_pepper': 'vegetable',
            'mushroom': 'vegetable',
            # Expanded mappings for better detection (e.g. Grapes)
            'buckeye': 'grapes',   # Common ImageNet confusion for grapes
            'hip': 'grapes',       # Rose hip often looks like grapes
            'custard_apple': 'grapes',
            'jackfruit': 'fruit',
            'bead': 'grapes',      # Grapes look like beads
            'bubble': 'grapes',    # Grapes look like bubbles
            'ping-pong_ball': 'grapes', # Green grapes look like ping-pong balls
            'tennis_ball': 'grapes', # Green grapes often misclassified as tennis balls
            'necklace': 'grapes',    # Clusters often look like necklaces
            'abacus': 'grapes'       # Beads on abacus
        }
        
        # 🍇 GRAPE CORRECTION LOGIC
        # EfficientNet often confuses Green Grapes with Granny Smith Apples.
        # If we see Apple but also see "grape-like" classes (bead, bubble, buckeye) in the top 20,
        # we prioritize Grapes.
        grape_indicators = ['buckeye', 'hip', 'bead', 'bubble', 'ping-pong_ball', 'custard_apple', 
                            'tennis_ball', 'necklace', 'abacus']
        found_grape_indicator = False
        
        # Check if any grape indicator is in the top 20 predictions
        for pred in decoded:
            if pred[1].lower() in grape_indicators:
                found_grape_indicator = True
                break

        for pred in decoded:
            raw_name = pred[1].lower()
            # Resolve name using map if exists, else use raw name
            item_name = imagenet_map.get(raw_name, raw_name)
            confidence = pred[2] * 100
            
            # CORRECTION: If Apple is detected but we found grape indicators, switch to Grapes
            if (item_name == 'apple' or item_name == 'lemon') and found_grape_indicator:
                item_name = 'grapes'
            
            # ❌ CHECK FOR NON-FOOD ITEMS FIRST
            for non_food in NON_FOOD_ITEMS:
                if non_food in item_name:
                    return {'is_real': True, 'is_food': False, 'is_compostable': False, 'detected_item': item_name,
                            'confidence': confidence, 'message': f'🚫 Not a food item: {item_name.title()} detected!'}
            
            # ⚠️ CHECK FOR NON-COMPOSTABLE FOODS (processed, meat, etc.)
            for non_comp in NON_COMPOSTABLE_FOOD:
                if non_comp in item_name:
                    return {'is_real': True, 'is_food': True, 'is_compostable': False, 'food_name': item_name.title(),
                            'confidence': confidence, 'category': '🍔 Non-Compostable Food', 'is_eco': False,
                            'eco_points': 0, 'carbon_footprint': 5.0, 'biodegradable': False,
                            'message': f'⚠️ {item_name.title()} is NOT compostable! (Processed/cooked foods & animal products cannot be composted)', 
                            'all_predictions': [{'name': p[1], 'confidence': p[2]*100} for p in decoded]}
            
            # ✅ CHECK FOR COMPOSTABLE FOODS (fruits, vegetables, raw foods)
            # Enforce confidence threshold (20%) to avoid wrong results (e.g. Grapes -> Lemon)
            if confidence < 20:
                continue

            for food_key, food_info in COMPOSTABLE_FOOD_DB.items():
                if food_key in item_name or item_name in food_key:
                    food_type = food_info.get('type', 'food')
                    type_icon = {'fruit': '🍎', 'vegetable': '🥕', 'grain': '🌾'}.get(food_type, '🍽️')
                    
                    return {'is_real': True, 'is_food': True, 'is_compostable': True, 'food_name': food_key.title(),
                            'confidence': confidence, 
                            'category': f"{type_icon} {'Fruit' if food_type=='fruit' else 'Vegetable' if food_type=='vegetable' else 'Grain'}",
                            'is_eco': True, 'eco_points': food_info['eco_points'],
                            'health_score': food_info['health_score'], 'profit': food_info['profit'],
                            'carbon_footprint': food_info['carbon'], 'biodegradable': food_info['biodegradable'],
                            'message': f'✅ Perfect! {food_key.title()} is compostable! +{food_info["eco_points"]} eco points!',
                            'all_predictions': [{'name': p[1], 'confidence': p[2]*100} for p in decoded]}
        
        # DEFAULT: Unknown food - DO NOT AWARD POINTS
        top = decoded[0]
        return {'is_real': True, 'is_food': True, 'is_compostable': False, 'food_name': top[1].title(),
                'confidence': top[2]*100, 'category': '❓ Unknown Food', 'is_eco': False,
                'eco_points': 0, 'carbon_footprint': 2.0, 'biodegradable': True,
                'message': f'❓ "{top[1].title()}" detected, but NOT in our compostable database! Only raw fruits, vegetables & grains are compostable.',
                'all_predictions': [{'name': p[1], 'confidence': p[2]*100} for p in decoded]}

# ==========================================
# 3. AI CHAT INTERFACE
# ==========================================

def chat_interface():
    """Renders the widgets for the chat interface inside a container."""
    def close_chat():
        st.session_state.show_chat = False

    # Header with a button-based close action
    header_cols = st.columns([0.9, 0.1])
    with header_cols[0]:
        st.markdown('<h3 style="color: #2c3e50; margin-bottom: 0;">🤖 EcoBot Mentor</h3>', unsafe_allow_html=True)
    with header_cols[1]:
        st.button("X", on_click=close_chat, key="close_chat_button")

    st.divider()

    # Chat messages display area
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🌿 {msg["content"]}</div>', unsafe_allow_html=True)

    # Chat input at the bottom
    if prompt := st.chat_input("How can I recycle glass?"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("EcoBot is thinking... 🌱"):
            try:
                ai_prompt = f"You are EcoBot, a fun sustainability expert for students. Keep it short (2-3 sentences) and encouraging. Answer: {prompt}"
                reply = get_groq_response(ai_prompt)
            except Exception as e:
                st.session_state['last_groq_error'] = str(e)
                st.session_state['last_prompt'] = prompt
                st.session_state['last_error_time'] = time.time()
                reply = "I'm having trouble connecting to the nature network. Try the 'Test Groq Connection' in the diagnostics or check your API key. 🌍"
        
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # --- Groq Diagnostics (moved to an expander at the bottom) ---
    with st.expander("🔧 Connection Diagnostics"):
        api_key = st.secrets.get('GROQ_API_KEY') if hasattr(st, 'secrets') else None
        key_ok = bool(api_key and api_key not in (None, '', 'YOUR_API_KEY_HERE', 'gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE'))
        st.write(f"**API key configured:** {'Yes' if key_ok else 'No'}")
        if st.button("Test Groq Connection", key="test_groq_inside_chat"):
            with st.spinner("Testing..."):
                ok, msg = test_groq_connection()
                if ok:
                    st.success(f"Connection OK: {msg}")
                else:
                    st.error(f"Connection failed: {msg}")
    
# ==========================================
# 4. AI QUIZ GAME
# ==========================================

def quiz_interface():
    st.markdown('<div class="eco-card"><h3>🧠 Quiz Game</h3><p>Play the Sustainability Quiz in KBC Style! Win Plant Points (🌱) and earn a Tree Plantation Reward!</p></div>', unsafe_allow_html=True)
    
    # Fallback notices from AI generation are now suppressed to avoid showing technical messages in the UI.
    # If you want to inspect fallback events for debugging, enable logging to console or a debug panel.
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Generate multiple questions (default 4) and display them all
        if not st.session_state['quiz_data']:
            if st.button("🌱 Start KBC Challenge (Mixed Levels)", key="gen_quiz"):
                with st.spinner("Setting up the Hot Seat..."):
                    qs = []
                    # Generate 4 questions with increasing difficulty
                    # 1 Easy, 2 Medium, 1 Hard
                    levels = [
                        ("Easy", "🌱 5,000"), 
                        ("Medium", "🌱 20,000"), 
                        ("Medium", "🌱 50,000"), 
                        ("Hard", "🌱 1,00,000")
                    ]
                    
                    for diff, prize in levels:
                        q_data = generate_ai_quiz_question(difficulty=diff)
                        if q_data:
                            q_data['prize'] = prize
                            qs.append(q_data)
                            
                    if qs:
                        st.session_state['quiz_data'] = qs
                        st.rerun()
                    else:
                        st.error("AI couldn't generate questions. Try again.")
        
        if st.session_state['quiz_data']:
            questions = st.session_state['quiz_data']
            # Display all generated questions with independent answer controls
            for idx, q in enumerate(list(questions)):
                # KBC Style Display
                st.markdown(f"""
                <div class="kbc-container">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="kbc-prize-tag">{q.get('prize', 'Bonus')}</span>
                        <span style="color: #d4af37; font-weight: bold;">Level: {q.get('difficulty', 'General')}</span>
                    </div>
                    <div class="kbc-header">Question {idx+1}</div>
                    <div class="kbc-question-box">{q['q']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                opts = q['options']
                choice = st.radio(f"Select your answer for Question {idx+1}:", opts, key=f"quiz_choice_{idx}", index=None)
                
                if st.button(f"🔒 Lock Answer {idx+1}", key=f"submit_quiz_{idx}"):
                    if choice:
                        choice_index = opts.index(choice)
                        choice_letter = ["A", "B", "C", "D"][choice_index]
                        if choice_letter == q['ans']:
                            st.balloons()
                            
                            # Check for tree reward (50,000+ points)
                            prize_text = q.get('prize', '0')
                            reward_msg = ""
                            try:
                                # Remove non-numeric characters to parse value
                                points_val = int(''.join(filter(str.isdigit, prize_text)))
                                if points_val >= 50000:
                                    reward_msg = "\n\n🌳 **CONGRATULATIONS! You've collected 50,000+ Plant Points! A real tree will be planted in your honor!** 🌳"
                            except:
                                pass
                                
                            st.success(f"✅ Correct! +5 Eco Points! You won {prize_text}! {reward_msg}\n\n{q['exp']}")
                            log_action(f"KBC Win ({q.get('difficulty')})", 5)  # Award 5 eco points for correct answer
                            # We don't auto-remove to let user see the result, 
                            # but you could add logic to disable the button
                        else:
                            st.error(f"❌ Wrong Answer! -2.5 Eco Points. The correct option was {q['ans']}.")
                            st.warning(q['exp'])
                            log_action(f"KBC Wrong ({q.get('difficulty')})", -2.5)  # Deduct 2.5 eco points for wrong answer
                    else:
                        st.warning("⚠️ Please select an option before locking it!")
                
                st.markdown("---")
            
            if st.button("🔄 Generate New Set", key="reset_quiz"):
                st.session_state['quiz_data'] = []
                st.rerun()

    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/4148/4148323.png", width=150)
        st.metric("🌱 Eco-Score", st.session_state['eco_score'])

# ==========================================
# 5. MISSION TRACKER
# ==========================================

def mission_tracker():
    st.markdown('<div class="eco-card"><h3>📝 Daily Green Missions</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        action = st.selectbox("Select Mission Completed:", 
                              ["Recycled Plastic", "Planted a Tree", "Walking to School", 
                               "Saved Electricity", "Composted Food"],
                              key="mission_select")
    
    with col2:
        points_map = {
            "Recycled Plastic": 15, 
            "Planted a Tree": 25, 
            "Walking to School": 10, 
            "Saved Electricity": 15, 
            "Composted Food": 20
        }
        st.metric(label="Points Value", value=points_map[action])
    
    if action == "Planted a Tree":
        st.info("📸 **Verification Required:** Please upload a real photo of you planting the tree. AI-generated or fake images will be rejected.")
        uploaded_file = st.file_uploader("Upload Evidence", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            if st.button("🔍 Verify & Log Mission", key="verify_mission"):
                with st.spinner("🤖 Verifying image authenticity..."):
                    try:
                        if not groq_client:
                            st.error("Groq API Key not configured or client initialization failed.")
                        else:
                            # Resize image to max 1024x1024 to ensure API compatibility and speed
                            image = Image.open(uploaded_file)
                            image.thumbnail((1024, 1024))
                            
                            # Convert back to bytes for base64 encoding
                            img_byte_arr = io.BytesIO()
                            # Default to JPEG if format is not detected
                            fmt = image.format if image.format else 'JPEG'
                            image.save(img_byte_arr, format=fmt)
                            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                            mime_type = uploaded_file.type
                            
                            prompt = (
                                "Analyze this image for a mission verification. "
                                "Is this a REAL photo of a person planting a tree? "
                                "Strictly reject AI-generated images, screenshots, digital art, or stock photos. "
                                "Look for natural lighting, realistic textures, and imperfections typical of a phone camera. "
                                "It must show a person engaged in the act of planting. "
                                "Return EXACTLY one of these formats: 'VERIFIED' or 'REJECTED|reason'. "
                                "Do not add markdown, commentary, or extra explanation."
                            )
                            
                            completion = None
                            # Retry logic for 503 Service Unavailable / Over Capacity
                            for attempt in range(3):
                                try:
                                    completion = safe_groq_chat(
                                        messages=[
                                            {
                                                "role": "user",
                                                "content": [
                                                    {"type": "text", "text": prompt},
                                                    {
                                                        "type": "image_url",
                                                        "image_url": {
                                                            "url": f"data:{mime_type};base64,{base64_image}",
                                                        },
                                                    },
                                                ],
                                            }
                                        ],
                                        model=MODEL_NAME,
                                        temperature=0.1,
                                        max_tokens=1024,
                                    )
                                    break
                                except Exception as e:
                                    if ("503" in str(e) or "over capacity" in str(e).lower()) and attempt < 2:
                                        time.sleep(2 ** (attempt + 1))
                                        continue
                                    raise e
                            
                            raw_response = completion.choices[0].message.content
                            response_text = debug_mission_response(raw_response, "Tree")
                            log_mission_debug("Planted a Tree", raw_response, response_text)
                            
                            if "VERIFIED" in response_text.upper():
                                log_action("Planted a Tree (Verified)", 25)
                                st.success("✅ Verified! +25 Eco-Points added.")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                reason = get_pipe_parts(response_text)
                                reason_text = reason[1] if len(reason) > 1 else (response_text.replace("REJECTED", "").strip() or "The image does not match the mission requirement.")
                                st.error(f"❌ Verification Failed: {reason_text}")
                    except Exception as e:
                        st.error(f"Verification Error: {str(e)}")
    
    elif action == "Walking to School":
        st.info("🎥 **Verification Required:** Upload a SHORT VIDEO (15-60 seconds) of you walking to school. We'll verify it's real using AI!")
        st.markdown("📹 **Video Requirements:**\n- Show yourself walking\n- Include recognizable landmarks or surroundings\n- Clear, natural lighting\n- MP4, WebM, or MOV format (max 100MB)")
        
        video_file = st.file_uploader("Upload Walking Video", type=['mp4', 'webm', 'mov', 'avi'], key="walked_video")
        
        if video_file is not None:
            st.video(video_file)
            if st.button("🔍 Verify Video & Log Mission", key="verify_walked"):
                with st.spinner("🤖 Analyzing video for walking activity..."):
                    try:
                        if not groq_client:
                            st.error("Groq API Key not configured or client initialization failed.")
                        else:
                            
                            # Save uploaded video to temp file
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                                tmp_file.write(video_file.getbuffer())
                                tmp_path = tmp_file.name
                            
                            try:
                                # Open video and extract key frames
                                cap = cv2.VideoCapture(tmp_path)
                                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                                fps = cap.get(cv2.CAP_PROP_FPS)
                                duration = total_frames / fps if fps > 0 else 0
                                
                                # Check video duration (should be 15-60 seconds)
                                if duration < 10 or duration > 120:
                                    st.error(f"❌ Video duration is {duration:.1f} seconds. Please upload a video between 15-60 seconds.")
                                    cap.release()
                                else:
                                    # Extract 3 key frames from different parts of video
                                    frames_to_extract = [
                                        int(total_frames * 0.25),
                                        int(total_frames * 0.5),
                                        int(total_frames * 0.75)
                                    ]
                                    
                                    extracted_frames = []
                                    frame_analysis = []
                                    
                                    for frame_idx in frames_to_extract:
                                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                                        ret, frame = cap.read()
                                        
                                        if ret:
                                            # Resize frame for API compatibility
                                            frame = cv2.resize(frame, (512, 512))
                                            extracted_frames.append(frame)
                                            
                                            # Convert frame to base64
                                            _, buffer = cv2.imencode('.jpg', frame)
                                            base64_frame = base64.b64encode(buffer).decode('utf-8')
                                            frame_analysis.append(base64_frame)
                                    
                                    cap.release()
                                    
                                    if not frame_analysis:
                                        st.error("Could not extract frames from video. Try a different video format.")
                                    else:
                                        # Analyze frames with Groq
                                        prompt = (
                                            "Analyze these video frames for a 'Walking to School' mission verification. "
                                            "Requirements:\n"
                                            "1. AUTHENTICITY: Are these REAL video frames or AI-generated/fake? "
                                            "   Look for natural motion blur, realistic lighting, and video artifacts.\n"
                                            "2. ACTIVITY DETECTION: Does the person appear to be WALKING? "
                                            "   Look for body posture and leg movement while walking.\n"
                                            "3. ENVIRONMENT: Is this outdoors? Look for sky, trees, buildings, roads, or vehicles.\n"
                                            "4. MOTION CONSISTENCY: Do frames show progression of movement (not static)?\n"
                                            "\n"
                                            "Return EXACTLY ONE LINE in this format:\n"
                                            "VERIFIED|Description|Activity_Type|Energy_Estimate\n"
                                            "or\n"
                                            "REJECTED|reason\n"
                                            "No markdown, no extra explanation, no bullet list."
                                        )
                                        
                                        # Build message with multiple image frames
                                        content = [{"type": "text", "text": prompt}]
                                        for base64_frame in frame_analysis:
                                            content.append({
                                                "type": "image_url",
                                                "image_url": {"url": f"data:image/jpeg;base64,{base64_frame}"}
                                            })
                                        
                                        completion = None
                                        for attempt in range(3):
                                            try:
                                                completion = safe_groq_chat(
                                                    messages=[{"role": "user", "content": content}],
                                                    model=MODEL_NAME,
                                                    temperature=0.1,
                                                    max_tokens=500,
                                                )
                                                break
                                            except Exception as e:
                                                if ("503" in str(e) or "over capacity" in str(e).lower()) and attempt < 2:
                                                    time.sleep(2 ** (attempt + 1))
                                                    continue
                                                raise e
                                        
                                        raw_response = completion.choices[0].message.content
                                        resp = debug_mission_response(raw_response, "Walk")
                                        log_mission_debug("Walked to School", raw_response, resp)
                                        
                                        if "VERIFIED" in resp.upper():
                                            parts = get_pipe_parts(resp)
                                            description = parts[1] if len(parts) > 1 else "Walking activity confirmed."
                                            activity = parts[2] if len(parts) > 2 else "Walking"
                                            energy = parts[3] if len(parts) > 3 else "Energy saved"
                                            
                                            log_action("Walked to School (Verified)", 10)
                                            st.success("✅ Verified! +10 Eco-Points added.")
                                            st.info(f"🚶 **Analysis:** {description}\n\n**Activity:** {activity}\n\n⚡ **Impact:** {energy}")
                                            st.balloons()
                                            time.sleep(3)
                                            st.rerun()
                                        else:
                                            parts = get_pipe_parts(resp)
                                            reason = parts[1] if len(parts) > 1 else (resp.replace("REJECTED", "").strip() or "The video does not clearly show a real walking mission.")
                                            st.error(f"❌ Verification Failed: {reason}")
                                            st.warning("💡 **Tips:**\n- Ensure clear outdoor visibility\n- Film yourself actively walking or biking\n- Use natural lighting\n- Keep video 15-60 seconds")
                            
                            finally:
                                # Clean up temp file
                                try:
                                    os.remove(tmp_path)
                                except:
                                    pass
                                    
                    except ImportError:
                        st.error("⚠️ OpenCV not installed. Please run: pip install opencv-python")
                    except Exception as e:
                        st.error(f"Verification Error: {str(e)}")
    
    elif action == "Recycled Plastic":
        st.info("📸 **Verification Required:** Capture or upload a photo of the plastic item. We'll verify it's real and recyclable!")
        
        method = st.radio("Input Method", ["📸 Camera", "📂 Upload"], horizontal=True, index=1)
        img_file = None
        
        if method == "📸 Camera":
            img_file = st.camera_input("Take a photo of the plastic item")
        else:
            img_file = st.file_uploader("Upload image", type=['jpg', 'jpeg', 'png'])
            
        if img_file:
            st.image(img_file, caption="Item to Verify", width=300)
            if st.button("🔍 Verify & Recycle", key="verify_plastic"):
                with st.spinner("🤖 Analyzing image authenticity and plastic type..."):
                    try:
                        if not groq_client:
                            st.error("Groq API Key not configured.")
                        else:
                            # Prepare image
                            image = Image.open(img_file)
                            image.thumbnail((1024, 1024))
                            img_byte_arr = io.BytesIO()
                            fmt = image.format if image.format else 'JPEG'
                            image.save(img_byte_arr, format=fmt)
                            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                            
                            prompt = (
                                "Analyze this image for a plastic recycling mission. "
                                "1. AUTHENTICITY: Is this a REAL photo captured by a camera? Reject AI-generated images, digital art, or screens. "
                                "2. MATERIAL: Is the main object made of PLASTIC? "
                                "3. RECYCLABILITY: Is it a recyclable plastic item? "
                                "Return EXACTLY one line: 'VERIFIED|Object Name|Quick Recycling Tip' or 'REJECTED|reason'. "
                                "No markdown, no extra sentence, no bullet list."
                            )
                            
                            completion = None
                            # Retry logic for 503 Service Unavailable / Over Capacity
                            for attempt in range(3):
                                try:
                                    completion = safe_groq_chat(
                                        messages=[
                                            {
                                                "role": "user",
                                                "content": [
                                                    {"type": "text", "text": prompt},
                                                    {
                                                        "type": "image_url",
                                                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                                    },
                                                ],
                                            }
                                        ],
                                        model=MODEL_NAME,
                                        temperature=0.1,
                                        max_tokens=300,
                                    )
                                    break
                                except Exception as e:
                                    if ("503" in str(e) or "over capacity" in str(e).lower()) and attempt < 2:
                                        time.sleep(2 ** (attempt + 1))
                                        continue
                                    raise e
                            
                            raw_response = completion.choices[0].message.content
                            resp = debug_mission_response(raw_response, "Plastic")
                            log_mission_debug("Recycled Plastic", raw_response, resp)
                            
                            if "VERIFIED" in resp.upper():
                                parts = get_pipe_parts(resp)
                                if len(parts) >= 3:
                                    details = f"**Object:** {parts[1].strip()}\n\n**Tip:** {parts[2].strip()}"
                                else:
                                    details = resp.replace("VERIFIED", "").replace("|", " ").strip() or "Plastic item verified successfully."
                                
                                log_action("Recycled Plastic (Verified)", 15)
                                st.success("✅ Verified! +15 Eco-Points added.")
                                st.info(f"♻️ **Analysis:**\n{details}")
                                st.balloons()
                                time.sleep(4)
                                st.rerun()
                            else:
                                parts = get_pipe_parts(resp)
                                reason = parts[1] if len(parts) > 1 else (resp.replace("REJECTED", "").strip() or "The object does not clearly match a recyclable plastic item.")
                                st.error(f"❌ Verification Failed: {reason}")
                                
                    except Exception as e:
                        st.error(f"Verification Error: {str(e)}")

    elif action == "Saved Electricity":
        st.info("📸 **Verification Required:** Capture the electric board/switch to verify energy saving.")
        st.markdown("💡 **Tip:** Switch OFF the key/socket when charger is plugged in but not in use!")

        method = st.radio("Input Method", ["📸 Camera", "📂 Upload"], horizontal=True, key="elec_method", index=1)
        img_file = None
        
        if method == "📸 Camera":
            img_file = st.camera_input("Capture electric board/switch")
        else:
            img_file = st.file_uploader("Upload image", type=['jpg', 'jpeg', 'png'], key="elec_upload")
            
        if img_file:
            st.image(img_file, caption="Evidence", width=300)
            if st.button("🔍 Verify & Save Energy", key="verify_elec"):
                with st.spinner("⚡ Analyzing energy usage and authenticity..."):
                    try:
                        if not groq_client:
                            st.error("Groq API Key not configured.")
                        else:
                            # Prepare image
                            image = Image.open(img_file)
                            image.thumbnail((1024, 1024))
                            img_byte_arr = io.BytesIO()
                            fmt = image.format if image.format else 'JPEG'
                            image.save(img_byte_arr, format=fmt)
                            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                            
                            prompt = (
                                "Analyze this image for a 'Saved Electricity' mission. "
                                "1. AUTHENTICITY: Is this a REAL photo? Reject AI-generated, digital art, or screens. "
                                "2. LIGHTING: Is the environment dark or light? Suggest turning off lights if bright, or on if too dark. "
                                "3. SWITCH/CHARGER STATUS: Look at the electric socket/switch. "
                                "   - Is the switch ON or OFF? "
                                "   - Is a charger plugged in? Is a mobile connected? "
                                "4. SCENARIO EVALUATION: "
                                "   - If Switch is ON + Charger plugged + NO Mobile = WASTEFUL (Phantom Load). "
                                "   - If Switch is ON + No device = WASTEFUL. "
                                "   - If Switch is OFF = GOOD (Saved Electricity). "
                                "   - If Switch is ON + Device Charging = NEUTRAL (Usage). "
                                "5. ENERGY: Estimate power consumption/waste in Watts. "
                                "Return EXACTLY one line: 'VERIFIED_PASS|Message|Energy_Estimate' OR 'VERIFIED_FAIL|Message|Energy_Estimate' OR 'REJECTED|reason'. "
                                "No markdown, no explanation outside the format."
                            )
                            
                            completion = None
                            for attempt in range(3):
                                try:
                                    completion = safe_groq_chat(
                                        messages=[
                                            {
                                                "role": "user",
                                                "content": [
                                                    {"type": "text", "text": prompt},
                                                    {
                                                        "type": "image_url",
                                                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                                    },
                                                ],
                                            }
                                        ],
                                        model=MODEL_NAME,
                                        temperature=0.1,
                                        max_tokens=300,
                                    )
                                    break
                                except Exception as e:
                                    if ("503" in str(e) or "over capacity" in str(e).lower()) and attempt < 2:
                                        time.sleep(2 ** (attempt + 1))
                                        continue
                                    raise e
                            
                            raw_response = completion.choices[0].message.content
                            resp = debug_mission_response(raw_response, "Electricity")
                            log_mission_debug("Saved Electricity", raw_response, resp)
                            
                            if "VERIFIED_PASS" in resp.upper():
                                parts = get_pipe_parts(resp)
                                msg = parts[1] if len(parts) > 1 else "Good job!"
                                energy = parts[2] if len(parts) > 2 else "Saved energy"
                                
                                log_action("Saved Electricity (Verified)", 15)
                                st.success("✅ Verified! +15 Eco-Points added.")
                                st.info(f"💡 **Analysis:** {msg}")
                                st.metric("⚡ Energy Impact", energy)
                                st.balloons()
                                time.sleep(4)
                                st.rerun()
                            elif "VERIFIED_FAIL" in resp.upper():
                                parts = get_pipe_parts(resp)
                                msg = parts[1] if len(parts) > 1 else "Please switch off."
                                energy = parts[2] if len(parts) > 2 else "Wasted energy"
                                
                                st.warning(f"⚠️ **Action Needed:** {msg}")
                                st.error("❌ No points awarded. Switch off the key/switch when not in use!")
                                st.metric("⚡ Energy Consumption", energy)
                            else:
                                parts = get_pipe_parts(resp)
                                reason = parts[1] if len(parts) > 1 else (resp.replace("REJECTED", "").strip() or "The image does not clearly show the electricity-saving condition.")
                                st.error(f"❌ Verification Failed: {reason}")
                                
                    except Exception as e:
                        st.error(f"Verification Error: {str(e)}")

    elif action == "Composted Food":
        st.markdown("### 🌱 Eco Food Analyzer - Compost Checker")
        st.info("📸 **AI Verification:** Upload a photo of ONLY raw food (fruits, vegetables, grains) to verify it's compostable and earn eco points!")
        st.warning("⚠️ **Note:** Only raw, uncooked fruits, vegetables & grains are compostable. Cooked/processed foods & animal products are NOT compostable!")
        
        tab1, tab2 = st.tabs(["📤 Upload", "📷 Camera"])
        img_input = None
        
        with tab1:
            uploaded = st.file_uploader("Choose image", type=['jpg', 'jpeg', 'png'], key="food_upload")
            if uploaded:
                img_input = uploaded
        with tab2:
            camera = st.camera_input("Take photo", key="food_camera")
            if camera:
                img_input = camera
                
        if img_input:
            st.image(img_input, caption="Food to Analyze", width=300)
            if st.button("🔍 Check if Compostable", key="analyze_food"):
                with st.spinner("🔬 Analyzing with AI... Checking if food is compostable..."):
                    # Use Groq Vision if available for better accuracy (supports Grapes etc.)
                    if groq_client:
                        try:
                            # Prepare image
                            image = Image.open(img_input)
                            image.thumbnail((1024, 1024))
                            img_byte_arr = io.BytesIO()
                            fmt = image.format if image.format else 'JPEG'
                            image.save(img_byte_arr, format=fmt)
                            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                            
                            prompt = (
                                "Analyze this image for composting verification. "
                                "Identify the main food item. "
                                "Is it a RAW fruit, vegetable, or grain suitable for composting? "
                                "Reject cooked food, meat, dairy, processed food, or non-food items. "
                                "Return EXACTLY one line: 'VERIFIED|FoodName|Category|20|CarbonFootprint(kg)' or 'REJECTED|reason'. "
                                "No markdown, no extra text."
                            )
                            
                            completion = safe_groq_chat(
                                messages=[
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": prompt},
                                            {
                                                "type": "image_url",
                                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                            },
                                        ],
                                    }
                                ],
                                model=MODEL_NAME,
                                temperature=0.1,
                                max_tokens=300,
                            )
                            
                            raw_response = completion.choices[0].message.content
                            resp = debug_mission_response(raw_response, "Food")
                            log_mission_debug("Composted Food", raw_response, resp)
                            
                            if "VERIFIED" in resp.upper():
                                parts = get_pipe_parts(resp)
                                food_name = parts[1] if len(parts) > 1 else "Food"
                                category = parts[2] if len(parts) > 2 else "Compostable"
                                points = 20
                                carbon = parts[4] if len(parts) > 4 else "0.5"
                                
                                st.success(f"✅ Verified! {food_name} is compostable!")
                                
                                col_res1, col_res2 = st.columns(2)
                                col_res1.metric("🍽️ Food", food_name)
                                col_res2.metric("🌟 Eco Points", f"+{points} 🎉")
                                
                                st.markdown(f"**Category:** {category}")
                                st.markdown(f"**Carbon Footprint:** {carbon} kg CO₂")
                                
                                # Insights
                                prompt_insights = f"Give 2 short fun facts about composting {food_name}."
                                insights = get_groq_response(prompt_insights, model=MODEL_NAME)
                                st.markdown(f'<div class="eco-card" style="background: #e3f2fd; border-left: 5px solid #4caf50;"><strong>🎙️ Eco Insights:</strong><br>{insights}</div>', unsafe_allow_html=True)
                                
                                log_action(f"Composted Food ({food_name})", points)
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                parts = get_pipe_parts(resp)
                                reason = parts[1] if len(parts) > 1 else (resp.replace("REJECTED", "").strip() or "The food item is not a raw compostable item.")
                                st.error(f"❌ Verification Failed: {reason}")
                                
                        except Exception as e:
                            st.error(f"AI Error: {str(e)}")
                            
                    else:
                        # Fallback to local classifier if Groq not available
                        # Save to temp file for CV2 reading
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                            tmp.write(img_input.getvalue())
                            tmp_path = tmp.name
                        
                        try:
                            # Initialize classifier
                            classifier = EcoFoodClassifier()
                            result = classifier.classify_food(tmp_path)
                            
                            # ❌ NOT A REAL IMAGE
                            if not result.get('is_real', True):
                                st.error("🤖 " + result.get('message'))
                            # ❌ NOT FOOD AT ALL
                            elif not result.get('is_food', True):
                                st.error("🚫 " + result.get('message'))
                                st.info("Please upload an image of actual food items!")
                            # ❌ FOOD BUT NOT COMPOSTABLE
                            elif not result.get('is_compostable', False):
                                st.warning("⚠️ " + result.get('message'))
                                st.metric("🌟 Eco Points", "0 (Not awarded)")
                                st.info("💡 **Tip:** Only raw, uncooked fruits, vegetables, and grains can be composted. Avoid cooked meals, meat, dairy, and processed foods!")
                            # ✅ COMPOSTABLE FOOD - AWARD POINTS
                            else:
                                st.success("✅ " + result.get('message'))
                                
                                # Fixed points for Composted Food mission = 20 points (consistent with points_map)
                                composted_points = 20
                                
                                col_res1, col_res2 = st.columns(2)
                                col_res1.metric("🍽️ Food", result['food_name'])
                                col_res2.metric("🌟 Eco Points", f"+{composted_points} 🎉")
                                
                                st.markdown(f"**Category:** {result['category']}")
                                st.markdown(f"**Confidence:** {result['confidence']:.1f}%")
                                st.markdown(f"**Carbon Footprint:** {result['carbon_footprint']} kg CO₂")
                                
                                log_action(f"Composted Food ({result['food_name']})", composted_points)
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            
                        finally:
                            os.unlink(tmp_path)

    else:
        if st.button("✅ Log Mission", key="log_mission"):
            log_action(action, points_map[action])
            st.success(f"Mission '{action}' logged! +{points_map[action]} points")
            time.sleep(1)
            st.rerun()
    
    # Mission History
    st.markdown("### 📋 Mission History")
    try:
        user_activities = auth.get_all_activities()
        my_activities = user_activities[user_activities['username'] == st.session_state.get('username')]
        if my_activities.empty:
            st.info("You haven't logged any missions yet.")
        else:
            recent = my_activities.tail(5).sort_index(ascending=False)
            st.dataframe(recent[['action', 'points', 'timestamp']], use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Could not load mission history: {e}")

    # Certificate Section
    st.markdown("---")
    st.markdown("### 🎖️ Certificate Status")
    
    if st.session_state.get('username'):
        username = st.session_state['username']
        try:
            cert_info = auth.get_certificate_info(username)
            
            if cert_info:
                st.success("🎉 You have earned your certificate!")
                st.markdown(f"**Issued on:** {cert_info['issued_date']}")
                st.markdown(f"**Certificate ID:** `{cert_info['certificate_id']}`")

                pdf_buffer = auth.generate_certificate_pdf(
                    username,
                    cert_info['eco_score'],
                    cert_info['rank'],
                    len(auth.get_leaderboard_data())
                )
                st.download_button(
                    label="⬇️ Download Your Certificate (PDF)",
                    data=pdf_buffer,
                    file_name=f"Certificate_{username}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                is_eligible, eco_score = auth.check_certificate_eligibility(username)
                st.metric("Your Eco-Score", eco_score)
                st.metric("Required for Certificate", "500")
                if is_eligible:
                    st.info("You are eligible to claim your certificate!")
                    if st.button("🏆 Claim Your Certificate Now!", use_container_width=True):
                        success, result = auth.issue_certificate(username)
                        if success:
                            st.balloons()
                            st.success("Congratulations! Your certificate has been issued. Refreshing...")
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(f"❌ Could not issue certificate: {result}")
                else:
                    progress = (eco_score / 500) * 100
                    st.warning(f"⏳ Keep going! You are at {progress:.1f}% of the way to your certificate.")
                    st.progress(min(progress / 100, 1.0))
        except Exception as e:
            st.error(f"Error loading certificate info: {e}")
    else:
        st.warning("Please login to view certificate status")


# ==========================================
# 6. SUSTAINABILITY PREDICTOR
# ==========================================

def sustainability_predictor():
    st.markdown('<div class="eco-card"><h3>🔮 Predict Your Sustainability Impact</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🌍 Carbon Footprint Tracker")
        
        transport = st.selectbox("🚗 Transportation:", 
                                ["Walk/Bike (-5 CO₂)", "Public Transport (-2 CO₂)", 
                                 "Electric Car (0 CO₂)", "Gasoline Car (+10 CO₂)"],
                                key="transport")
        
        diet = st.selectbox("🍽️ Diet:", 
                           ["Plant-Based (-3 CO₂)", "Local Produce (-2 CO₂)", 
                            "Mixed Diet (+2 CO₂)", "Imported Meat (+8 CO₂)"],
                           key="diet")
        
        energy = st.selectbox("💡 Energy:", 
                             ["Solar Power (-5 CO₂)", "Energy Saver (-3 CO₂)", 
                              "Normal Usage (+1 CO₂)", "High Consumption (+7 CO₂)"],
                             key="energy")
        
        if st.button("📊 Calculate Impact", key="calc_impact"):
            # Extract values
            transport_val = int(transport.split('(')[1].split()[0].replace('+', ''))
            diet_val = int(diet.split('(')[1].split()[0].replace('+', ''))
            energy_val = int(energy.split('(')[1].split()[0].replace('+', ''))
            
            change = transport_val + diet_val + energy_val
            st.session_state['carbon_footprint'] += change
            st.session_state['carbon_footprint'] = max(0, min(100, st.session_state['carbon_footprint']))
            
            if change < 0:
                st.success(f"🎉 Amazing! You reduced carbon by {abs(change)} units!")
                log_action("Carbon Reduction", abs(change) * 2)
                st.balloons()
            else:
                st.warning(f"⚠️ Your choices increased carbon by {change} units.")
            
            time.sleep(1)
            st.rerun()
    
    with col2:
        carbon = st.session_state['carbon_footprint']
        st.metric("🌡️ Your Carbon Level", f"{carbon} CO₂")
        
        # Status
        if carbon <= 25:
            status = "🌟 Eco Hero!"
            color = "#4CAF50"
        elif carbon <= 50:
            status = "👍 Good Job!"
            color = "#FFC107"
        else:
            status = "🔥 Need Improvement"
            color = "#F44336"
        
        st.markdown(f"**Status:** {status}")
        
        # Progress bar
        percentage = min(100, (carbon / 100) * 100)
        progress_html = f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {percentage}%; background-color: {color};">
                {int(percentage)}%
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        if st.button("🔄 Reset", key="reset_carbon"):
            st.session_state['carbon_footprint'] = 100
            st.rerun()

# ==========================================
# 7. GAMES HUB (PYGAME EMBEDDED)
# ==========================================

def games_hub():
    st.markdown('<div class="eco-card"><h2>🎯 Interactive Sustainability Games</h2><p>Play, Learn, and Save the Planet!</p></div>', unsafe_allow_html=True)
    
    if 'show_quiz_game' not in st.session_state:
        st.session_state.show_quiz_game = False

    if st.session_state.show_quiz_game:
        if st.button("⬅️ Back to Games Hub"):
            st.session_state.show_quiz_game = False
            st.rerun()
        quiz_interface()
        return

    # Age Recommendation System
    st.markdown("### 👤 Game Recommendation")
    age_group = st.radio(
        "What is your age? Select an age group to see our recommended games!",
        ["Show All Categories", "3 to 7 Years (Small Level)", "8 to 13 Years (Medium Level)", "14+ Years (Senior Level)"],
        horizontal=True
    )
    st.divider()

    def render_small_games():
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        row3_col1, _ = st.columns(2)
        
        with row1_col1:
            st.markdown('''
            <div class="game-card">
                <h3>🏃 Eco-Runner</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/3588/3588435.png" width="120">
                <p style="margin: 15px 0;">Control a person collecting leaves while avoiding waste! Get your carbon score to zero!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.info("🎮 **How to Play:**\n- Use ↑↓ arrow keys to move\n- Collect green leaves (-10 CO₂)\n- Avoid red waste (+20 CO₂)\n- Goal: Reach 0 carbon!")
            
            if st.button("🎮 Launch Eco-Runner", key="launch_eco_runner"):
                st.success("✅ Game launching! Check the pygame window that opened.")
                st.balloons()
                try:
                    import games.eco_runner as eco_runner
                    game_score = eco_runner.run_game()
                    log_action("Eco-Runner Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score}. Try winning next time!")
                    import time
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row1_col2:
            st.markdown('''
            <div class="game-card">
                <h3>🗑️ Eco Sorter</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/3299/3299935.png" width="120">
                <p style="margin: 15px 0;">Catch biodegradable items and avoid non-biodegradable waste in this 2D challenge!</p>
            </div>
            ''', unsafe_allow_html=True)
    
            st.info("🎮 **How to Play:**\n- ←→ or Mouse to move basket\n- Catch green/organic items (+2 pts)\n- Avoid plastic/metal (-1 pt)\n- Survive for 60s!")
    
            if st.button("🎮 Launch Eco Sorter", key="launch_eco_sorter"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.eco_sorter_wrapper as eco_sorter_wrapper
                    game_score = eco_sorter_wrapper.run_game()
                    log_action("Eco Sorter Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to catch more organic items next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row2_col1:
            st.markdown('''
            <div class="game-card">
                <h3>🏏 Eco Cricket</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/1000/1000454.png" width="120">
                <p style="margin: 15px 0;">Hit the ball to grow nature, smash waste, and save the planet!</p>
            </div>
            ''', unsafe_allow_html=True)
            st.info("🎮 **How to Play:**\n- SPACE / LEFT CLICK to swing bat.\n- Hit good items to grow nature and earn points.\n- Hit waste to destroy it, but lose points.\n- 5 misses and it's game over!")
    
            if st.button("🎮 Launch Eco Cricket", key="launch_eco_cricket"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.eco_cricket_wrapper as eco_cricket_wrapper
                    game_score = eco_cricket_wrapper.run_game()
                    log_action("Eco Cricket Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to hit more eco items and less waste next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row2_col2:
            st.markdown('''
            <div class="game-card">
                <h3>🧩 Eco Puzzle 3D</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/1039/1039328.png" width="120">
                <p style="margin: 15px 0;">Solve fun 3D puzzles, match eco pairs, and learn sustainability facts!</p>
            </div>
            ''', unsafe_allow_html=True)
    
            st.info("🎮 **How to Play:**\n- Pick a puzzle from the menu\n- Use your mouse to interact\n- Earn points for each puzzle solved!")
    
            if st.button("🎮 Launch Eco Puzzle 3D", key="launch_eco_puzzle"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.eco_puzzle_wrapper as eco_puzzle_wrapper
                    game_score = eco_puzzle_wrapper.run_game()
                    log_action("Eco Puzzle 3D Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to solve more puzzles next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row3_col1:
            st.markdown('''
            <div class="game-card">
                <h3>♻️ Smart Waste Segregation</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/3524/3524388.png" width="120">
                <p style="margin: 15px 0;">Use hand gestures to sort waste into correct bins! AI-powered recycling game!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.info("🎮 **How to Play:**\n- Allow camera access\n- Use hand pinch to grab items\n- Sort into correct colored bins\n- Goal: High score before 5 misses!")
            
            if st.button("🎮 Launch Waste Segregation", key="launch_waste_seg"):
                st.success("✅ Game launching! Check the window that opened.")
                st.balloons()
                try:
                    import games.waste_seg_wrapper as waste_seg_wrapper
                    game_score = waste_seg_wrapper.run_game()
                    log_action("Waste Segregation Attempt", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                        st.write(f"**Points earned from game:** {game_score}")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try sorting more items correctly!")
                        st.write(f"**Points earned from game:** {game_score}")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

    def render_medium_games():
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        row3_col1, _ = st.columns(2)

        with row1_col1:
            st.markdown('''
            <div class="game-card">
                <h3>🏃 Sustainability Runner</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/2921/2921766.png" width="120">
                <p style="margin: 15px 0;">A Subway Surfer-style game. Collect eco items and dodge pollution!</p>
            </div>
            ''', unsafe_allow_html=True)
    
            st.info("🎮 **How to Play:**\n- ←→/AD to move lanes\n- ↑/W/SPACE to jump\n- ↓/S to slide\n- Collect good items, avoid bad ones!")
    
            if st.button("🎮 Launch Sustainability Runner", key="launch_sustainability_runner"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.sustainability_runner_wrapper as sustainability_runner_wrapper
                    game_score = sustainability_runner_wrapper.run_game()
                    log_action("Sustainability Runner Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to collect more eco items next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row1_col2:
            st.markdown('''
            <div class="game-card">
                <h3>🧩 Eco-Crush Pro</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/3409/3409390.png" width="120">
                <p style="margin: 15px 0;">Match detailed eco-icons in this advanced puzzle game. A true test of your matching skills!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.info("🎮 **How to Play:**\n- Use your mouse to click and swap adjacent tiles.\n- Match 3 or more to score points!\n- You have a limited number of moves.")
            
            if st.button("🎮 Launch Eco-Crush Pro", key="launch_eco_crush"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.eco_crush_ai as eco_crush_ai
                    game_score = eco_crush_ai.run_game()
                    log_action("Eco-Crush Pro Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score}. Try to get more matches next time!")
                    import time
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row2_col1:
            st.markdown('''
            <div class="game-card">
                <h3>🌊 Ocean Guardian</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/9477/9477390.png" width="120">
                <p style="margin: 15px 0;">Captain a ship to clean waste from the ocean and restore biodiversity by planting seagrass.</p>
            </div>
            ''', unsafe_allow_html=True)
            st.info("🎮 **How to Play:**\n- Use ←→ arrow keys to move your ship.\n- Press SPACE to fire a detector ray.\n- Clean all waste to plant seagrass and win!\n- Win the game to earn points.")
    
            if st.button("🎮 Launch Ocean Guardian", key="launch_ocean_guardian"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.ocean_guardian_wrapper as ocean_guardian_wrapper
                    game_score = ocean_guardian_wrapper.run_game()
                    log_action("Ocean Guardian Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Mission complete! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to clean up all the waste next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row2_col2:
            st.markdown('''
            <div class="game-card">
                <h3>🐍 Eco Snake 3D</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/861/861882.png" width="120">
                <p style="margin: 15px 0;">A Pseudo-3D Sustainability Snake Game! Clean the planet and grow your snake.</p>
            </div>
            ''', unsafe_allow_html=True)
    
            st.info("🎮 **How to Play:**\n- Arrow keys / WASD to move\n- Collect green waste (+2 points)\n- Avoid red waste (-1 point & -HP)\n- Press H for AI hints!")
    
            if st.button("🎮 Launch Eco Snake 3D", key="launch_eco_snake"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.eco_snake_wrapper as eco_snake_wrapper
                    game_score = eco_snake_wrapper.run_game()
                    log_action("Eco Snake 3D Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to collect more bio waste next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row3_col1:
            st.markdown('''
            <div class="game-card">
                <h3>🌍 Planet Earth Simulation</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/814/814513.png" width="120">
                <p style="margin: 15px 0;">Make sustainable choices to protect the planet from pollution!</p>
            </div>
            ''', unsafe_allow_html=True)
    
            st.info("🎮 **How to Play:**\n- Click to choose actions\n- Collect 50 GOOD points to WIN\n- Collect 15 BAD points to LOSE\n- Press E to exit and save score")
    
            if st.button("🎮 Launch Planet Earth", key="launch_planet_earth"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.planet_game_wrapper as planet_game_wrapper
                    game_score = planet_game_wrapper.run_game()
                    log_action("Planet Earth Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to make better sustainable choices next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

    def render_senior_games():
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        with row1_col1:
            st.markdown('''
            <div class="game-card">
                <h3>🧠 Quiz Game</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/4148/4148323.png" width="120">
                <p style="margin: 15px 0;">Test your knowledge in a KBC-style challenge and win Plant Points!</p>
            </div>
            ''', unsafe_allow_html=True)
            st.info("🎮 **How to Play:**\n- Click 'Launch' to start\n- Answer a series of questions\n- Correct = +5 points\n- Wrong = -2.5 points\n- Goal: Win a Tree Plantation!")
            if st.button("🎮 Launch Quiz Game", key="launch_quiz_game"):
                st.session_state.show_quiz_game = True
                st.rerun()

        with row1_col2:
            st.markdown('''
            <div class="game-card">
                <h3>🔥 Fire Rescue 3D</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/482/482631.png" width="120">
                <p style="margin: 15px 0;">First-person mission: Protect the Sacred Tree from falling fireballs! Use mouse to shoot water.</p>
            </div>
            ''', unsafe_allow_html=True)
    
            st.info("🎮 **How to Play:**\n- WASD to move | Mouse to aim | Click to shoot water\n- Protect the Sacred Tree — if a fireball hits leaves, the mission ends!")
    
            if st.button("🎮 Launch Fire Rescue", key="launch_fire_rescue"):
                st.success("✅ Game launching! Check the Ursina window that opened.")
                st.balloons()
                try:
                    import games.fire_rescue as fire_rescue
                    game_score = fire_rescue.run_game()
                    log_action("Fire Rescue 3D Attempt", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Mission complete! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try shooting more fireballs next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row2_col1:
            st.markdown('''
            <div class="game-card">
                <h3>🌲 Eco Defender</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/2913/2913520.png" width="120">
                <p style="margin: 15px 0;">Protect nature by shooting down waste objects before they escape!</p>
            </div>
            ''', unsafe_allow_html=True)
            st.info("🎮 **How to Play:**\n- Click on waste to shoot (points vary by difficulty)\n- Missed waste costs points & 1 life (points vary by difficulty)\n- You have 6 lives. Press ESC to exit")
    
            if st.button("🎮 Launch Eco Defender", key="launch_eco_defender"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import games.eco_defender_wrapper as eco_defender_wrapper
                    game_score = eco_defender_wrapper.run_game()
                    log_action("Eco Defender Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Keep protecting the forest!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

        with row2_col2:
            st.markdown('''
            <div class="game-card">
                <h3>🚁 Sky Patrol: Waste Hunt</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/9363/9363297.png" width="120">
                <p style="margin: 15px 0;">Hunt down pollution and protect the forest from toxic waste as an Eco-Cop!</p>
            </div>
            ''', unsafe_allow_html=True)
    
            st.info("🎮 **How to Play:**\n- WASD / Arrows to move\n- Click or SPACE to shoot (+2 for a hit, -1 for a miss)\n- E to scan for hidden waste\n- R to reload\n- ESC to quit")
    
            if st.button("🎮 Launch Sky Patrol", key="launch_sky_patrol"):
                st.success("✅ Game launching! Check the new window that opened.")
                st.balloons()
                try:
                    import sky_patrol_wrapper
                    game_score = sky_patrol_wrapper.run_game()
                    log_action("Sky Patrol Game", game_score)
                    if game_score > 0:
                        st.success(f"🎉 Game completed! +{game_score} points added!")
                    else:
                        st.info(f"Game played! Score: {game_score} points. Try to shoot more waste next time!")
                    import time
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error launching game: {str(e)}")

    if age_group == "Show All Categories":
        tab_small, tab_medium, tab_senior = st.tabs([
            "🧸 Small Children (3-7 Years)", 
            "🎒 Medium Level (8-13 Years)", 
            "🎓 Senior Level (14+ Years)"
        ])
        with tab_small:
            render_small_games()
        with tab_medium:
            render_medium_games()
        with tab_senior:
            render_senior_games()
    elif "3 to 7" in age_group:
        st.info("🧸 **Recommended Games for Age 3 to 7 (Small Level, Nursery to 2nd)**: Simple mechanics, engaging visual tasks, and easy controls!")
        render_small_games()
    elif "8 to 13" in age_group:
        st.info("🎒 **Recommended Games for Age 8 to 13 (Medium Level, Std 3rd to 8th)**: Strategic challenges, reaction times, and broader mechanics!")
        render_medium_games()
    elif "14+" in age_group:
        st.info("🎓 **Recommended Games for Age 14+ (Senior Level, Std 9th to 12th)**: Deep logic, complex simulations, and first-person actions!")
        render_senior_games()

# 8. ADMIN DASHBOARD
# ==========================================

def admin_dashboard():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1d976c 0%, #93f9b9 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h1 style="margin:0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">🏫 Admin Dashboard</h1>
            <p style="margin-top: 10px; font-size: 1.2em; opacity: 0.9;">Overview of School Sustainability Impact</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load global data from CSV instead of session data to show old records
    try:
        global_df = auth.get_all_activities()
        if not global_df.empty:
            # Normalize columns to match session data format for charts
            df = global_df.rename(columns={
                'timestamp': 'Date',
                'username': 'Student_ID',
                'action': 'Action',
                'points': 'Points'
            })
        else:
            df = pd.DataFrame(columns=['Student_ID', 'Action', 'Points', 'Date']) # Empty dataframe
    except Exception as e:
        st.error(f"Could not load activities: {e}")
        df = pd.DataFrame(columns=['Student_ID', 'Action', 'Points', 'Date']) # Empty dataframe
    
    if df.empty:
        st.info("📊 No data yet. Wait for users to start logging missions and playing games!")
        return

    # Metrics Layout Redesign
    st.markdown("### 🌟 Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="eco-card" style="text-align: center; border-bottom: 5px solid #28a745;">
            <h2 style="color: #28a745; margin: 0; font-size: 2.5em;">{df['Points'].sum()}</h2>
            <p style="color: #555; font-size: 1.1em; font-weight: bold; margin-top: 5px;">🌱 Total Eco-Points</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="eco-card" style="text-align: center; border-bottom: 5px solid #17a2b8;">
            <h2 style="color: #17a2b8; margin: 0; font-size: 2.5em;">{len(df)}</h2>
            <p style="color: #555; font-size: 1.1em; font-weight: bold; margin-top: 5px;">📊 Total Actions Logged</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        trees_planted = len(df[df['Action'] == "Planted a Tree"])
        st.markdown(f"""
        <div class="eco-card" style="text-align: center; border-bottom: 5px solid #ffc107;">
            <h2 style="color: #ffc107; margin: 0; font-size: 2.5em;">{trees_planted}</h2>
            <p style="color: #555; font-size: 1.1em; font-weight: bold; margin-top: 5px;">🌳 Trees Planted</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Charts
    st.markdown("### 📈 Analytics & Trends")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig_pie = px.pie(df, names='Action', values='Points', 
                        title="Impact Distribution by Action", 
                        color_discrete_sequence=px.colors.sequential.Teal)
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Poppins"))
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with chart_col2:
        action_summary = df.groupby('Action')['Points'].sum().reset_index()
        fig_bar = px.bar(action_summary, x='Action', y='Points', 
                        title="Top Activities Contributed",
                        color='Points',
                        color_continuous_scale='Mint')
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Poppins"))
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Activity Log
    st.markdown("### 📈 Activity Log")
    try:
        all_activities = auth.get_all_activities()
        if not all_activities.empty:
            st.dataframe(all_activities.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("No activities logged yet.")
    except Exception as e:
        st.error(f"Could not load activity log: {e}")
        # Fallback to session data
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

    # Global Leaderboard
    st.markdown("---")
    st.markdown("### 🏆 Global Leaderboard & Performance Analytics")
    
    try:
        # Get leaderboard data with ranks
        leaderboard_data = auth.get_leaderboard_data()
        
        if not leaderboard_data.empty:
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👥 Total Users", len(leaderboard_data))
            col2.metric("🥇 Top Score", leaderboard_data['eco_score'].max())
            col3.metric("📊 Avg Score", round(leaderboard_data['eco_score'].mean(), 1))
            col4.metric("📈 Total Score", leaderboard_data['eco_score'].sum())
            
            st.divider()
            
            # Display top 3 with special formatting
            st.markdown("#### 🎖️ Top 3 Guardians")
            top3_cols = st.columns(3)
            
            medals = ["🥇", "🥈", "🥉"]
            for idx, (col, medal) in enumerate(zip(top3_cols, medals)):
                if idx < len(leaderboard_data):
                    user = leaderboard_data.iloc[idx]
                    with col:
                        st.markdown(f"""
                            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
                                <h1>{medal}</h1>
                                <h3>{user['username']}</h3>
                                <p><strong>{user['full_name']}</strong></p>
                                <h2>⭐ {user['eco_score']} pts</h2>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.divider()
            
            # Leaderboard Filters & Search
            st.markdown("#### 🔍 Leaderboard Controls")
            search_col, filter_col = st.columns([2, 1])
            
            with search_col:
                search_query = st.text_input("🔎 Search by username or name:", placeholder="Type to filter...")
            
            with filter_col:
                sort_order = st.selectbox("Sort by:", ["Top Score (Descending)", "Top Score (Ascending)", "Username (A-Z)"])
            
            # Apply search filter
            filtered_df = leaderboard_data.copy()
            if search_query:
                filtered_df = filtered_df[
                    (filtered_df['username'].str.contains(search_query, case=False)) |
                    (filtered_df['full_name'].str.contains(search_query, case=False))
                ]
            
            # Apply sort
            if sort_order == "Top Score (Ascending)":
                filtered_df = filtered_df.sort_values('eco_score', ascending=True).reset_index(drop=True)
            elif sort_order == "Username (A-Z)":
                filtered_df = filtered_df.sort_values('username', ascending=True).reset_index(drop=True)
            else:  # Default: Top Score (Descending)
                filtered_df = filtered_df.sort_values('eco_score', ascending=False).reset_index(drop=True)
            
            st.divider()
            
            # Full Leaderboard Table with Rank, Username, Name, and Score
            st.markdown(f"#### 📋 Complete Leaderboard ({len(filtered_df)} Users)")
            
            # Prepare display dataframe with ranking
            display_df = filtered_df[['rank', 'username', 'full_name', 'eco_score']].copy()
            display_df.columns = ['🏅 Rank', '👤 Username', '📝 Full Name', '⭐ Eco-Score']
            
            # Display as dataframe with custom styling
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Performance Analytics
            st.divider()
            st.markdown("#### 📊 Performance Analytics")
            
            analytics_col1, analytics_col2 = st.columns(2)
            
            with analytics_col1:
                # Score distribution chart
                fig_hist = px.histogram(leaderboard_data, x='eco_score', 
                                       title="Score Distribution",
                                       labels={'eco_score': 'Eco-Score', 'count': 'Number of Users'},
                                       color_discrete_sequence=['#00b09b'])
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with analytics_col2:
                # Top performers chart
                top_10 = leaderboard_data.nlargest(10, 'eco_score')
                fig_top = px.bar(top_10, x='username', y='eco_score',
                                title="Top 10 Performers",
                                labels={'eco_score': 'Eco-Score', 'username': 'Username'},
                                color='eco_score',
                                color_continuous_scale='Greens')
                st.plotly_chart(fig_top, use_container_width=True)
            
            # Highlight current user's rank (if logged in)
            st.divider()
            if st.session_state.get('username'):
                user_rank = auth.get_user_rank(st.session_state['username'])
                user_row = leaderboard_data[leaderboard_data['username'] == st.session_state['username']]
                
                if not user_row.empty:
                    user_percentile = auth.get_user_percentile(st.session_state['username'])
                    user_score = int(user_row['eco_score'].values[0])
                    
                    if user_rank:
                        col_rank1, col_rank2, col_rank3 = st.columns(3)
                        col_rank1.info(f"📍 Your Rank: **#{user_rank}** out of {len(leaderboard_data)}")
                        col_rank2.success(f"🎯 Your Percentile: **{user_percentile}%**")
                        col_rank3.warning(f"⭐ Your Score: **{user_score}** points")
            
            # Top user highlight
            top_user = leaderboard_data.iloc[0]
            st.success(f"🎉 **Top Guardian:** {top_user['username']} ({top_user['full_name']}) with {top_user['eco_score']} eco-points!")
            
        else:
            st.info("📊 No leaderboard data available yet. Start playing games and completing missions!")
            
    except Exception as e:
        st.error(f"Could not load leaderboard: {e}")

    # Certificate Management (Hidden - Certificates now auto-issued in Student Hub)
    # This section is for viewing certificates. Issuing is done in the Student Hub.
    # Admin can view issued certificates below for informational purposes.
    
    st.markdown("---")
    st.markdown("### 🎖️ Certificate Status (View Only)")
    st.info("📌 **Note:** Certificates are now automatically issued in the Student Hub when eligible users confirm. Admins can view all issued certificates below.")
    
    cert_tab = st.tabs(["✅ View Issued Certificates"])
    
    with cert_tab[0]:
        st.markdown("#### View All Issued Certificates")
        
        try:
            all_certs = auth.get_all_certificates()
            
            if all_certs.empty:
                st.info("📜 No certificates issued yet.")
            else:
                # Display certificates
                for idx, (_, cert) in enumerate(all_certs.iterrows()):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{cert['username']}** - Score: {cert['eco_score']} | Rank: #{cert['rank']}")
                        st.caption(f"Issued: {cert['issued_date']}")
                    
                    with col2:
                        user_data = auth.get_user_info(cert['username'])
                        if user_data:
                            st.write(f"📍 {user_data.get('full_name', 'N/A')}")
                    
                    with col3:
                        if st.button(f"Download", key=f"download_{cert['certificate_id']}"):
                            # Generate PDF
                            pdf_buffer = auth.generate_certificate_pdf(
                                cert['username'],
                                cert['eco_score'],
                                cert['rank'],
                                len(all_certs)
                            )
                            st.download_button(
                                label="⬇️ PDF Certificate",
                                data=pdf_buffer,
                                file_name=f"Certificate_{cert['username']}.pdf",
                                mime="application/pdf",
                                key=f"pdf_download_{cert['certificate_id']}"
                            )
        except Exception as e:
            st.error(f"Error loading certificates: {e}")

# ==========================================
# 9. MAIN LAYOUT
# ==========================================

def main():
    # Check for persistent login via query params (Handle Page Refresh)
    if not st.session_state['logged_in']:
        params = st.query_params
        if params.get("logged_in") == "true" and params.get("user"):
            username = params.get("user")
            user_info = auth.get_user_info(username)
            if user_info:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['role'] = params.get("role", user_info.get("role", "person"))
                st.session_state['user_info'] = user_info
                if 'eco_score' in user_info:
                    st.session_state['eco_score'] = int(user_info['eco_score'])
                st.rerun()

    # Check if user is logged in
    if not st.session_state['logged_in']:
        # Show login or signup page
        if st.session_state.get('show_signup', False):
            auth.signup_page()
        else:
            auth.login_page()
        return
    
    # Ensure role is set in session state
    if 'role' not in st.session_state:
        st.session_state['role'] = st.session_state.get('user_info', {}).get('role', 'person')
        
    user_role = st.session_state['role']
    
    # User is logged in - show main app
    # Sidebar
    with st.sidebar:
        st.title("🌍 Climate Guardian")
        
        st.markdown("""
            <div class="logo-container">
                <img src="https://cdn-icons-png.flaticon.com/512/1165/1165674.png" class="logo-img">
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Save Earth, Save Future** 🌿")
        
        # User Profile Section
        st.markdown("---")
        st.markdown(f"### 👤 Welcome, {st.session_state['username']}!")
        
        if user_role == 'person':
            # Calculate eco score from actual activities instead of database
            user_eco_score = auth.get_user_eco_score_from_activities(st.session_state['username'])
            st.metric("🌱 Total Eco-Score", user_eco_score)
        
        st.markdown("---")
        
        if user_role == 'admin':
            st.markdown("📍 **Current View:** Admin Dashboard")
        else:
            st.markdown("📍 **Current View:** Student Hub")
        
        st.divider()
        if user_role == 'person':
            st.info("💡 **Tip:** Complete missions daily to earn Eco-Points!")
        
        # Logout button
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            # Update user score before logout
            if st.session_state['username'] and user_role == 'person':
                auth.update_user_score(st.session_state['username'], int(st.session_state.get('eco_score', 0)))
            auth.logout()
        
        st.caption("Developed by Environment Cleaner")

    # Header
    st.title(f"🌿 Welcome to Climate Guardian, {st.session_state['username']}!")
    if user_role == 'admin':
        st.markdown("*Your Administrative Control Center*")
    else:
        st.markdown("*Your AI-powered companion for a greener planet*")
    st.divider()

    # Main Content based on role
    if user_role == 'admin':
        admin_dashboard()
    else:
        tab1, tab2, tab3 = st.tabs([
            "🎯 Games Hub",
            "✅ Missions", 
            "🔮 Predict Sustainability"
        ])
        
        with tab1:
            games_hub()
        with tab2:
            mission_tracker()
        with tab3:
            sustainability_predictor()

    # --- Floating Chat Widget Implementation ---
    # This section uses CSS to style a Streamlit container as a floating modal.
    # It's a robust workaround that avoids the previous issues.
    st.markdown("""
    <style>
        /* Container for the button, to position it */
        .fab-container {
            position: fixed;
            bottom: 40px;
            right: 40px;
            z-index: 1000;
        }
        /* Styling the button itself to look like a FAB */
        .fab-container .stButton button {
            width: 80px; height: 80px; border-radius: 50%;
            background: linear-gradient(120deg, #00b09b, #96c93d); color: white;
            font-weight: 600; font-size: 16px; border: none;
            box-shadow: 0 6px 20px rgba(0, 176, 155, 0.4);
        }
        /* Wrapper for the chat window, to position it */
        .chat-window-wrapper {
            position: fixed;
            bottom: 40px;
            right: 40px;
            z-index: 1001;
        }
        /* Styling the container that holds the chat widgets */
        .chat-window-wrapper > div[data-testid="stVerticalBlock"] {
            width: 380px; height: 600px;
            background-color: #f0f7f4;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border: 1px solid #e0e0e0;
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.get('show_chat', False):
        st.markdown('<div class="chat-window-wrapper">', unsafe_allow_html=True)
        with st.container():
            chat_interface()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="fab-container">', unsafe_allow_html=True)
        if st.button("Ask Me", key="open_chat_fab"):
            st.session_state.show_chat = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
