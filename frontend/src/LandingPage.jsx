import React from 'react';

const LandingPage = ({ onExplorePredictions, onExploreFixtures }) => {
  return (
    <div className="landing-container">
      {/* Hero Showcase Banner */}
      <section className="landing-hero">
        <div className="landing-hero-badge">
          <span className="pulse-dot"></span>
          <span>Poisson &amp; Dixon-Coles Bivariate Modeling · 2026/27 Live</span>
        </div>

        <h1 className="landing-hero-title">
          Quantitative Football Intelligence &amp; Predictive Modeling
        </h1>
        <p className="landing-hero-subtitle">
          Advanced probability distribution modeling, expected goals (xG), and head-to-head metrics 
          engineered for serious match analysis across top European leagues.
        </p>

        <div className="landing-cta-group">
          <button className="btn-landing-primary" onClick={onExplorePredictions}>
            Launch Predictor
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
          <button className="btn-landing-secondary" onClick={onExploreFixtures}>
            Browse Fixtures
          </button>
        </div>

        {/* Feature stat cards */}
        <div className="landing-stats-grid">
          <div className="landing-stat-card">
            <span className="landing-stat-label">Model Accuracy Rate</span>
            <div className="landing-stat-val tabular-nums">54.4%</div>
            <span className="landing-stat-sub">Graded match outcomes vs. closing market lines</span>
          </div>

          <div className="landing-stat-card">
            <span className="landing-stat-label">Leagues Tracked</span>
            <div className="landing-stat-val tabular-nums">3 Top Tiers</div>
            <span className="landing-stat-sub">Premier League, La Liga, and Bundesliga</span>
          </div>

          <div className="landing-stat-card">
            <span className="landing-stat-label">Daily Live Ingestion</span>
            <div className="landing-stat-val tabular-nums">24h Cycle</div>
            <span className="landing-stat-sub">Automated pipeline recalculating team attack &amp; defense ratings</span>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="landing-section">
        <div className="landing-section-header">
          <h2 className="landing-section-title">Engineered for analytical precision</h2>
          <p className="landing-section-desc">
            Moving beyond simple form tables with probabilistic simulation engines.
          </p>
        </div>

        <div className="landing-feature-grid">
          <div className="landing-feature-card">
            <div className="landing-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 3v18h18" />
                <path d="M18 17l-5-5-3 3-4-4" />
              </svg>
            </div>
            <h3>Dixon-Coles &amp; Poisson Engine</h3>
            <p>
              Simulates low-scoring draw corrections and interdependent goal distributions to deliver precise 1X2 and Over/Under probabilities.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
            </div>
            <h3>Expected Goals (xG)</h3>
            <p>
              Underlying offensive and defensive shot quality ratings strip out luck and variance to estimate true performance trajectory.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
            </div>
            <h3>Full Fixture Intelligence</h3>
            <p>
              One-click simulation on incoming matchweeks with up-to-date league standings, head-to-head records, and team momentum.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
