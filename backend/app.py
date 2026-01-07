from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the models
# Get the absolute path to the backend directory, then go up one level to find saved_models
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
MODEL_DIR = os.path.join(PROJECT_ROOT, 'saved_models')
HOUR_MODEL_PATH = os.path.join(MODEL_DIR, 'best_hour_model.pkl')
DAY_MODEL_PATH = os.path.join(MODEL_DIR, 'best_day_model.pkl')

print(f"🔍 Looking for models in: {MODEL_DIR}")
print(f"🔍 Hour model path: {HOUR_MODEL_PATH}")
print(f"🔍 Day model path: {DAY_MODEL_PATH}")
print(f"🔍 Hour model exists: {os.path.exists(HOUR_MODEL_PATH)}")
print(f"🔍 Day model exists: {os.path.exists(DAY_MODEL_PATH)}")

try:
    if os.path.exists(HOUR_MODEL_PATH):
        with open(HOUR_MODEL_PATH, 'rb') as f:
            hour_model = pickle.load(f)
        print(f"✓ Loaded hourly model from {HOUR_MODEL_PATH}")
    else:
        print(f"✗ Hour model file not found at {HOUR_MODEL_PATH}")
        hour_model = None
except Exception as e:
    print(f"✗ Error loading hourly model: {e}")
    import traceback
    traceback.print_exc()
    hour_model = None

try:
    if os.path.exists(DAY_MODEL_PATH):
        print(f"Attempting to load daily model from {DAY_MODEL_PATH}...")
        with open(DAY_MODEL_PATH, 'rb') as f:
            day_model = pickle.load(f)
        print(f"✓ Successfully loaded daily model from {DAY_MODEL_PATH}")
        print(f"  Model type: {type(day_model)}")
    else:
        print(f"✗ Day model file not found at {DAY_MODEL_PATH}")
        day_model = None
except ModuleNotFoundError as e:
    print(f"✗ Missing required module for daily model: {e}")
    print(f"  Please install the missing module to use daily predictions.")
    import traceback
    traceback.print_exc()
    day_model = None
