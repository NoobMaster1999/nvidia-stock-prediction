from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
from flask_cors import cross_origin

prediction_bp = Blueprint('prediction', __name__)

# Load the trained model and scaler
model_path = os.path.join(os.path.dirname(__file__), '..', 'stock_prediction_model.pkl')
scaler_path = os.path.join(os.path.dirname(__file__), '..', 'scaler.pkl')
data_path = os.path.join(os.path.dirname(__file__), '..', 'NVDA_historical_data.csv')

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Load historical data for getting recent prices
df = pd.read_csv(data_path, skiprows=[1, 2], index_col=0, parse_dates=True)

@prediction_bp.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    try:
        # Get the last 5 days of closing prices
        last_5_prices = df['Close'].tail(5).values[::-1]  # Reverse to get in correct order
        
        # Scale the features
        features = scaler.transform([last_5_prices])
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        return jsonify({
            'prediction': float(prediction),
            'last_5_prices': last_5_prices.tolist(),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@prediction_bp.route('/historical', methods=['GET'])
@cross_origin()
def get_historical_data():
    try:
        # Get last 30 days of data
        recent_data = df.tail(30)
        
        data = []
        for date, row in recent_data.iterrows():
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'close': float(row['Close']),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'volume': int(float(row['Volume']))
            })
        
        return jsonify({
            'data': data,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@prediction_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    try:
        current_price = float(df['Close'].iloc[-1])
        previous_price = float(df['Close'].iloc[-2])
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100
        
        # Calculate some basic statistics
        recent_30_days = df.tail(30)
        high_30d = float(recent_30_days['High'].max())
        low_30d = float(recent_30_days['Low'].min())
        avg_volume_30d = int(float(recent_30_days['Volume'].mean()))
        
        return jsonify({
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent,
            'high_30d': high_30d,
            'low_30d': low_30d,
            'avg_volume_30d': avg_volume_30d,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

