import { useState } from 'react';
import './Header.css';

export default function Header({ apiStatus, modelInfo }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="main-header">
      <div className="header-container">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">🏠</span>
            <div className="logo-text">
              <h1>HousePrice AI</h1>
              <p>Dự đoán giá nhà thông minh</p>
            </div>
          </div>
        </div>

        <div className="header-center">
          <nav className="nav-menu">
            <a href="#predict" className="nav-link">Dự Đoán</a>
            <a href="#dashboard" className="nav-link">Dashboard</a>
            <a href="#about" className="nav-link">Giới Thiệu</a>
          </nav>
        </div>

        <div className="header-right">
          <div className="status-indicator">
            {apiStatus?.model_loaded ? (
              <div className="status-badge status-online">
                <span className="status-dot"></span>
                <span>Model Ready</span>
              </div>
            ) : (
              <div className="status-badge status-offline">
                <span className="status-dot"></span>
                <span>Model Offline</span>
              </div>
            )}
          </div>
          
          {modelInfo && (
            <div className="model-version">
              <span className="version-label">v{modelInfo.version?.split('_')[0] || '1.0'}</span>
            </div>
          )}

          <button 
            className="menu-toggle"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="mobile-menu">
          <nav className="mobile-nav">
            <a href="#predict" onClick={() => setMenuOpen(false)}>Dự Đoán</a>
            <a href="#dashboard" onClick={() => setMenuOpen(false)}>Dashboard</a>
            <a href="#about" onClick={() => setMenuOpen(false)}>Giới Thiệu</a>
          </nav>
        </div>
      )}
    </header>
  );
}

