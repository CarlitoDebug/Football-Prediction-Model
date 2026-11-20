import React, { useState } from 'react';

const Sidebar = ({ currentTab, onTabChange, activeLeague, onSelectLeague }) => {
  const [leagueOpen, setLeagueOpen] = useState(currentTab === 'leagueStats');

  return (
    <aside className="sidebar">
      {/* Brand */}
      <button
        onClick={() => onTabChange('home')}
        className="sidebar-brand"
        style={{ background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left', width: '100%' }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: 20, height: 20, color: 'var(--brand-accent)' }}>
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M3 12m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
          <path d="M9 8m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
          <path d="M15 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
          <path d="M4 20l14 0" />
        </svg>
        FootyPredict
      </button>

      {/* Primary Nav */}
      <button
        className={`nav-item${currentTab === 'home' ? ' active' : ''}`}
        onClick={() => onTabChange('home')}
      >
        Home
      </button>

      <button
        className={`nav-item${currentTab === 'dashboard' ? ' active' : ''}`}
        onClick={() => onTabChange('dashboard')}
      >
        Match Predictor
      </button>

      <button
        className={`nav-item${currentTab === 'predictions' ? ' active' : ''}`}
        onClick={() => onTabChange('predictions')}
      >
        Fixtures
      </button>

      {/* League Stats Collapsible */}
      <div
        className="sidebar-section-label"
        onClick={() => setLeagueOpen(o => !o)}
        role="button"
        aria-expanded={leagueOpen}
      >
        <span>League Stats</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          style={{
            width: 14,
            height: 14,
            transition: 'transform 0.2s ease',
            transform: leagueOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </div>

      {leagueOpen && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2, paddingLeft: 8 }}>
          {[
            { label: 'Premier League', key: 'ENG-Premier League' },
            { label: 'La Liga',        key: 'ESP-La Liga' },
            { label: 'Bundesliga',     key: 'GER-Bundesliga' },
          ].map(({ label, key }) => (
            <button
              key={key}
              className={`nav-item${currentTab === 'leagueStats' && activeLeague === key ? ' active' : ''}`}
              onClick={() => {
                onSelectLeague(key);
                onTabChange('leagueStats');
              }}
            >
              {label}
            </button>
          ))}
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
