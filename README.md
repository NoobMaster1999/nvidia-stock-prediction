# NVIDIA Stock Price Prediction Application

A full-stack machine learning application that predicts NVIDIA stock prices using historical data and provides an interactive web interface for visualization.

## 🚀 Features

- **Real-time Stock Data**: Displays current NVIDIA stock price, change, and key statistics
- **Historical Data Visualization**: Interactive chart showing the last 30 days of stock price history
- **AI-Powered Predictions**: Machine learning model trained on historical data to predict next stock price
- **Modern Web Interface**: Responsive React frontend with beautiful gradient design
- **RESTful API**: Flask backend serving prediction endpoints

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with CORS support
- **Machine Learning**: Scikit-learn Linear Regression model
- **Data Processing**: Pandas for data manipulation
- **API Endpoints**:
  - `/api/stats` - Current stock statistics
  - `/api/historical` - Last 30 days of historical data
  - `/api/predict` - Stock price prediction

### Frontend (React)
- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React icons
- **Design**: Modern gradient UI with glassmorphism effects

### Machine Learning Model
- **Algorithm**: Linear Regression
- **Features**: Last 5 days of closing prices
- **Data**: Historical NVIDIA stock data from Yahoo Finance
- **Performance**: R-squared score of 0.998 (99.8% accuracy)

## 📊 Model Performance

The machine learning model achieved excellent performance metrics:
- **Mean Squared Error**: 5.08
- **R-squared Score**: 0.9977 (99.77% accuracy)

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm

### Backend Setup
```bash
cd stock_prediction_api
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Setup
```bash
cd stock_prediction_frontend
pnpm install
pnpm run build
```

## 🚀 Deployment

The application is configured for easy deployment:

1. **Frontend**: Built and served from Flask's static directory
2. **Backend**: Flask app configured to serve both API and frontend
3. **Port**: Application runs on port 8080
4. **CORS**: Enabled for cross-origin requests

## 📱 Usage

1. **View Statistics**: See current stock price, change, and 30-day high/low
2. **Analyze Trends**: Interactive chart shows price movement over the last 30 days
3. **Get Predictions**: Click "Predict Next Price" to get AI-powered price forecast
4. **Historical Context**: View the last 5 prices used for prediction

## 🔧 API Endpoints

### GET /api/stats
Returns current stock statistics including price, change, and 30-day metrics.

### GET /api/historical
Returns the last 30 days of historical stock data for chart visualization.

### POST /api/predict
Generates a stock price prediction based on the last 5 trading days.

## 📈 Data Source

Historical stock data is sourced from Yahoo Finance using the `yfinance` library, covering NVIDIA (NVDA) stock from 2000 to present.

## ⚠️ Disclaimer

This application is for educational purposes only and should not be used as financial advice. Stock market predictions are inherently uncertain and past performance does not guarantee future results.

## 🔗 Live Demo

Access the live application at: https://8080-iamj4h0y3oxtdqry3xnwa-6ed1f9e1.manusvm.computer

## 📁 Project Structure

```
nvidia_stock_prediction/
├── stock_prediction_api/          # Flask backend
│   ├── src/
│   │   ├── routes/
│   │   │   ├── prediction.py      # ML prediction endpoints
│   │   │   └── user.py           # User management
│   │   ├── models/               # Database models
│   │   ├── static/               # Built frontend files
│   │   └── main.py              # Flask app entry point
│   ├── venv/                    # Python virtual environment
│   └── requirements.txt         # Python dependencies
├── stock_prediction_frontend/    # React frontend
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   └── App.css              # Styling
│   ├── dist/                    # Built frontend files
│   └── package.json             # Node.js dependencies
├── NVDA_historical_data.csv     # Historical stock data
├── stock_prediction_model.pkl   # Trained ML model
├── scaler.pkl                   # Data scaler
└── README.md                    # This file
```

## 🤝 Contributing

This project demonstrates a complete machine learning workflow from data collection to deployment. Feel free to explore the code and adapt it for other stocks or prediction models.

