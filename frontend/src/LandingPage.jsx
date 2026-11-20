import React from 'react';

const LandingPage = ({ onExplorePredictions, onExploreFixtures }) => {
  return (
    <div className="landing-container">
      {/* ── 1. Hero Showcase Banner ── */}
      <section className="landing-hero">
        <div className="landing-hero-badge">
          <span className="pulse-dot"></span>
          <span>Poisson &amp; Dixon-Coles Bivariate Modeling</span>
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

      {/* ── 2. Algorithm Architecture & Specs ── */}
      <section className="landing-section">
        <div className="landing-section-header">
          <h2 className="landing-section-title">Algorithm Specifications &amp; Architecture</h2>
          <p className="landing-section-desc">
            A hybrid probabilistic machine learning system that separates finishing variance from true underlying team quality.
          </p>
        </div>

        <div className="algo-specs-grid">
          <div className="algo-spec-card">
            <div className="algo-spec-step">01</div>
            <div className="algo-spec-badge">Target Isolation</div>
            <h3 className="algo-spec-title">Underlying xG Over Raw Goals</h3>
            <p className="algo-spec-desc">
              Rather than predicting noisy goal counts directly, the base ensemble predicts match-level Expected Goals (xG). This strips out finishing variance, deflections, and goalkeeper luck to assess true performance trajectory.
            </p>
            <div className="algo-spec-footer">
              <span>Metric: Shot Quality (Understat xG)</span>
            </div>
          </div>

          <div className="algo-spec-card">
            <div className="algo-spec-step">02</div>
            <div className="algo-spec-badge">Model Stacking</div>
            <h3 className="algo-spec-title">4-Way Poisson Ensemble</h3>
            <p className="algo-spec-desc">
              Features are trained across <strong>LightGBM</strong>, <strong>XGBoost</strong>, <strong>CatBoost</strong>, and a <strong>Poisson GLM</strong> with 5-fold cross-validation. A Ridge regression meta-model stacks out-of-fold predictions into unified expected lambda parameters.
            </p>
            <div className="algo-spec-footer">
              <span>Stack: LGBM + XGB + CatBoost + GLM</span>
            </div>
          </div>

          <div className="algo-spec-card">
            <div className="algo-spec-step">03</div>
            <div className="algo-spec-badge">Bivariate Calibration</div>
            <h3 className="algo-spec-title">Dixon-Coles Low-Score Correction</h3>
            <p className="algo-spec-desc">
              Standard Poisson distributions systematically underpredict draws and low scores (0-0, 1-1, 1-0). A bivariate Dixon-Coles adjustment with dynamically optimized &rho; parameter modifies the joint probabilities to align with real football score frequencies.
            </p>
            <div className="algo-spec-footer">
              <span>Optimized Parameter: &rho; (Rho) via MLE</span>
            </div>
          </div>

          <div className="algo-spec-card">
            <div className="algo-spec-step">04</div>
            <div className="algo-spec-badge">Dynamic Ratings</div>
            <h3 className="algo-spec-title">Decayed Elo &amp; Schedule Adjustment</h3>
            <p className="algo-spec-desc">
              Calculates dynamic Elo ratings with Margin-of-Victory scaling and an exponentially weighted Home Field Advantage (HFA) fitted via Maximum Likelihood Estimation. xG is weighted against opponent difficulty (Strength-of-Schedule).
            </p>
            <div className="algo-spec-footer">
              <span>Features: Elo Diff + SoS xG + Fatigue Index</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── 3. Platform Capabilities & Features ── */}
      <section className="landing-section">
        <div className="landing-section-header">
          <h2 className="landing-section-title">Platform Capabilities &amp; Analytical Features</h2>
          <p className="landing-section-desc">
            Explore comprehensive statistical tools designed for high-conviction match analysis.
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
            <h3>1X2 &amp; Exact Score Matrix</h3>
            <p>
              Generates calibrated 3-way outcome probabilities (Home Win, Draw, Away Win) along with the top most likely exact scorelines derived from full bivariate Poisson matrices.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
            </div>
            <h3>Expected Goals &amp; Corner Modeling</h3>
            <p>
              Compare offensive and defensive xG generation alongside Tweedie-optimized Expected Corner distributions and over/under probability lines for in-depth total betting analysis.
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
            <h3>Upcoming Fixtures Simulator</h3>
            <p>
              Scans all incoming matchweeks across Premier League, La Liga, and Bundesliga. Click any matchup to instantly simulate predicted probabilities and form indicators.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <h3>Injury &amp; Squad Fatigue Tracking</h3>
            <p>
              Integrates real-time missing player feeds and rolling rest days to penalize squad depletion and consecutive fixture congestion in upcoming fixtures.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 20V10" />
                <path d="M18 20V4" />
                <path d="M6 20v-4" />
              </svg>
            </div>
            <h3>League Standings &amp; Momentum</h3>
            <p>
              Detailed league tables featuring Points Per Game (PPG), Clean Sheet percentages, Both Teams To Score (BTTS) rates, and visual 5-match form trajectories.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
              </svg>
            </div>
            <h3>Head-to-Head History</h3>
            <p>
              Time-decayed matchup archives breaking down previous encounters, goal distributions, and historical matchup dominances between the two competing sides.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
