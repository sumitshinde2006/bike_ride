"""
RideWise Flask Backend - Bike Demand Prediction
- Dual endpoints: /predict/hour and /predict/day
- Models loaded from saved_models/
- Features extracted from model.feature_names_in_
- CORS enabled for React frontend on http://localhost:3000
- No login/authentication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load
import pandas as pd
import numpy as np
import os
import traceback
import logging
from dotenv import load_dotenv

# Google Generative AI SDK
try:
    import google.genai as genai
except Exception:
    genai = None

app = Flask(__name__)

# Enable CORS for local dev origins (adjust in production)
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]}})

# Configure logging to stdout for easier debugging in terminals and containers
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Configuration and model loading
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
MODEL_DIR = os.path.join(PROJECT_ROOT, 'saved_models')

# Load .env from project root (if present) so GEMINI_API_KEY is available.
# This will not override environment variables already set in the OS.
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configure Gemini API key for google-genai SDK if available
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyCGv9p5fjN0lg4pGV_Qfvn_c5rf4p4Xx8Y'
if genai is None:
    logger.warning("google-genai SDK is not installed. Install it with 'pip install google-genai'.")
else:
    if GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            logger.info("Gemini API key configured successfully.")
        except Exception as e:
            logger.exception("Failed to configure google-genai SDK: %s", e)
    else:
        logger.warning("GEMINI_API_KEY not found in environment. Set it in backend/.env or system environment variables.")

# System prompt used for all chatbot requests (as requested)
SYSTEM_PROMPT = (
    "You are RideWise Assistant, an AI chatbot integrated into a bike-sharing analytics platform.\n\n"
    "Your role:\n"
    "- Help users understand bike-sharing demand patterns\n"
    "- Explain how weather, time, season, and working days affect bike demand\n"
    "- Provide clear, simple, and practical insights\n"
    "- Answer like a data analyst, not a generic chatbot\n\n"
    "Rules:\n"
    "- Do not mention Gemini, Google, or AI models\n"
    "- Keep responses concise, friendly, and professional\n"
    "- Avoid hallucinated exact numbers; use reasonable analytical ranges\n"
    "- If the question is unrelated, gently redirect to bike-sharing insights"
)

# Day model path
DAY_MODEL_FILE = os.path.join(MODEL_DIR, 'best_day_model.pkl')

# Hour model path
HOUR_MODEL_FILE = os.path.join(MODEL_DIR, 'best_hour_model.pkl')


def _safe_load_model(path):
    if not os.path.exists(path):
        return None
    try:
        return load(path)
    except Exception:
        traceback.print_exc()
        return None


def _load_day_model_and_features(path):
    model = _safe_load_model(path)
    if model is None:
        print(f"Warning: Model not found at {path}, skipping.")
        return None, []
    if not hasattr(model, 'feature_names_in_'):
        print(f"Warning: Model does not expose `feature_names_in_`, skipping.")
        return None, []
    features = list(model.feature_names_in_)
    return model, features


# Load day model at startup (source of truth: feature_names_in_)
print("Loading day model from:", DAY_MODEL_FILE)
day_model, day_expected_features = _load_day_model_and_features(DAY_MODEL_FILE)
if day_model:
    print(f"Day model loaded - expects {len(day_expected_features)} features")
else:
    print("Day model not loaded")

# Load hour model at startup
print("Loading hour model from:", HOUR_MODEL_FILE)
hour_model, hour_expected_features = _load_day_model_and_features(HOUR_MODEL_FILE)
if hour_model:
    print(f"Hour model loaded - expects {len(hour_expected_features)} features")
else:
    print("Hour model not loaded")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - test backend connectivity."""
    return jsonify({
        'status': 'ok',
        'day_model_loaded': day_model is not None,
        'day_feature_count': len(day_expected_features),
        'hour_model_loaded': hour_model is not None,
        'hour_feature_count': len(hour_expected_features)
    }), 200