except Exception as e:
    print(f"✗ Error loading daily model: {e}")
    print(f"  Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    day_model = None


def encode_features(inputs, is_hourly=True):
    """Convert frontend inputs to model features with proper encoding"""
    import math
    features = []
    
    # Get base values
    season = inputs.get('season', 'spring')
    weather = inputs.get('weather', 'clear')
    temp = float(inputs.get('temperature', 20))
    humidity = float(inputs.get('humidity', 50))
    working_day = 1 if inputs.get('workingDay', 'yes') == 'yes' else 0
    
    # 1-4: Season one-hot encoding (4 features)
    season_map = {'spring': [1, 0, 0, 0], 'summer': [0, 1, 0, 0], 'fall': [0, 0, 1, 0], 'winter': [0, 0, 0, 1]}
    features.extend(season_map.get(season, [1, 0, 0, 0]))
    
    # 5-8: Weather one-hot encoding (4 features)
    weather_map = {'clear': [1, 0, 0, 0], 'cloudy': [0, 1, 0, 0], 'light_rain': [0, 0, 1, 0], 'heavy_rain': [0, 0, 0, 1]}
    features.extend(weather_map.get(weather, [1, 0, 0, 0]))
    
    # 9: Temperature (raw)
    features.append(temp)
    
    # 10: Temperature squared
    features.append(temp ** 2)
    
    # 11: Temperature normalized (assuming range 0-40)
    features.append(temp / 40.0)
    
    # 12: Humidity (raw)
    features.append(humidity)
    
    # 13: Humidity squared
    features.append(humidity ** 2)
    
    # 14: Humidity normalized
    features.append(humidity / 100.0)
    
    # 15: Working day
    features.append(working_day)
    
    if is_hourly:
        hour = int(inputs.get('hour', 0))
        
        # 16: Hour (raw)
        features.append(hour)
        
        # 17-18: Hour cyclical encoding (sin, cos)
        features.append(math.sin(2 * math.pi * hour / 24))
        features.append(math.cos(2 * math.pi * hour / 24))
        
        # 19: Hour squared
        features.append(hour ** 2)
        
        # 20: Hour normalized
        features.append(hour / 23.0)
        
        # 21-22: Temperature * Hour interaction
        features.append(temp * hour)
        features.append(temp * hour / 100.0)
        
        # 23-24: Humidity * Hour interaction
        features.append(humidity * hour)
        features.append(humidity * hour / 100.0)
        
        # 25: Working day * Hour interaction
        features.append(working_day * hour)
        
        # 26: Temperature * Humidity interaction
        features.append(temp * humidity / 100.0)
    else:
        month = int(inputs.get('month', 1))
        weekday = int(inputs.get('weekday', 0))
        
        # 16: Month (raw)
        features.append(month)
        
        # 17-18: Month cyclical encoding
        features.append(math.sin(2 * math.pi * month / 12))
        features.append(math.cos(2 * math.pi * month / 12))
        
        # 19: Weekday (raw)
        features.append(weekday)
        
        # 20-21: Weekday cyclical encoding
        features.append(math.sin(2 * math.pi * weekday / 7))
        features.append(math.cos(2 * math.pi * weekday / 7))
        
        # 22: Month squared
        features.append(month ** 2)
        
        # 23: Temperature * Month interaction
        features.append(temp * month)
        
        # 24: Humidity * Month interaction
        features.append(humidity * month)
        
        # 25: Working day * Weekday interaction
        features.append(working_day * weekday)
        
        # 26: Temperature * Humidity interaction
        features.append(temp * humidity / 100.0)
    
    feature_array = np.array(features, dtype=np.float32).reshape(1, -1)
    print(f"Generated {len(features)} features for {'hourly' if is_hourly else 'daily'} prediction")
    return feature_array


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API information"""
    return jsonify({
        'message': 'RideWise Insights API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'predict': '/api/predict (POST)'
        },
        'status': 'running'
    })


@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'RideWise Insights API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/health': 'Check server health and model status',
            'POST /api/predict': 'Get bike demand prediction'
        },
        'models': {
            'hourly': hour_model is not None,
            'daily': day_model is not None
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'hour_model_loaded': hour_model is not None,
        'day_model_loaded': day_model is not None
    })


@app.route('/api/predict', methods=['GET', 'POST'])
def predict():
    """Predict bike demand based on input features"""
    # Handle GET request - return endpoint information
    if request.method == 'GET':
        return jsonify({
            'message': 'Prediction endpoint - use POST method',
            'method': 'POST',
            'endpoint': '/api/predict',
            'required_fields': {
                'isHourly': 'boolean - true for hourly, false for daily',
                'inputs': {
                    'season': 'string - spring, summer, fall, winter',
                    'weather': 'string - clear, cloudy, light_rain, heavy_rain',
                    'temperature': 'number - temperature in Celsius',
                    'humidity': 'number - humidity percentage (0-100)',
                    'workingDay': 'string - yes or no',
                    'hour': 'number (0-23) - required if isHourly is true',
                    'month': 'number (1-12) - required if isHourly is false',
                    'weekday': 'number (0-6) - required if isHourly is false'
                }
            },
            'example_request': {
                'isHourly': True,
                'inputs': {
                    'season': 'summer',
                    'hour': '8',
                    'weather': 'clear',
                    'temperature': '25',
                    'humidity': '60',
                    'workingDay': 'yes'
                }
            }
        })
    
    # Handle POST request - make prediction
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        is_hourly = data.get('isHourly', True)
        
        # Select appropriate model
        model = hour_model if is_hourly else day_model
        
        if model is None:
            model_name = 'hourly' if is_hourly else 'daily'
            return jsonify({
                'error': f'{model_name} model not loaded',
                'prediction': None
            }), 500
        
        # Prepare features
        features = encode_features(data.get('inputs', {}), is_hourly=is_hourly)
        
        # Debug: Check feature shape
        print(f"Feature shape: {features.shape}, Expected: Check model")
        
        # Make prediction
        try:
            prediction = model.predict(features)[0]
        except ValueError as e:
            # If shape mismatch, provide helpful error
            if "feature" in str(e).lower() or "shape" in str(e).lower():
                return jsonify({
                    'error': f'Feature shape mismatch. Generated {features.shape[1]} features. Model expects different number. Error: {str(e)}',
                    'feature_count': int(features.shape[1]),
                    'prediction': None,
                    'success': False
                }), 400
            raise
        
        # Ensure prediction is non-negative
        prediction = max(0, float(prediction))
        
        return jsonify({
            'prediction': round(prediction, 2),
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'prediction': None,
            'success': False
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"\n{'='*50}")
    print("🚀 RideWise Backend Server Starting...")
    print(f"{'='*50}")
    print(f"📍 Server running on http://localhost:{port}")
    print(f"📍 Health check: http://localhost:{port}/api/health")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=port, debug=True)

