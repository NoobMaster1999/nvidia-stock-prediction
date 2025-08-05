import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, DollarSign, Activity, BarChart3 } from "lucide-react";
import "./App.css";

function App() {
  const [prediction, setPrediction] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistoricalData();
    fetchStats();
  }, []);

  const fetchPrediction = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error("Error fetching prediction:", error);
    }
    setLoading(false);
  };

  const fetchHistoricalData = async () => {
    try {
      const response = await fetch("/api/historical");
      const data = await response.json();
      setHistoricalData(data.data);
    } catch (error) {
      console.error("Error fetching historical data:", error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/stats");
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
            Stock Analysis
          </h1>
          <p className="text-xl text-gray-300">
            AI-powered stock price prediction using Markov chain
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Current Price</p>
                  <p className="text-2xl font-bold text-white">
                    ${stats.current_price?.toFixed(2)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-green-400" />
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Change</p>
                  <p
                    className={`text-2xl font-bold ${stats.change >= 0 ? "text-green-400" : "text-red-400"}`}
                  >
                    {stats.change >= 0 ? "+" : ""}${stats.change?.toFixed(2)}
                  </p>
                </div>
                <TrendingUp
                  className={`h-8 w-8 ${stats.change >= 0 ? "text-green-400" : "text-red-400"}`}
                />
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">30D High</p>
                  <p className="text-2xl font-bold text-white">
                    ${stats.high_30d?.toFixed(2)}
                  </p>
                </div>
                <Activity className="h-8 w-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">30D Low</p>
                  <p className="text-2xl font-bold text-white">
                    ${stats.low_30d?.toFixed(2)}
                  </p>
                </div>
                <BarChart3 className="h-8 w-8 text-purple-400" />
              </div>
            </div>
          </div>
        )}

        {/* Chart */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">
            Price History (Last 30 Days)
          </h2>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="date"
                  stroke="#9CA3AF"
                  tick={{ fill: "#9CA3AF" }}
                />
                <YAxis stroke="#9CA3AF" tick={{ fill: "#9CA3AF" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                    color: "#F9FAFB",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="close"
                  stroke="#10B981"
                  strokeWidth={2}
                  dot={{ fill: "#10B981", strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Prediction Section */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6">
            Stock Price Prediction
          </h2>

          <div className="text-center">
            <button
              onClick={fetchPrediction}
              disabled={loading}
              className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Predicting..." : "Predict Next Price"}
            </button>
          </div>

          {prediction && (
            <div className="mt-8 text-center">
              <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-xl p-6 border border-green-500/30">
                <h3 className="text-lg font-semibold text-white mb-2">
                  Predicted Next Price
                </h3>
                <p className="text-4xl font-bold text-green-400 mb-4">
                  ${prediction.prediction?.toFixed(2)}
                </p>
                <p className="text-gray-300 text-sm">
                  Based on the last 5 trading days
                </p>
                {prediction.last_5_prices && (
                  <div className="mt-4">
                    <p className="text-gray-400 text-sm mb-2">
                      Recent prices used:
                    </p>
                    <div className="flex justify-center space-x-2">
                      {prediction.last_5_prices.map((price, index) => (
                        <span
                          key={index}
                          className="bg-white/10 px-3 py-1 rounded text-sm text-gray-300"
                        >
                          ${price.toFixed(2)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12">
          <p className="text-gray-400 text-sm">
            Disclaimer: This is for educational purposes only. Not financial
            advice.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
