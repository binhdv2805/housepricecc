import { useState } from 'react';
import { trainModel } from '../services/api';
import './TrainSection.css';

export default function TrainSection({ onTrainComplete }) {
  const [trainLoading, setTrainLoading] = useState(false);
  const [trainResult, setTrainResult] = useState(null);
  const [trainError, setTrainError] = useState(null);
  const [trainConfig, setTrainConfig] = useState({
    generateSample: false,
    n_samples: 50000,
    dataPath: '',
  });

  const handleTrain = async (generateSample = false) => {
    setTrainLoading(true);
    setTrainError(null);
    setTrainResult(null);

    try {
      const trainData = {
        generate_sample: generateSample,
        n_samples: trainConfig.n_samples,
        data_path: trainConfig.dataPath || undefined,
      };

      const response = await trainModel(trainData);
      setTrainResult(response);
      
      if (onTrainComplete) {
        onTrainComplete(response);
      }
    } catch (err) {
      setTrainError(err.message);
    } finally {
      setTrainLoading(false);
    }
  };

  return (
    <div className="train-section">
      <div className="train-header">
        <div className="train-icon">🤖</div>
        <div>
          <h2>Train Model XGBoost</h2>
          <p>Huấn luyện lại model với dữ liệu mới để cải thiện độ chính xác</p>
        </div>
      </div>

      <div className="train-content">
        {/* Nút Train với Dữ Liệu Thật - Nổi bật */}
        <div className="train-real-data-section">
          <div className="real-data-card">
            <div className="real-data-header">
              <span className="real-data-icon">🎯</span>
              <div>
                <h3>Train với Dữ Liệu Thật</h3>
                <p>Huấn luyện model với dataset thực tế từ file CSV có sẵn</p>
              </div>
            </div>
            <div className="real-data-config">
              <label>
                Đường dẫn file CSV (để trống để tự động tìm):
                <input
                  type="text"
                  value={trainConfig.dataPath}
                  onChange={(e) =>
                    setTrainConfig({ ...trainConfig, dataPath: e.target.value })
                  }
                  placeholder="data/house_data.csv hoặc để trống"
                  disabled={trainLoading}
                />
              </label>
            </div>
            <button
              onClick={() => handleTrain(false)}
              className="train-real-data-btn"
              disabled={trainLoading}
            >
              {trainLoading ? (
                <>
                  <span className="spinner"></span>
                  Đang train model với dữ liệu thật...
                </>
              ) : (
                <>
                  <span>🚀</span>
                  Train với Dữ Liệu Thật
                </>
              )}
            </button>
          </div>
        </div>

        {/* Option Train với Dữ Liệu Mẫu */}
        <div className="train-options">
          <div className="option-card">
            <div className="option-header">
              <span className="option-icon">📊</span>
              <h3>Tạo Dữ Liệu Mẫu</h3>
            </div>
            <p className="option-description">
              Tự động tạo dataset mẫu với số lượng lớn để train model (dùng khi chưa có dữ liệu thật)
            </p>
            <div className="option-config">
              <label>
                Số lượng mẫu:
                <input
                  type="number"
                  value={trainConfig.n_samples}
                  onChange={(e) =>
                    setTrainConfig({ ...trainConfig, n_samples: parseInt(e.target.value) || 50000 })
                  }
                  min="1000"
                  max="100000"
                  step="1000"
                  disabled={trainLoading}
                />
              </label>
            </div>
            <button
              onClick={() => handleTrain(true)}
              className="train-action-btn primary"
              disabled={trainLoading}
            >
              {trainLoading ? (
                <>
                  <span className="spinner"></span>
                  Đang train...
                </>
              ) : (
                <>
                  <span>📊</span>
                  Train với Dữ Liệu Mẫu
                </>
              )}
            </button>
          </div>
        </div>

        {trainError && (
          <div className="train-error">
            <div className="error-icon">❌</div>
            <div>
              <h4>Lỗi khi train model</h4>
              <p>{trainError}</p>
            </div>
          </div>
        )}

        {trainResult && trainResult.status === 'success' && (
          <div className="train-success">
            <div className="success-header">
              <div className="success-icon">✅</div>
              <h3>Train thành công!</h3>
            </div>
            <p className="success-message">{trainResult.message}</p>

            {trainResult.performance?.metrics && (
              <div className="train-metrics">
                <h4>Kết quả đánh giá:</h4>
                <div className="metrics-grid">
                  <div className="metric-card">
                    <div className="metric-icon">📉</div>
                    <div className="metric-info">
                      <span className="metric-name">RMSE</span>
                      <span className="metric-value">
                        {trainResult.performance.metrics.rmse?.toLocaleString('vi-VN', {
                          maximumFractionDigits: 2
                        })}
                      </span>
                    </div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-icon">📊</div>
                    <div className="metric-info">
                      <span className="metric-name">MAE</span>
                      <span className="metric-value">
                        {trainResult.performance.metrics.mae?.toLocaleString('vi-VN', {
                          maximumFractionDigits: 2
                        })}
                      </span>
                    </div>
                  </div>
                  <div className="metric-card highlight">
                    <div className="metric-icon">⭐</div>
                    <div className="metric-info">
                      <span className="metric-name">R² Score</span>
                      <span className="metric-value">
                        {trainResult.performance.metrics.r2_score?.toFixed(4)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {trainResult.performance?.features && (
              <div className="train-features">
                <h4>Features được sử dụng ({trainResult.performance.feature_count}):</h4>
                <div className="features-tags">
                  {trainResult.performance.features.map((feature, index) => (
                    <span key={index} className="feature-tag">
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

