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
      </div>
    </header>
  );
};

export default TopNavbar;