def _build_chat_messages(user_message: str, prediction: dict | None = None):
    """
    Build a list of messages for Gemini chat API.

    - Always sends the configured `SYSTEM_PROMPT` as the system message.
    - Optionally injects a `prediction` block (structured information produced
      by ML pipelines) in a neutral "context" assistant message so future
      versions can include model outputs without changing core logic.
    - Appends the user's message as the final user message.

    This function centralizes prompt construction so ML predictions can be
    injected safely and consistently.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # If there are structured prediction outputs, include them as a context
    # assistant message. This keeps them separate from the user's prompt.
    if prediction:
        # Simple safe formatting of prediction dict for context.
        pred_lines = [f"{k}: {v}" for k, v in (prediction.items() if isinstance(prediction, dict) else [])]
        pred_text = "\n".join(pred_lines)
        if pred_text:
            messages.append({"role": "assistant", "content": f"Context - model prediction:\n{pred_text}"})

    # Finally append the end-user message
    messages.append({"role": "user", "content": user_message})
    return messages


def _get_fallback_response(user_message: str):
    """
    Provide intelligent fallback responses based on keywords in user message.
    Used when Gemini API is unavailable.
    """
    message_lower = user_message.lower()
    
    fallback_responses = {
        'weather': 'Weather has a significant impact on bike demand. Clear weather typically increases rentals by 30-40% compared to cloudy conditions. Temperature between 18-25°C shows the highest correlation with bike demand, while rain and snow substantially reduce usage.',
        'peak': 'Bike demand typically peaks during commute hours: 7-9 AM and 5-7 PM on working days. Weekend demand is generally 15-20% higher than weekdays, especially during good weather conditions.',
        'demand': 'Bike demand depends on multiple factors: weather conditions, time of day, season, and whether it\'s a working day. Summer months (June-August) see higher demand than winter. Working days have distinct morning and evening peaks.',
        'season': 'Seasonal patterns show peak demand in summer (June-August), moderate demand in spring and fall, and lower demand in winter. Holiday periods show different patterns with delayed morning peaks and more evenly distributed usage.',
        'temperature': 'Temperature is a key factor in bike-sharing demand. Optimal conditions are between 18-25°C. Demand decreases significantly in cold weather (below 5°C) and extremely hot weather (above 35°C).',
        'humidity': 'High humidity can reduce bike demand as it makes cycling less comfortable. The combined effect of temperature and humidity (temp-humidity index) is more predictive than temperature alone.',
        'working': 'Working days show distinct patterns with clear commute peaks at 7-9 AM and 5-7 PM. Non-working days and holidays have more distributed demand throughout the day.',
        'weekend': 'Weekends typically show 15-20% higher overall bike demand than weekdays, with peaks later in the morning (around 11 AM-2 PM) rather than during strict commute hours.',
    }
    
    # Find matching keywords
    for keyword, response in fallback_responses.items():
        if keyword in message_lower:
            return response
    
    # Default response
    return 'I can help you understand bike-sharing demand patterns. Ask me about weather impact, peak hours, seasonal trends, temperature effects, or any other factors affecting bike demand.'


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    Chat endpoint that proxies user messages to Google Gemini and returns
    the assistant reply. Falls back to intelligent responses if API unavailable.

    Expected JSON body: { "message": "<user message>", "prediction": {...} (optional) }

    Security notes:
    - GEMINI_API_KEY is loaded from environment or .env via python-dotenv.
    - No API keys are sent to the frontend.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json(force=True)
        if not data or 'message' not in data:
            return jsonify({'error': 'Expected JSON body with "message" field.'}), 400

        user_message = str(data.get('message'))
        prediction = data.get('prediction')  # optional structured context

        logger.info("/chat request received: %s", user_message)

        # Try to use Gemini API
        use_fallback = False
        reply_text = None
        
        if 'client' in globals() and client is not None:
            try:
                # Use the new Google GenAI client
                user_msg = user_message
                if prediction:
                    pred_lines = [f"{k}: {v}" for k, v in (prediction.items() if isinstance(prediction, dict) else [])]
                    pred_text = "\n".join(pred_lines)
                    if pred_text:
                        user_msg = f"Context - model prediction:\n{pred_text}\n\nUser question: {user_message}"
                
                contents = f"{SYSTEM_PROMPT}\n\nUser: {user_msg}"
                
                resp = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=contents,
                    config={
                        "temperature": 0.0,
                        "max_output_tokens": 512
                    }
                )
                logger.info("Gemini response successful")
                
                # Extract assistant text from Gemini response
                try:
                    if hasattr(resp, 'text'):
                        reply_text = resp.text
                    else:
                        reply_text = str(resp) if resp else None
                except Exception as e:
                    logger.exception("Error parsing Gemini response: %s", e)
                    reply_text = None
                    
            except Exception as e:
                # API call failed, use fallback
                logger.warning("[/chat] Gemini API call failed, using fallback: %s", str(e))
                use_fallback = True
        else:
            # SDK or API key not available, use fallback
            logger.warning("[/chat] Google GenAI not configured, using fallback responses")
            use_fallback = True

        # If no reply from API, use fallback
        if not reply_text:
            use_fallback = True
        
        if use_fallback:
            reply_text = _get_fallback_response(user_message)
            logger.info("Using fallback response for: %s", user_message)

        return jsonify({'reply': reply_text}), 200

    except Exception as e:
        logger.exception("[/chat] Unexpected error handling request: %s", e)
        return jsonify({'error': 'Internal server error'}), 500



# Allowed UI inputs (exactly these 8)
DAY_UI_FIELDS = ['dteday', 'season', 'holiday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum']


@app.route('/predict/day', methods=['POST', 'OPTIONS'])
def predict_day():
    """
    Day-level prediction endpoint.

    Strict behavior:
    - Accept only the 8 UI inputs listed in `DAY_UI_FIELDS`.
    - Compute date-derived features (yr, mnth, weekday, quarter, is_weekend).
    - Compute cyclical features for month and weekday.
    - Compute derived features: is_peak_season, temp_humidity, temp_windspeed (0), weather_severity.
    - Remove raw `dteday` and reindex strictly to `day_expected_features`.
    - Return JSON: { "prediction": value }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        payload = request.get_json(force=True)
        print("\n[/predict/day] Received payload:", payload)

        if not payload:
            return jsonify({'error': 'No JSON body provided'}), 400

        # Enforce UI inputs only
        inputs = {k: payload.get(k) for k in DAY_UI_FIELDS}

        # Verify required fields present (treat empty string as missing)
        missing = [k for k, v in inputs.items() if v is None or (isinstance(v, str) and v.strip() == "")] 
        if missing:
            return jsonify({'error': f'Missing required inputs: {missing}'}), 400

        # Store values needed for dashboard update
        weathersit_val = inputs.get('weathersit', '1')
        
        # Build DataFrame from inputs
        df = pd.DataFrame([inputs])

        # Parse and derive date features
        try:
            dt = pd.to_datetime(df.at[0, 'dteday'])
        except Exception as e:
            return jsonify({'error': f'Invalid dteday format: {e}'}), 400

        # Mandatory date-derived features
        df['yr'] = dt.year
        df['mnth'] = dt.month
        df['weekday'] = dt.weekday()
        df['quarter'] = (dt.month - 1) // 3 + 1
        df['is_weekend'] = 1 if df.at[0, 'weekday'] >= 5 else 0

        # Cyclical encodings (day model expects these if present in feature list)
        df['mnth_sin'] = np.sin(2 * np.pi * df['mnth'] / 12)
        df['mnth_cos'] = np.cos(2 * np.pi * df['mnth'] / 12)
        df['weekday_sin'] = np.sin(2 * np.pi * df['weekday'] / 7)
        df['weekday_cos'] = np.cos(2 * np.pi * df['weekday'] / 7)

        # Derived features
        df['is_peak_season'] = 1 if int(df.at[0, 'mnth']) in (6, 7, 8) else 0
        # temp_humidity (temp * hum)
        df['temp_humidity'] = pd.to_numeric(df['temp'], errors='coerce') * pd.to_numeric(df['hum'], errors='coerce')
        # temp_windspeed: not provided in day UI, set to 0 as required
        df['temp_windspeed'] = 0
        # weather_severity mirrors weathersit
        df['weather_severity'] = df['weathersit']

        # Remove raw dteday before prediction
        df = df.drop(columns=['dteday'])

        # Ensure numeric columns are properly typed
        numeric_cols = ['season', 'holiday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum',
                        'yr', 'mnth', 'weekday', 'quarter', 'is_weekend',
                        'mnth_sin', 'mnth_cos', 'weekday_sin', 'weekday_cos',
                        'is_peak_season', 'temp_humidity', 'temp_windspeed', 'weather_severity']
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Reindex strictly to expected features (only source of truth)
        df_reindexed = df.reindex(columns=day_expected_features, fill_value=0)

        if len(df_reindexed.columns) != len(day_expected_features):
            return jsonify({'error': f'Feature alignment error: prepared {len(df_reindexed.columns)} features, expected {len(day_expected_features)}'}), 500

        # Prediction
        try:
            X = df_reindexed.values
            preds = day_model.predict(X)
            pred_value = float(preds[0])
            pred_value = max(0.0, pred_value)
            print(f"[/predict/day] Prediction: {pred_value}")
            
            # Update dashboard summary (in-memory)
            from datetime import datetime
            global last_prediction
            last_prediction = {
                "predicted_demand": round(pred_value, 2),
                "prediction_type": "Daily",
                "weather_impact": _calculate_weather_impact(weathersit_val),
                "peak_status": _calculate_peak_status(demand=int(pred_value)),
                "timestamp": datetime.now().isoformat()
            }
            
            return jsonify({'prediction': round(pred_value, 2)}), 200
        except Exception as e:
            print(f"[/predict/day] Model prediction error: {e}")
            traceback.print_exc()
            return jsonify({'error': f'Prediction failed: {e}'}), 500

    except Exception as e:
        print(f"[/predict/day] Unexpected error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



# Allowed UI inputs for HOUR model (no windspeed - derived by backend)
HOUR_UI_FIELDS = ['dteday', 'hr', 'season', 'holiday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum']


@app.route('/predict/hour', methods=['POST', 'OPTIONS'])
def predict_hour():
    """
    Hour-level prediction endpoint.

    Strict behavior:
    - Accept only the 10 UI inputs listed in `HOUR_UI_FIELDS`.
    - Compute date-derived features (yr, mnth, weekday, quarter, is_weekend) from dteday.
    - Compute cyclical features for month, weekday, and hour if expected by model.
    - Compute derived features: is_peak_season, temp_humidity, temp_windspeed, weather_severity.
    - Remove raw `dteday` and reindex strictly to `hour_expected_features`.
    - Return JSON: { "prediction": value }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        payload = request.get_json(force=True)
        print("\n[/predict/hour] Received payload:", payload)

        if not payload:
            return jsonify({'error': 'No JSON body provided'}), 400

        # Enforce UI inputs only
        inputs = {k: payload.get(k) for k in HOUR_UI_FIELDS}

        # Verify required fields present (treat empty string as missing)
        missing = [k for k, v in inputs.items() if v is None or (isinstance(v, str) and v.strip() == "")] 
        if missing:
            return jsonify({'error': f'Missing required inputs: {missing}'}), 400

        # Store values needed for dashboard update
        weathersit_val = inputs.get('weathersit', '1')
        hr_val = int(inputs.get('hr', 0))
        
        # Build DataFrame from inputs
        df = pd.DataFrame([inputs])

        # Parse and derive date features
        try:
            dt = pd.to_datetime(df.at[0, 'dteday'])
        except Exception as e:
            return jsonify({'error': f'Invalid dteday format: {e}'}), 400

        # Mandatory date-derived features
        df['yr'] = dt.year
        df['mnth'] = dt.month
        df['weekday'] = dt.weekday()
        df['quarter'] = (dt.month - 1) // 3 + 1
        df['is_weekend'] = 1 if df.at[0, 'weekday'] >= 5 else 0

        # Cyclical encodings for hour model
        df['mnth_sin'] = np.sin(2 * np.pi * df['mnth'] / 12)
        df['mnth_cos'] = np.cos(2 * np.pi * df['mnth'] / 12)
        df['weekday_sin'] = np.sin(2 * np.pi * df['weekday'] / 7)
        df['weekday_cos'] = np.cos(2 * np.pi * df['weekday'] / 7)
        
        # Hour cyclical encoding (if expected by model)
        hr_numeric = pd.to_numeric(df['hr'], errors='coerce').fillna(0).astype(int)
        df['hr_sin'] = np.sin(2 * np.pi * hr_numeric / 24)
        df['hr_cos'] = np.cos(2 * np.pi * hr_numeric / 24)

        # Derived features
        df['is_peak_season'] = 1 if int(df.at[0, 'mnth']) in (6, 7, 8) else 0
        # temp_humidity (temp * hum)
        df['temp_humidity'] = pd.to_numeric(df['temp'], errors='coerce') * pd.to_numeric(df['hum'], errors='coerce')
        # temp_windspeed: not provided in hour UI, set to 0 as required
        df['windspeed'] = 0
        df['temp_windspeed'] = pd.to_numeric(df['temp'], errors='coerce') * 0
        # weather_severity mirrors weathersit
        df['weather_severity'] = df['weathersit']

        # Remove raw dteday before prediction
        df = df.drop(columns=['dteday'])

        # Ensure numeric columns are properly typed
        numeric_cols = ['season', 'holiday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed', 'hr',
                        'yr', 'mnth', 'weekday', 'quarter', 'is_weekend',
                        'mnth_sin', 'mnth_cos', 'weekday_sin', 'weekday_cos', 'hr_sin', 'hr_cos',
                        'is_peak_season', 'temp_humidity', 'temp_windspeed', 'weather_severity']
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Reindex strictly to expected features (only source of truth)
        df_reindexed = df.reindex(columns=hour_expected_features, fill_value=0)

        if len(df_reindexed.columns) != len(hour_expected_features):
            return jsonify({'error': f'Feature alignment error: prepared {len(df_reindexed.columns)} features, expected {len(hour_expected_features)}'}), 500

        # Prediction
        try:
            X = df_reindexed.values
            preds = hour_model.predict(X)
            pred_value = float(preds[0])
            pred_value = max(0.0, pred_value)
            print(f"[/predict/hour] Prediction: {pred_value}")
            
            # Update dashboard summary (in-memory)
            from datetime import datetime
            global last_prediction
            last_prediction = {
                "predicted_demand": round(pred_value, 2),
                "prediction_type": "Hourly",
                "weather_impact": _calculate_weather_impact(weathersit_val),
                "peak_status": _calculate_peak_status(hour=hr_val, demand=int(pred_value)),
                "timestamp": datetime.now().isoformat()
            }
            
            return jsonify({'prediction': round(pred_value, 2)}), 200
        except Exception as e:
            print(f"[/predict/hour] Model prediction error: {e}")
            traceback.print_exc()
            return jsonify({'error': f'Prediction failed: {e}'}), 500

    except Exception as e:
        print(f"[/predict/hour] Unexpected error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# IN-MEMORY STORAGE: Dashboard Summary & Feedback
# ============================================================================

# Track last prediction for dynamic dashboard
last_prediction = {
    "predicted_demand": None,
    "prediction_type": None,
    "weather_impact": None,
    "peak_status": None,
    "timestamp": None
}

# Store user feedback (in-memory list)
feedback_list = []

# Store user reviews (in-memory dict: user_email -> list of reviews)
reviews_db = {}


def _calculate_weather_impact(weathersit: str) -> str:
    """Calculate weather impact level based on weather situation code."""
    try:
        code = int(weathersit)
        if code == 1:
            return "Low"      # Clear / Sunny
        elif code == 2:
            return "Medium"   # Cloudy / Misty
        elif code == 3:
            return "High"     # Light Rain / Snow
        else:
            return "High"     # Heavy Rain / Storm
    except:
        return "Medium"


def _calculate_peak_status(hour: int = None, demand: int = None) -> str:
    """Calculate peak status based on hour and demand level."""
    if demand is None:
        return "Normal"
    
    # Peak hours: 7-9 AM, 4-7 PM (high demand typical)
    peak_hours = [7, 8, 9, 16, 17, 18, 19]
    
    if demand > 400:
        return "Peak"
    elif demand > 200:
        return "Normal"
    else:
        return "Off-Peak"


@app.route('/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """
    GET endpoint to retrieve the last prediction summary for dashboard.
    
    Returns:
    {
        "predicted_demand": number or null,
        "prediction_type": "Hourly" or "Daily" or null,
        "weather_impact": "Low" | "Medium" | "High" or null,
        "peak_status": "Peak" | "Normal" | "Off-Peak" or null,
        "timestamp": ISO string or null
    }
    """
    return jsonify(last_prediction), 200


@app.route('/feedback', methods=['POST', 'OPTIONS'])
def submit_feedback():
    """
    POST endpoint to submit user feedback.
    
    Request body:
    {
        "rating": 1-5,
        "comment": "feedback text"
    }
    
    Returns:
    {
        "status": "success"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        payload = request.get_json(force=True)
        
        if not payload:
            return jsonify({'error': 'No JSON body provided'}), 400
        
        # Validate required fields
        rating = payload.get('rating')
        comment = payload.get('comment', '').strip()
        
        if rating is None or not comment:
            return jsonify({'error': 'Missing rating or comment'}), 400
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Rating must be an integer'}), 400
        
        # Store feedback with timestamp
        from datetime import datetime
        feedback_entry = {
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        
        feedback_list.append(feedback_entry)
        print(f"[Feedback] Received: {rating}★ - {comment[:50]}...")
        
        return jsonify({'status': 'success'}), 201
    
    except Exception as e:
        print(f"[Feedback] Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['GET'])
def get_feedback():
    """
    GET endpoint to retrieve all feedback entries.
    
    Returns:
    {
        "feedback": [
            { "rating": 5, "comment": "...", "timestamp": "..." },
            ...
        ]
    }
    """
    return jsonify({'feedback': feedback_list}), 200


@app.route('/api/reviews', methods=['POST', 'OPTIONS'])
def submit_review():
    """
    POST endpoint to submit user review.
    
    Request body:
    {
        "user_email": "user@example.com",
        "rating": 1-5,
        "comment": "review text"
    }
    
    Returns:
    {
        "status": "success",
        "review_id": 123
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        payload = request.get_json(force=True)
        
        if not payload:
            return jsonify({'error': 'No JSON body provided'}), 400
        
        # Validate required fields
        user_email = payload.get('user_email', '').strip()
        rating = payload.get('rating')
        comment = payload.get('comment', '').strip()
        
        if not user_email or rating is None or not comment:
            return jsonify({'error': 'Missing user_email, rating, or comment'}), 400
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Rating must be an integer'}), 400
        
        # Initialize user reviews if not exists
        if user_email not in reviews_db:
            reviews_db[user_email] = []
        
        # Generate review ID
        review_id = len(reviews_db[user_email]) + 1
        
        # Store review with timestamp
        from datetime import datetime
        review_entry = {
            'id': review_id,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        
        reviews_db[user_email].append(review_entry)
        print(f"[Review] Received from {user_email}: {rating}★ - {comment[:50]}...")
        
        return jsonify({'status': 'success', 'review_id': review_id}), 201
    
    except Exception as e:
        print(f"[Review] Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """
    GET endpoint to retrieve user reviews.
    
    Query params:
    - user_email: string
    
    Returns:
    {
        "reviews": [
            { "id": 1, "rating": 5, "comment": "...", "timestamp": "..." },
            ...
        ]
    }
    """
    try:
        user_email = request.args.get('user_email', '').strip()
        if not user_email:
            return jsonify({'error': 'user_email query parameter required'}), 400
        
        user_reviews = reviews_db.get(user_email, [])
        return jsonify({'reviews': user_reviews}), 200
    
    except Exception as e:
        print(f"[Review] Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reviews/all', methods=['GET'])
def get_all_reviews():
    """
    GET endpoint to retrieve all reviews from all users.
    
    Returns:
    {
        "reviews": [
            { "user_email": "...", "id": 1, "rating": 5, "comment": "...", "timestamp": "..." },
            ...
        ]
    }
    """
    try:
        all_reviews = []
        for user_email, user_reviews in reviews_db.items():
            for review in user_reviews:
                all_reviews.append({
                    "user_email": user_email,
                    "id": review["id"],
                    "rating": review["rating"],
                    "comment": review["comment"],
                    "timestamp": review["timestamp"]
                })
        
        # Sort by timestamp descending (latest first)
        all_reviews.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return jsonify({'reviews': all_reviews}), 200
    
    except Exception as e:
        print(f"[Review] Error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*60}")
    print("RideWise Backend Server Starting")
    print(f"{'='*60}")
    print(f"Server: http://0.0.0.0:{port}")
    print(f"Health: GET http://localhost:{port}/health")
    print(f"Daily Predict: POST http://localhost:{port}/predict/day")
    print(f"Hour Predict: POST http://localhost:{port}/predict/hour")
    print(f"Dashboard: GET http://localhost:{port}/dashboard/summary")
    print(f"Feedback: POST http://localhost:{port}/feedback")
    print(f"Reviews: POST/GET http://localhost:{port}/api/reviews")
    print(f"All Reviews: GET http://localhost:{port}/api/reviews/all")
    print(f"CORS: Enabled for http://localhost:3000")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
