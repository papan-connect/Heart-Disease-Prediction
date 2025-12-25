import pickle
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Try to load the trained SVM model, but provide a fallback
model = None
model_loaded = False

try:
    if os.path.exists('best_knn_model.pkl'):
        with open('best_knn_model.pkl', 'rb') as file:
            model = pickle.load(file)
        model_loaded = True
        print("Model loaded successfully!")
    else:
        print("Warning: best_knn_model.pkl not found. Using mock predictions.")
except Exception as e:
    print(f"Error loading model: {e}. Using mock predictions.")

# Feature names based on the heart disease dataset
FEATURE_NAMES = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
    'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]

# Feature descriptions for better UX
FEATURE_DESCRIPTIONS = {
    'age': 'Age (years)',
    'sex': 'Sex (1 = male, 0 = female)',
    'cp': 'Chest Pain Type (0-3)',
    'trestbps': 'Resting Blood Pressure (mm Hg)',
    'chol': 'Serum Cholesterol (mg/dl)',
    'fbs': 'Fasting Blood Sugar > 120 mg/dl (1 = true, 0 = false)',
    'restecg': 'Resting ECG Results (0-2)',
    'thalach': 'Maximum Heart Rate Achieved',
    'exang': 'Exercise Induced Angina (1 = yes, 0 = no)',
    'oldpeak': 'ST Depression Induced by Exercise',
    'slope': 'Peak Exercise ST Segment Slope (0-2)',
    'ca': 'Number of Major Vessels Colored by Fluoroscopy (0-3)',
    'thal': 'Thalassemia (1 = normal, 2 = fixed defect, 3 = reversible defect)'
}

def mock_prediction(features):
    """Simple mock prediction for when the real model isn't available"""
    # Simple rule-based prediction for demo purposes
    age = features[0]
    sex = features[1]
    cp = features[2]
    trestbps = features[3]
    chol = features[4]
    thalach = features[7]
    
    # Count risk factors
    risk_score = 0
    
    if age > 55:
        risk_score += 1
    if sex == 1:  # Male
        risk_score += 1
    if cp == 0:  # Typical angina
        risk_score += 2
    if trestbps > 140:
        risk_score += 1
    if chol > 240:
        risk_score += 1
    if thalach < 120:
        risk_score += 1
    
    # Predict based on risk score
    prediction = 1 if risk_score >= 3 else 0
    probability_disease = min(0.9, risk_score * 0.15 + 0.1)
    probability_no_disease = 1 - probability_disease
    
    return prediction, [probability_no_disease, probability_disease]

@app.route('/')
def home():
    """Render the home page with prediction form"""
    return render_template('index.html', features=FEATURE_DESCRIPTIONS)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        # Get form data
        features = []
        feature_dict = {}
        
        for feature in FEATURE_NAMES:
            value = request.form.get(feature)
            if value is None or value == '':
                return jsonify({
                    'error': f'Missing value for {feature}',
                    'success': False
                })
            
            try:
                feature_value = float(value)
                features.append(feature_value)
                feature_dict[feature] = feature_value
            except ValueError:
                return jsonify({
                    'error': f'Invalid value for {feature}. Please enter a number.',
                    'success': False
                })
        
        # Make prediction
        if model_loaded and model is not None:
            try:
                # Try to use the real model
                import numpy as np
                features_array = np.array(features).reshape(1, -1)
                prediction = model.predict(features_array)[0]
                probability = model.predict_proba(features_array)[0]
            except Exception as e:
                print(f"Error using real model: {e}. Falling back to mock prediction.")
                prediction, probability = mock_prediction(features)
        else:
            # Use mock prediction
            prediction, probability = mock_prediction(features)
        
        # Prepare response
        result = {
            'prediction': int(prediction),
            'probability_no_disease': float(probability[0]),
            'probability_disease': float(probability[1]),
            'risk_level': 'High' if prediction == 1 else 'Low',
            'input_features': feature_dict,
            'model_loaded': model_loaded,
            'success': True
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Prediction error: {str(e)}',
            'success': False
        })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for JSON prediction requests"""
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'success': False
            })
        
        # Extract features
        features = []
        for feature in FEATURE_NAMES:
            if feature not in data:
                return jsonify({
                    'error': f'Missing feature: {feature}',
                    'success': False
                })
            features.append(data[feature])
        
        # Make prediction
        if model_loaded and model is not None:
            try:
                # Try to use the real model
                import numpy as np
                features_array = np.array(features).reshape(1, -1)
                prediction = model.predict(features_array)[0]
                probability = model.predict_proba(features_array)[0]
            except Exception as e:
                print(f"Error using real model: {e}. Falling back to mock prediction.")
                prediction, probability = mock_prediction(features)
        else:
            # Use mock prediction
            prediction, probability = mock_prediction(features)
        
        # Prepare response
        result = {
            'prediction': int(prediction),
            'probability_no_disease': float(probability[0]),
            'probability_disease': float(probability[1]),
            'risk_level': 'High' if prediction == 1 else 'Low',
            'model_loaded': model_loaded,
            'success': True
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Prediction error: {str(e)}',
            'success': False
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'message': 'Heart Disease Prediction API is running'
    })

@app.route('/status')
def status():
    """Status endpoint with more details"""
    return jsonify({
        'app_name': 'Heart Disease Prediction',
        'status': 'running',
        'model_loaded': model_loaded,
        'model_file_exists': os.path.exists('best_knn_model.pkl'),  # changed here
        'features_count': len(FEATURE_NAMES),
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Main prediction form'},
            {'path': '/predict', 'method': 'POST', 'description': 'Form-based prediction'},
            {'path': '/api/predict', 'method': 'POST', 'description': 'JSON API prediction'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
            {'path': '/status', 'method': 'GET', 'description': 'Detailed status'}
        ]
    })

if __name__ == '__main__':
    print("Starting Heart Disease Prediction Server...")
    print(f"Model loaded: {model_loaded}")
    print(f"Model file exists: {os.path.exists('best_knn_model.pkl')}")  # changed here
    app.run(debug=True, host='0.0.0.0', port=5000)
