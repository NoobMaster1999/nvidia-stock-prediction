
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import joblib

# Load the historical data
df = pd.read_csv("NVDA_historical_data.csv", index_col=0, parse_dates=True)

# Feature Engineering
# Use 'Close' price for prediction
df = df[["Close"]]

# Create lagged features (e.g., previous day's close price)
for i in range(1, 6): # Using past 5 days' prices as features
    df[f'Close_Lag_{i}'] = df['Close'].shift(i)

# Drop rows with NaN values created by lagging
df.dropna(inplace=True)

# Define features (X) and target (y)
X = df.drop('Close', axis=1)
y = df['Close']

# Scale the features
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, shuffle=False)

# Train a Linear Regression model (simple model for demonstration)
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

# Save the trained model and scaler
joblib.dump(model, 'stock_prediction_model.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("Model and scaler saved successfully.")


