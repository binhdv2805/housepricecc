import { useState, useEffect } from 'react';
import { predictPrice, checkHealth, getModelInfo } from './services/api';
import LocationMap from './components/LocationMap';
import Dashboard from './components/Dashboard';
import TrainSection from './components/TrainSection';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    area: '',
    bedrooms: '',
    bathrooms: '',
    floors: '1',
    year_built: '',
    location: '',
    location_score: '',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  
  // State cho active tab
  const [activeTab, setActiveTab] = useState('predict'); // 'predict' hoặc 'train'
  
  // State cho map
  const [mapPosition, setMapPosition] = useState([10.762622, 106.660172]); // Mặc định TP.HCM
  
  // State cho model info
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    // Kiểm tra trạng thái API khi component mount
    checkHealth().then((status) => {
      setApiStatus(status);
    });
    
    // Lấy thông tin model
    getModelInfo().then((response) => {
      if (response.status === 'success' && response.model_info) {
        setModelInfo(response.model_info);
      }
    });
  }, []);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError(null);
    setResult(null);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(price);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Chuyển đổi dữ liệu form thành format API yêu cầu
      const houseData = {
        area: parseFloat(formData.area),
        bedrooms: parseInt(formData.bedrooms),
        bathrooms: parseInt(formData.bathrooms),
        floors: parseInt(formData.floors) || 1,
        year_built: formData.year_built ? parseInt(formData.year_built) : null,
        location_score: formData.location_score
          ? parseFloat(formData.location_score)
          : null,
        location: formData.location || null,  // Gửi địa chỉ lên API
      };

      const response = await predictPrice(houseData);
      setResult(response);
      
      // Lưu vào localStorage để dashboard hiển thị
      try {
        const saved = localStorage.getItem('housePricePredictions') || '[]';
        const predictions = JSON.parse(saved);
        predictions.push({
          ...response,
          timestamp: new Date().toISOString(),
        });
        // Chỉ giữ 100 predictions gần nhất
        if (predictions.length > 100) {
          predictions.shift();
        }
        localStorage.setItem('housePricePredictions', JSON.stringify(predictions));
      } catch (e) {
        console.error('Error saving prediction:', e);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTrainComplete = (result) => {
    // Refresh model info sau khi train xong
    if (result?.status === 'success') {
      checkHealth().then((status) => {
        setApiStatus(status);
      });
      getModelInfo().then((response) => {
        if (response.status === 'success' && response.model_info) {
          setModelInfo(response.model_info);
        }
      });
    }
  };

  return (
    <div className="app">
      <div className="app-content-wrapper">
        <div className="page-header">
          <h1>🏠 Dự Đoán Giá Nhà</h1>
          <p>Sử dụng mô hình XGBoost Machine Learning</p>
        </div>

        {/* Tabs Navigation */}
        <div className="tabs-container">
          <button
            className={`tab-btn ${activeTab === 'predict' ? 'active' : ''}`}
            onClick={() => setActiveTab('predict')}
          >
            <span>🔮</span>
            Dự Đoán Giá Nhà
          </button>
          <button
            className={`tab-btn ${activeTab === 'train' ? 'active' : ''}`}
            onClick={() => setActiveTab('train')}
          >
            <span>🤖</span>
            Train Model
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'train' ? (
          <TrainSection onTrainComplete={handleTrainComplete} />
        ) : (
          <div className="app-content">
            {/* Cột trái - Form */}
            <div className="form-column">
              <div className="container">
            {!apiStatus?.model_loaded && (
          <div style={{ 
            padding: '20px', 
            background: '#fef3c7', 
            borderRadius: '10px', 
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            <p style={{ margin: '0 0 15px 0', color: '#92400e' }}>
              ⚠ Model chưa được train. Vui lòng train model trước khi sử dụng.
            </p>
            <button
              onClick={() => setActiveTab('train')}
              className="train-btn"
            >
              Train Model Ngay
            </button>
          </div>
            )}

            <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="area">
              Diện tích nhà (m²) <span style={{ color: 'red' }}>*</span>
            </label>
            <input
              type="number"
              id="area"
              name="area"
              value={formData.area}
              onChange={handleChange}
              required
              min="1"
              step="0.1"
              placeholder="Ví dụ: 150.5"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="bedrooms">
                Số phòng ngủ <span style={{ color: 'red' }}>*</span>
              </label>
              <input
                type="number"
                id="bedrooms"
                name="bedrooms"
                value={formData.bedrooms}
                onChange={handleChange}
                required
                min="1"
                placeholder="Ví dụ: 3"
              />
            </div>

            <div className="form-group">
              <label htmlFor="bathrooms">
                Số phòng tắm <span style={{ color: 'red' }}>*</span>
              </label>
              <input
                type="number"
                id="bathrooms"
                name="bathrooms"
                value={formData.bathrooms}
                onChange={handleChange}
                required
                min="1"
                placeholder="Ví dụ: 2"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="floors">Số tầng</label>
              <select
                id="floors"
                name="floors"
                value={formData.floors}
                onChange={handleChange}
              >
                <option value="1">1 tầng</option>
                <option value="2">2 tầng</option>
                <option value="3">3 tầng</option>
                <option value="4">4+ tầng</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="year_built">Năm xây dựng</label>
              <input
                type="number"
                id="year_built"
                name="year_built"
                value={formData.year_built}
                onChange={handleChange}
                min="1900"
                max="2024"
                placeholder="Ví dụ: 2010"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="location">
              📍 Vị trí / Địa chỉ
            </label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Nhập địa chỉ hoặc click trên bản đồ để chọn vị trí"
            />
            <div style={{ marginTop: '15px' }}>
              <LocationMap
                position={mapPosition}
                onPositionChange={(pos) => {
                  setMapPosition(pos);
                }}
                onLocationNameChange={(name) => {
                  setFormData((prev) => ({
                    ...prev,
                    location: name,
                  }));
                }}
              />
              <small style={{ display: 'block', marginTop: '8px', color: '#666', fontSize: '0.85rem' }}>
                💡 Click trên bản đồ để chọn vị trí. Địa chỉ sẽ được tự động điền.
              </small>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="location_score">
              Điểm đánh giá vị trí (0-10)
            </label>
            <input
              type="number"
              id="location_score"
              name="location_score"
              value={formData.location_score}
              onChange={handleChange}
              min="0"
              max="10"
              step="0.1"
              placeholder="Ví dụ: 7.5"
            />
            <small style={{ display: 'block', marginTop: '5px', color: '#666', fontSize: '0.85rem' }}>
              Đánh giá chất lượng vị trí: giao thông, tiện ích, an ninh...
            </small>
          </div>

            <button
              type="submit"
              className="submit-btn"
              disabled={loading || !apiStatus?.model_loaded}
            >
              {loading ? 'Đang dự đoán...' : 'Dự Đoán Giá Nhà'}
            </button>
            </form>

            {error && <div className="error">❌ {error}</div>}

            {result && (
              <div className="result">
                <h3>💰 Giá Nhà Dự Đoán</h3>
                <div className="price">{formatPrice(result.predicted_price)}</div>
                <div className="features-summary">
                  <h4>Thông tin đã nhập:</h4>
                  <ul>
                    <li>Diện tích: {result.features_used.area} m²</li>
                    <li>Phòng ngủ: {result.features_used.bedrooms}</li>
                    <li>Phòng tắm: {result.features_used.bathrooms}</li>
                    <li>Số tầng: {result.features_used.floors}</li>
                    {result.features_used.year_built && (
                      <li>Năm xây: {result.features_used.year_built}</li>
                    )}
                    {result.features_used.location_score && (
                      <li>
                        Điểm vị trí: {result.features_used.location_score}
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            )}

            {/* Model Info Table */}
            {modelInfo && (
              <div className="model-info-section" style={{ marginTop: '30px' }}>
                <h3 style={{ marginBottom: '15px', color: '#333' }}>📊 Thông Tin Model</h3>
                <div className="model-info-table">
                  <table>
                    <tbody>
                      <tr>
                        <td className="info-label">Version</td>
                        <td className="info-value">{modelInfo.version || 'N/A'}</td>
                      </tr>
                      <tr>
                        <td className="info-label">Ngày Train</td>
                        <td className="info-value">
                          {modelInfo.trained_at 
                            ? new Date(modelInfo.trained_at).toLocaleString('vi-VN')
                            : 'N/A'}
                        </td>
                      </tr>
                      <tr>
                        <td className="info-label">Số Mẫu Train</td>
                        <td className="info-value">
                          {modelInfo.training_samples?.toLocaleString('vi-VN') || 'N/A'}
                        </td>
                      </tr>
                      <tr>
                        <td className="info-label">Số Features</td>
                        <td className="info-value">{modelInfo.feature_count || 0}</td>
                      </tr>
                      {modelInfo.metrics && (
                        <>
                          <tr>
                            <td className="info-label">RMSE</td>
                            <td className="info-value">
                              {modelInfo.metrics.rmse?.toLocaleString('vi-VN', {
                                maximumFractionDigits: 2
                              }) || 'N/A'}
                            </td>
                          </tr>
                          <tr>
                            <td className="info-label">MAE</td>
                            <td className="info-value">
                              {modelInfo.metrics.mae?.toLocaleString('vi-VN', {
                                maximumFractionDigits: 2
                              }) || 'N/A'}
                            </td>
                          </tr>
                          <tr>
                            <td className="info-label">R² Score</td>
                            <td className="info-value">
                              {modelInfo.metrics.r2_score?.toFixed(4) || 'N/A'}
                            </td>
                          </tr>
                        </>
                      )}
                      {modelInfo.features && modelInfo.features.length > 0 && (
                        <tr>
                          <td className="info-label">Features</td>
                          <td className="info-value">
                            <div className="features-list">
                              {modelInfo.features.slice(0, 5).map((f, i) => (
                                <span key={i} className="feature-tag">{f}</span>
                              ))}
                              {modelInfo.features.length > 5 && (
                                <span className="feature-tag">+{modelInfo.features.length - 5} more</span>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
              </div>
            </div>

            {/* Dashboard bên phải */}
            <div className="dashboard-sidebar">
              <Dashboard />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

