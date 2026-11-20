import React from 'react';
import { Toggle } from '@/components/base/toggle/toggle';

const TAB_ROUTES = {
  home: '/',
  dashboard: '/predictor',
  predictions: '/fixtures',
  leagueStats: '/league-stats',
};

const TopNavbar = ({ currentTab, onTabChange, theme = 'dark', onToggleTheme }) => {
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

        {/* Right side: Light/Dark Mode Toggle with <Toggle size="sm" /> */}
        <div className="navbar-meta">
          <div
            className="theme-toggle-wrapper"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {/* Sun Icon */}
            <svg
              className={`theme-toggle-icon${theme === 'light' ? ' active' : ''}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="14"
              height="14"
            >
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>

            {/* BaseDemo Toggle matching user's snippet */}
            <Toggle
              size="sm"
              checked={theme === 'dark'}
              onChange={() => onToggleTheme && onToggleTheme()}
              ariaLabel="Toggle dark/light mode"
            />

            {/* Moon Icon */}
            <svg
              className={`theme-toggle-icon${theme === 'dark' ? ' active' : ''}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="14"
              height="14"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNavbar;
