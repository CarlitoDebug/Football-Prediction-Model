import React from 'react';

const TopNavbar = ({ currentTab, onTabChange }) => {
  const tabs = [
    { id: 'home', label: 'Home' },
    { id: 'dashboard', label: 'Match Predictor' },
    { id: 'predictions', label: 'Fixtures' },
    { id: 'leagueStats', label: 'League Statistics' },
  ];

  return (
    <header className="site-navbar">
      <div className="site-navbar-inner">
        {/* Brand / Logo */}
        <div 
          className="navbar-brand" 
          onClick={() => onTabChange('home')}
          role="button"
          tabIndex={0}
        >
          <div className="navbar-logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
              <path d="M9 8m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
              <path d="M15 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
              <path d="M4 20l14 0" />
            </svg>
          </div>
          <span className="navbar-brand-name">FootyPredict</span>
          <span className="navbar-badge">PRO</span>
        </div>

        {/* Navigation Tabs */}
        <nav className="navbar-nav-tabs">
          {tabs.map((tab) => {
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                className={`navbar-tab-item${isActive ? ' active' : ''}`}
                onClick={() => onTabChange(tab.id)}
              >
                {tab.label}
                {isActive && <span className="navbar-tab-indicator" />}
              </button>
            );
          })}
        </nav>

        {/* Right Status / Meta */}
        <div className="navbar-meta">
          <div className="navbar-status-pill">
            <span className="status-indicator-dot"></span>
            <span>2026/27 Active</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNavbar;
