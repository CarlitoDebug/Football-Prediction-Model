import React from 'react';

const TAB_ROUTES = {
  home: '/',
  dashboard: '/predictor',
  predictions: '/fixtures',
  leagueStats: '/league-stats',
};

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
        {/* Brand & Logo */}
        <a
          href="/"
          className="navbar-brand"
          onClick={(e) => {
            e.preventDefault();
            onTabChange('home');
          }}
          style={{ outline: 'none', textDecoration: 'none' }}
        >
          <div className="navbar-logo-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path d="M3 12m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
              <path d="M9 8m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
              <path d="M15 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
              <path d="M4 20l14 0" />
            </svg>
          </div>
          <span className="navbar-brand-name">FootyPredict</span>
        </a>

        {/* Navigation Tabs */}
        <nav className="navbar-nav-tabs">
          {tabs.map((tab) => {
            const isActive = currentTab === tab.id;
            const path = TAB_ROUTES[tab.id] || '/';
            return (
              <a
                key={tab.id}
                href={path}
                className={`navbar-tab-item${isActive ? ' active' : ''}`}
                onClick={(e) => {
                  e.preventDefault();
                  onTabChange(tab.id);
                }}
              >
                {tab.label}
                {isActive && <span className="navbar-tab-indicator" />}
              </a>
            );
          })}
        </nav>
      </div>
    </header>
  );
};

export default TopNavbar;
