import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { getModelInfo } from '../services/api';
import './Dashboard.css';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];

export default function Dashboard() {
  const [modelInfo, setModelInfo] = useState(null);
  const [stats, setStats] = useState({
    totalPredictions: 0,
    avgPrice: 0,
    minPrice: 0,
    maxPrice: 0,
  });
  const [recentPredictions, setRecentPredictions] = useState([]);

  useEffect(() => {
    // Load model info
    getModelInfo().then((response) => {
      if (response.status === 'success' && response.model_info) {
        setModelInfo(response.model_info);
      }
    });

    // Load stats from localStorage (lưu từ predictions)
    loadStats();
  }, []);

  const loadStats = () => {
    try {
      const saved = localStorage.getItem('housePricePredictions');
      if (saved) {
        const predictions = JSON.parse(saved);
        setRecentPredictions(predictions.slice(-10)); // 10 predictions gần nhất

        if (predictions.length > 0) {
          const prices = predictions.map((p) => p.predicted_price);
          setStats({
            totalPredictions: predictions.length,
            avgPrice: prices.reduce((a, b) => a + b, 0) / prices.length,
            minPrice: Math.min(...prices),
            maxPrice: Math.max(...prices),
          });
        }
      }
    } catch (e) {
      console.error('Error loading stats:', e);
    }
  };

  // Dữ liệu cho biểu đồ theo thời gian
  const timeSeriesData = recentPredictions.map((pred, index) => ({
    name: `Pred ${index + 1}`,
    price: pred.predicted_price,
    area: pred.features_used?.area || 0,
  }));

  // Dữ liệu phân bố theo số phòng ngủ
  const bedroomData = recentPredictions.reduce((acc, pred) => {
    const bedrooms = pred.features_used?.bedrooms || 0;
    const existing = acc.find((item) => item.name === `${bedrooms} phòng`);
    if (existing) {
      existing.value += 1;
      existing.totalPrice += pred.predicted_price;
    } else {
      acc.push({
        name: `${bedrooms} phòng`,
        value: 1,
        totalPrice: pred.predicted_price,
      });
    }
    return acc;
  }, []);

  // Dữ liệu phân bố theo diện tích
  const areaRanges = [
    { name: '< 100m²', min: 0, max: 100 },
    { name: '100-150m²', min: 100, max: 150 },
    { name: '150-200m²', min: 150, max: 200 },
    { name: '200-300m²', min: 200, max: 300 },
    { name: '> 300m²', min: 300, max: Infinity },
  ];

  const areaData = areaRanges.map((range) => {
    const count = recentPredictions.filter(
      (pred) =>
        pred.features_used?.area >= range.min &&
        pred.features_used?.area < range.max
    ).length;
    return {
      name: range.name,
      value: count,
    };
  });

  const formatPrice = (price) => {
    if (price >= 1_000_000_000) {
      return `${(price / 1_000_000_000).toFixed(2)} tỷ`;
    }
    return `${(price / 1_000_000).toFixed(0)} triệu`;
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Dashboard Thống Kê</h1>
        <p>Phân tích và hiển thị dữ liệu dự đoán giá nhà</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card card-1">
          <div className="stat-icon">🏠</div>
          <div className="stat-content">
            <h3>Tổng Dự Đoán</h3>
            <p className="stat-value">{stats.totalPredictions}</p>
            <span className="stat-label">lần dự đoán</span>
          </div>
        </div>

        <div className="stat-card card-2">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3>Giá Trung Bình</h3>
            <p className="stat-value">{formatPrice(stats.avgPrice)}</p>
            <span className="stat-label">VND</span>
          </div>
        </div>

        <div className="stat-card card-3">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>Giá Cao Nhất</h3>
            <p className="stat-value">{formatPrice(stats.maxPrice)}</p>
            <span className="stat-label">VND</span>
          </div>
        </div>

        <div className="stat-card card-4">
          <div className="stat-icon">📉</div>
          <div className="stat-content">
            <h3>Giá Thấp Nhất</h3>
            <p className="stat-value">{formatPrice(stats.minPrice)}</p>
            <span className="stat-label">VND</span>
          </div>
        </div>
      </div>

      {/* Model Info Card */}
      {modelInfo && (
        <div className="model-info-card">
          <h2>🤖 Thông Tin Model</h2>
          <div className="model-metrics">
            <div className="metric-item">
              <span className="metric-label">Version</span>
              <span className="metric-value">{modelInfo.version}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">R² Score</span>
              <span className="metric-value highlight">
                {modelInfo.metrics?.r2_score?.toFixed(4) || 'N/A'}
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">RMSE</span>
              <span className="metric-value">
                {modelInfo.metrics?.rmse?.toLocaleString('vi-VN') || 'N/A'}
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Training Samples</span>
              <span className="metric-value">
                {modelInfo.training_samples?.toLocaleString('vi-VN') || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Line Chart - Giá theo thời gian */}
        {recentPredictions.length > 0 && (
          <div className="chart-card">
            <h3>📈 Xu Hướng Giá Theo Thời Gian</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis
                  tickFormatter={(value) => formatPrice(value)}
                  domain={['auto', 'auto']}
                />
                <Tooltip
                  formatter={(value) => formatPrice(value)}
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#667eea"
                  strokeWidth={3}
                  dot={{ fill: '#667eea', r: 5 }}
                  name="Giá nhà (VND)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Bar Chart - Phân bố theo số phòng ngủ */}
        {bedroomData.length > 0 && (
          <div className="chart-card">
            <h3>🛏️ Phân Bố Theo Số Phòng Ngủ</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={bedroomData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#764ba2" name="Số lượng" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Pie Chart - Phân bố theo diện tích */}
        {areaData.some((d) => d.value > 0) && (
          <div className="chart-card">
            <h3>📐 Phân Bố Theo Diện Tích</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={areaData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {areaData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Bar Chart - Giá trung bình theo số phòng */}
        {bedroomData.length > 0 && (
          <div className="chart-card">
            <h3>💵 Giá Trung Bình Theo Số Phòng</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={bedroomData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis
                  tickFormatter={(value) => formatPrice(value)}
                  domain={['auto', 'auto']}
                />
                <Tooltip
                  formatter={(value) => formatPrice(value)}
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Bar
                  dataKey="totalPrice"
                  fill="#f093fb"
                  name="Tổng giá (VND)"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {recentPredictions.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>Chưa có dữ liệu dự đoán</h3>
          <p>Thực hiện một số dự đoán để xem thống kê tại đây!</p>
        </div>
      )}
    </div>
  );
}

