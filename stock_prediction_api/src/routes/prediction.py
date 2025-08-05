from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
from flask_cors import cross_origin
from scipy.stats import norm


prediction_bp = Blueprint('prediction', __name__)

# Load the trained model and scaler
model_path = os.path.join(os.path.dirname(__file__), '..', 'stock_prediction_model.pkl')
scaler_path = os.path.join(os.path.dirname(__file__), '..', 'scaler.pkl')
data_path = os.path.join(os.path.dirname(__file__), '..', 'NVDA_historical_data.csv')

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Load historical data for getting recent prices
df = pd.read_csv(data_path, skiprows=[1, 2], index_col=0, parse_dates=True)

def calculate_volatility(prices, window=30):
    """Calculate historical volatility using daily returns"""
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns.std() * np.sqrt(252)  # Annualized volatility

def monte_carlo_simulation(current_price, volatility, drift, days, simulations=1000):
    """
    Monte Carlo simulation for stock price prediction
    """
    dt = 1/252  # Daily time step (assuming 252 trading days per year)

    # Generate random price paths
    price_paths = np.zeros((simulations, days + 1))
    price_paths[:, 0] = current_price

    for t in range(1, days + 1):
        random_shock = np.random.normal(0, 1, simulations)
        price_paths[:, t] = price_paths[:, t-1] * np.exp(
            (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * random_shock
        )

    # Calculate statistics
    final_prices = price_paths[:, -1]

    return {
        'mean_price': float(np.mean(final_prices)),
        'median_price': float(np.median(final_prices)),
        'std_price': float(np.std(final_prices)),
        'confidence_95_lower': float(np.percentile(final_prices, 2.5)),
        'confidence_95_upper': float(np.percentile(final_prices, 97.5)),
        'confidence_68_lower': float(np.percentile(final_prices, 16)),
        'confidence_68_upper': float(np.percentile(final_prices, 84)),
        'price_paths': price_paths[:min(100, simulations)].tolist()  # Return first 100 paths for visualization
    }

def black_scholes_call(S, K, T, r, sigma):
    """
    Calculate Black-Scholes call option price
    S: Current stock price
    K: Strike price
    T: Time to expiration (in years)
    r: Risk-free rate
    sigma: Volatility
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

def black_scholes_put(S, K, T, r, sigma):
    """
    Calculate Black-Scholes put option price
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

def calculate_greeks(S, K, T, r, sigma):
    """
    Calculate option Greeks
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Delta
    call_delta = norm.cdf(d1)
    put_delta = call_delta - 1

    # Gamma
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

    # Theta
    call_theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                  - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    put_theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

    # Vega
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100

    return {
        'call_delta': float(call_delta),
        'put_delta': float(put_delta),
        'gamma': float(gamma),
        'call_theta': float(call_theta),
        'put_theta': float(put_theta),
        'vega': float(vega)
    }

@prediction_bp.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    try:
        data = request.get_json() or {}
        method = data.get('method', 'ml')  # Default to original ML method

        # Get the last 5 days of closing prices
        last_5_prices = df['Close'].tail(5).values[::-1]  # Reverse to get in correct order
        current_price = float(df['Close'].iloc[-1])

        if method == 'ml':
            # Original ML prediction
            features = scaler.transform([last_5_prices])
            prediction = model.predict(features)[0]

            return jsonify({
                'method': 'machine_learning',
                'prediction': float(prediction),
                'last_5_prices': last_5_prices.tolist(),
                'status': 'success'
            })

        elif method == 'monte_carlo':
            # Monte Carlo simulation
            days = data.get('days', 30)  # Default 30 days
            simulations = data.get('simulations', 1000)  # Default 1000 simulations

            # Calculate historical volatility and drift
            recent_prices = df['Close'].tail(60)  # Use last 60 days for calculations
            volatility = calculate_volatility(recent_prices)
            returns = np.log(recent_prices / recent_prices.shift(1)).dropna()
            drift = returns.mean() * 252  # Annualized drift

            mc_results = monte_carlo_simulation(current_price, volatility, drift, days, simulations)

            return jsonify({
                'method': 'monte_carlo',
                'current_price': current_price,
                'days': days,
                'simulations': simulations,
                'volatility': float(volatility),
                'drift': float(drift),
                'results': mc_results,
                'status': 'success'
            })

        elif method == 'black_scholes':
            # Black-Scholes option pricing
            strike_price = data.get('strike_price', current_price)  # At-the-money by default
            days_to_expiry = data.get('days_to_expiry', 30)  # Default 30 days
            risk_free_rate = data.get('risk_free_rate', 0.05)  # Default 5%

            # Calculate volatility
            recent_prices = df['Close'].tail(60)
            volatility = calculate_volatility(recent_prices)

            T = days_to_expiry / 365  # Convert to years

            call_price = black_scholes_call(current_price, strike_price, T, risk_free_rate, volatility)
            put_price = black_scholes_put(current_price, strike_price, T, risk_free_rate, volatility)
            greeks = calculate_greeks(current_price, strike_price, T, risk_free_rate, volatility)

            return jsonify({
                'method': 'black_scholes',
                'current_price': current_price,
                'strike_price': strike_price,
                'days_to_expiry': days_to_expiry,
                'risk_free_rate': risk_free_rate,
                'volatility': float(volatility),
                'call_price': float(call_price),
                'put_price': float(put_price),
                'greeks': greeks,
                'status': 'success'
            })

        else:
            return jsonify({
                'error': 'Invalid method. Choose from: ml, monte_carlo, black_scholes',
                'status': 'error'
            }), 400

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
                'date': pd.Timestamp(date).strftime('%Y-%m-%d'),
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

        # Add volatility calculation
        volatility = calculate_volatility(df['Close'].tail(60))

        return jsonify({
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent,
            'high_30d': high_30d,
            'low_30d': low_30d,
            'avg_volume_30d': avg_volume_30d,
            'volatility': float(volatility),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@prediction_bp.route('/methods', methods=['GET'])
@cross_origin()
def get_available_methods():
    """Return information about available prediction methods"""
    return jsonify({
        'methods': {
            'ml': {
                'name': 'Machine Learning',
                'description': 'Uses your trained model with last 5 closing prices',
                'parameters': []
            },
            'monte_carlo': {
                'name': 'Monte Carlo Simulation',
                'description': 'Simulates multiple price paths using geometric Brownian motion',
                'parameters': [
                    {'name': 'days', 'type': 'integer', 'default': 30, 'description': 'Number of days to simulate'},
                    {'name': 'simulations', 'type': 'integer', 'default': 1000, 'description': 'Number of simulation runs'}
                ]
            },
            'black_scholes': {
                'name': 'Black-Scholes Option Pricing',
                'description': 'Calculates option prices and Greeks using Black-Scholes formula',
                'parameters': [
                    {'name': 'strike_price', 'type': 'float', 'default': 'current_price', 'description': 'Option strike price'},
                    {'name': 'days_to_expiry', 'type': 'integer', 'default': 30, 'description': 'Days until option expires'},
                    {'name': 'risk_free_rate', 'type': 'float', 'default': 0.05, 'description': 'Risk-free interest rate'}
                ]
            }
        },
        'status': 'success'
    })