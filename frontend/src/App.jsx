import React, { useState, useEffect } from 'react';
import './index.css';
import Sidebar from './Sidebar';
import LeagueStats from './LeagueStats';
import TeamFormCard from './TeamFormCard';
import BttsPredictionsCard from './BttsPredictionsCard';

import { API_URL, API_BASE_URL } from './config/api';
const LEAGUES = ['All', 'ENG-Premier League', 'ESP-La Liga', 'GER-Bundesliga'];

const App = () => {
  const [teams, setTeams] = useState([]);
  const [teamsError, setTeamsError] = useState(null);
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [activeLeague, setActiveLeague] = useState('All');
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [h2hData, setH2hData] = useState(null);
  const [displayProbs, setDisplayProbs] = useState({ h: '0.0', d: '0.0', a: '0.0' });

  // Fixtures State
  const [fixtures, setFixtures] = useState([]);
  const [fixturesLoading, setFixturesLoading] = useState(false);
  const [fixturesError, setFixturesError] = useState(null);
  const [availableMatchweeks, setAvailableMatchweeks] = useState([]);
  const [currentMatchweekIndex, setCurrentMatchweekIndex] = useState(0);

  useEffect(() => {
    fetch(`${API_URL}/teams`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (data.teams) {
          setTeams(data.teams);
          setTeamsError(null);
          if (data.teams.includes("Arsenal")) setHomeTeam("Arsenal");
          if (data.teams.includes("Chelsea")) setAwayTeam("Chelsea");
        }
      })
      .catch(err => {
        console.error("API Fetch Failed (teams):", err);
        setTeamsError("Could not reach backend API. If the free cloud server was sleeping, please wait ~30s and refresh.");
      });
  }, []);

  useEffect(() => {
    fetchFixtures(activeLeague);
  }, [activeLeague]);

  const handleLeagueClick = (league) => {
    setActiveLeague(league);
    const fixturesSection = document.getElementById('fixtures-section');
    if (fixturesSection) {
      fixturesSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const getLeagueName = (league) => {
    if (league === 'All') return 'All Leagues';
    if (league === 'ENG-Premier League') return 'English Premier League';
    if (league === 'ESP-La Liga') return 'La Liga';
    if (league === 'GER-Bundesliga') return 'Bundesliga';
    return league.split('-')[1];
  };

  const getTeamLogo = (teamName) => {
    const logos = {
      // Premier League
      "Arsenal": "/logos/premier-league/arsenal-logo-footylogos.svg",
      "Chelsea": "/logos/premier-league/chelsea-logo-footylogos.svg",
      "Manchester City": "/logos/premier-league/manchester-city-logo-footylogos.svg",
      "Manchester United": "/logos/premier-league/manchester-united-logo-footylogos.svg",
      "Liverpool": "/logos/premier-league/liverpool-fc-logo-footylogos.svg",
      "Tottenham": "/logos/premier-league/tottenham-hotspur-logo-footylogos.svg",
      "Everton": "/logos/premier-league/everton-logo-footylogos.svg",
      "Aston Villa": "/logos/premier-league/aston-villa-logo-footylogos.svg",
      "Sunderland": "/logos/premier-league/sunderland-logo-footylogos.svg",
      "Nottingham Forest": "/logos/premier-league/nottingham-forest-logo-footylogos.svg",
      "Bournemouth": "/logos/premier-league/afc-bournemouth-logo-footylogos.svg",
      "Brentford": "/logos/premier-league/brentford-logo-footylogos.svg",
      "Hull": "/logos/premier-league/hull-city-logo-footylogos.svg",
      "Crystal Palace": "/logos/premier-league/crystal-palace-logo-footylogos.svg",
      "Ipswich": "/logos/premier-league/ipswich-town-logo-footylogos.svg",
      "Fulham": "/logos/premier-league/fulham-logo-footylogos.svg",
      "Coventry": "/logos/premier-league/coventry-city-logo-footylogos.svg",
      "Brighton": "/logos/premier-league/brighton-and-hove-albion-logo-footylogos.svg",
      "Leeds": "/logos/premier-league/leeds-united-logo-footylogos.svg",
      "Newcastle United": "/logos/premier-league/newcastle-united-logo-footylogos.svg",
      "Leicester": "/logos/premier-league/chelsea-logo-footylogos.svg",
      "West Ham": "/logos/premier-league/fulham-logo-footylogos.svg",
      "Wolverhampton Wanderers": "/logos/premier-league/brentford-logo-footylogos.svg",

      // La Liga
      "Valencia": "/logos/la-liga/valencia-cf-logo-footylogos.svg",
      "Alaves": "/logos/la-liga/deportivo-alaves-logo-footylogos.svg",
      "Osasuna": "/logos/la-liga/osasuna-logo-footylogos.svg",
      "Barcelona": "/logos/la-liga/fc-barcelona-logo-footylogos.svg",
      "Celta Vigo": "/logos/la-liga/celta-vigo-logo-footylogos.svg",
      "Sevilla": "/logos/la-liga/sevilla-fc-logo-footylogos.svg",
      "Elche": "/logos/la-liga/elche-cf-logo-footylogos.svg",
      "Real Betis": "/logos/la-liga/real-betis-balompie-logo-footylogos.svg",
      "Athletic Club": "/logos/la-liga/athletic-club-bilbao-logo-footylogos.svg",
      "Espanyol": "/logos/la-liga/rcd-espanyol-barcelona-logo-footylogos.svg",
      "Atletico Madrid": "/logos/la-liga/atletico-madrid-logo-footylogos.svg",
      "Levante": "/logos/la-liga/levante-ud-logo-footylogos.svg",
      "Real Sociedad": "/logos/la-liga/real-sociedad-logo-footylogos.svg",
      "Getafe": "/logos/la-liga/getafe-cf-logo-footylogos.svg",
      "Rayo Vallecano": "/logos/la-liga/rayo-vallecano-logo-footylogos.svg",
      "Real Madrid": "/logos/la-liga/real-madrid-logo-footylogos.svg",
      "Racing Santander": "/logos/la-liga/racing-santander-logo-footylogos.svg",
      "Deportivo La Coruna": "/logos/la-liga/deportivo-la-coruna-logo-footylogos.svg",
      "Malaga": "/logos/la-liga/malaga-cf-logo-footylogos.svg",
      "Villarreal": "/logos/la-liga/villarreal-cf-logo-footylogos.svg",
      "Girona": "/logos/la-liga/fc-barcelona-logo-footylogos.svg",
      "Mallorca": "/logos/la-liga/osasuna-logo-footylogos.svg",
      "Las Palmas": "/logos/la-liga/valencia-cf-logo-footylogos.svg",
      "Leganes": "/logos/la-liga/getafe-cf-logo-footylogos.svg",
      "Real Valladolid": "/logos/la-liga/celta-vigo-logo-footylogos.svg",

      // Bundesliga
      "Borussia Dortmund": "/logos/bundesliga/borussia-dortmund-logo-footylogos.svg",
      "Union Berlin": "/logos/bundesliga/union-berlin-logo-footylogos.svg",
      "VfB Stuttgart": "/logos/bundesliga/vfb-stuttgart-logo-footylogos.svg",
      "FC Cologne": "/logos/bundesliga/1-fc-koln-logo-footylogos.svg",
      "Mainz 05": "/logos/bundesliga/mainz-05-logo-footylogos.svg",
      "RasenBallsport Leipzig": "/logos/bundesliga/rb-leipzig-logo-footylogos.svg",
      "Bayer Leverkusen": "/logos/bundesliga/bayer-leverkusen-logo-footylogos.svg",
      "Eintracht Frankfurt": "/logos/bundesliga/eintracht-frankfurt-logo-footylogos.svg",
      "Freiburg": "/logos/bundesliga/sc-freiburg-logo-footylogos.svg",
      "Bayern Munich": "/logos/bundesliga/bayern-munich-logo-footylogos.svg",
      "Hoffenheim": "/logos/bundesliga/tsg-hoffenheim-logo-footylogos.svg",
      "Schalke 04": "/logos/bundesliga/schalke-04-logo-footylogos.svg",
      "Werder Bremen": "/logos/bundesliga/werder-bremen-logo-footylogos.svg",
      "Hamburger SV": "/logos/bundesliga/hamburger-sv-logo-footylogos.svg",
      "Augsburg": "/logos/bundesliga/fc-augsburg-logo-footylogos.svg",
      "Borussia M.Gladbach": "/logos/bundesliga/borussia-monchengladbach-logo-footylogos.svg",
      "Paderborn": "/logos/bundesliga/sc-paderborn-07-logo-footylogos.svg",
      "Paderborn 07": "/logos/bundesliga/sc-paderborn-07-logo-footylogos.svg",
      "SC Paderborn 07": "/logos/bundesliga/sc-paderborn-07-logo-footylogos.svg",
      "Elversberg": "/logos/bundesliga/sv-elversberg-logo-footylogos.svg",
      "St. Pauli": "/logos/bundesliga/fc-augsburg-logo-footylogos.svg",
      "Wolfsburg": "/logos/bundesliga/bayer-leverkusen-logo-footylogos.svg",
      "Bochum": "/logos/bundesliga/mainz-05-logo-footylogos.svg",
      "FC Heidenheim": "/logos/bundesliga/1-fc-koln-logo-footylogos.svg",
      "Holstein Kiel": "/logos/bundesliga/hamburger-sv-logo-footylogos.svg",
    };
    return logos[teamName] || `https://ui-avatars.com/api/?name=${encodeURIComponent(teamName)}&background=1e293b&color=94a3b8&size=120&rounded=true`;
  };

  const getLeagueLogo = (league) => {
    const leagueLogos = {
      'ENG-Premier League': '/logos/premier-league/premier-league-england-logo-footylogos.svg',
      'ESP-La Liga': '/logos/la-liga/laliga-spain-logo-footylogos.svg',
      'GER-Bundesliga': '/logos/bundesliga/bundesliga-germany-logo-footylogos.svg',
    };
    return leagueLogos[league] || null;
  };

  const fetchFixtures = async (league) => {
    setFixturesLoading(true);
    setFixturesError(null);
    try {
      let url = `${API_URL}/fixtures`;
      if (league && league !== 'All') {
        url += `?league=${encodeURIComponent(league)}`;
      }
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.fixtures) {
        setFixtures(data.fixtures);
        const weeks = [...new Set(data.fixtures.map(f => f.matchweek))].sort((a, b) => a - b);
        setAvailableMatchweeks(weeks);
        setCurrentMatchweekIndex(0);
      }
    } catch (err) {
      console.error("API Fetch Failed (fixtures):", err);
      setFixturesError("Failed to load fixtures. If the cloud server is waking up, please wait ~30s and retry.");
    } finally {
      setFixturesLoading(false);
    }
  };

  const handlePredict = async (hTeam, aTeam) => {
    if (!hTeam || !aTeam) return;
    setLoading(true);
    setError(null);
    setPrediction(null);
    setH2hData(null);

    try {
      const res = await fetch(`${API_URL}/predict?home_team=${encodeURIComponent(hTeam)}&away_team=${encodeURIComponent(aTeam)}`);
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to generate prediction');
      }

      const h2hRes = await fetch(`${API_URL}/h2h?home_team=${encodeURIComponent(hTeam)}&away_team=${encodeURIComponent(aTeam)}`);
      if (h2hRes.ok) {
        const h2h = await h2hRes.json();
        setH2hData(h2h);
      }

      // Exact probability rounding (no 100.1% errors)
      let h = Math.round(data.home_win_prob * 1000);
      let d = Math.round(data.draw_prob * 1000);
      let a = Math.round(data.away_win_prob * 1000);
      const diff = 1000 - (h + d + a);
      if (diff !== 0) {
        if (h >= d && h >= a) h += diff;
        else if (d >= h && d >= a) d += diff;
        else a += diff;
      }
      setDisplayProbs({
        h: (h / 10).toFixed(1),
        d: (d / 10).toFixed(1),
        a: (a / 10).toFixed(1),
      });

      setPrediction(data);
    } catch (err) {
      console.error("API Fetch Failed (predict):", err);
      setError(err.message || 'Error communicating with prediction server');
    } finally {
      setLoading(false);
    }
  };

  const handleFixtureClick = (fixture) => {
    setCurrentTab('dashboard');
    setHomeTeam(fixture.home_team);
    setAwayTeam(fixture.away_team);
    handlePredict(fixture.home_team, fixture.away_team);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleTabChange = (tab) => {
    setCurrentTab(tab);
    if (tab === 'dashboard') {
      setHomeTeam('');
      setAwayTeam('');
      setPrediction(null);
      setH2hData(null);
      setError(null);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar
        currentTab={currentTab}
        onTabChange={handleTabChange}
        activeLeague={activeLeague}
        onSelectLeague={setActiveLeague}
      />

      <div className="main-wrapper">
        <div className="main-container">

          {/* ── Compact Top Header (replaces large blue banner) ── */}
          <header className="top-header">
            <div>
              <h1 className="top-header-title">Football Analytics Pro</h1>
              <p className="top-header-subtitle">AI-Powered Match Predictions &amp; Data Modeling</p>
            </div>
            <div className="top-header-badge">
              <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--emerald-bar)', flexShrink: 0 }}></span>
              Model: Poisson + Dixon-Coles &nbsp;·&nbsp; 2026/27 Active
            </div>
          </header>

          {/* ═══════════════════════════════════════════════════
              TAB: DASHBOARD (Match Prediction)
          ═══════════════════════════════════════════════════ */}
          {currentTab === 'dashboard' && (
            <>
              {teamsError && (
                <div className="card" style={{ padding: '14px 18px', background: 'var(--rose-bg)', border: '1px solid var(--rose-border)', marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                    <div>
                      <p style={{ color: 'var(--rose-text)', fontSize: 13, margin: 0, fontWeight: 600 }}>
                        {teamsError}
                      </p>
                      <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
                        API Endpoint: <code>{API_URL}</code>
                      </p>
                    </div>
                    <button
                      className="btn-secondary"
                      style={{ fontSize: 12, padding: '4px 12px' }}
                      onClick={() => window.location.reload()}
                    >
                      Retry Connection
                    </button>
                  </div>
                </div>
              )}

              {/* Match Selector Card */}
              <div className="card">
                <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', gap: 16 }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1, minWidth: 180 }}>
                    <label style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>Home Team</label>
                    <select className="select-input" value={homeTeam} onChange={e => setHomeTeam(e.target.value)} style={{ width: '100%' }}>
                      <option value="">Select Home Team</option>
                      {teams.map(team => <option key={team} value={team}>{team}</option>)}
                    </select>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', paddingBottom: 10, fontWeight: 700, color: 'var(--text-muted)', fontSize: 16 }}>VS</div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1, minWidth: 180 }}>
                    <label style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>Away Team</label>
                    <select className="select-input" value={awayTeam} onChange={e => setAwayTeam(e.target.value)} style={{ width: '100%' }}>
                      <option value="">Select Away Team</option>
                      {teams.map(team => <option key={team} value={team}>{team}</option>)}
                    </select>
                  </div>

                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <button
                      className="btn-primary"
                      onClick={() => handlePredict(homeTeam, awayTeam)}
                      disabled={loading || !homeTeam || !awayTeam}
                    >
                      {loading ? 'Predicting…' : 'Generate Prediction'}
                    </button>
                    <button className="btn-secondary" onClick={() => handleTabChange('predictions')}>
                      ← Back to Fixtures
                    </button>
                  </div>
                </div>

                {error && <div className="error-message" style={{ marginTop: 16 }}>{error}</div>}
                {loading && <div style={{ marginTop: 20, textAlign: 'center' }}><div className="loader"></div></div>}
              </div>

              {/* Top Analytics Row */}
              {prediction && !loading && (
                <div className="grid-3">
                  {/* Match Overview */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">Match Overview</h3>
                    </div>
                    <div className="xg-display">
                      <span className="xg-home tabular-nums">{prediction.home_xg.toFixed(2)}</span>
                      <span className="xg-vs">xG</span>
                      <span className="xg-away tabular-nums">{prediction.away_xg.toFixed(2)}</span>
                    </div>
                    <div style={{ marginTop: 8 }}>
                      <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: 8 }}>Match Probabilities</div>
                      <div className="odds-bar-container">
                        <div className="odds-segment odds-home" style={{ width: `${displayProbs.h}%` }}>{displayProbs.h}%</div>
                        <div className="odds-segment odds-draw" style={{ width: `${displayProbs.d}%` }}>{displayProbs.d}%</div>
                        <div className="odds-segment odds-away" style={{ width: `${displayProbs.a}%` }}>{displayProbs.a}%</div>
                      </div>
                      <div className="odds-labels">
                        <span>{prediction.home_team}</span>
                        <span>Draw</span>
                        <span>{prediction.away_team}</span>
                      </div>
                    </div>
                  </div>

                  {/* Top 3 Exact Scores */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">Top 3 Exact Scores</h3>
                    </div>
                    <div style={{ marginTop: 4 }}>
                      {prediction.top_exact_scores.map((score, idx) => (
                        <div key={idx} className="score-row">
                          <div className="team-score tabular-nums">{score.home_goals} – {score.away_goals}</div>
                          <span className={`pill ${(score.probability * 100) >= 10 ? 'pill-emerald' : 'pill-neutral'}`}>
                            {(score.probability * 100).toFixed(2)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Expected Corners */}
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">Expected Corners</h3>
                    </div>
                    <div className="corners-grid">
                      <div className="corner-stat">
                        <div className="corner-stat-value tabular-nums">{prediction.exp_home_corners.toFixed(1)}</div>
                        <div className="corner-stat-label">{prediction.home_team}</div>
                      </div>
                      <div className="corner-stat">
                        <div className="corner-stat-value tabular-nums">{prediction.exp_away_corners.toFixed(1)}</div>
                        <div className="corner-stat-label">{prediction.away_team}</div>
                      </div>
                    </div>
                    <table className="corner-table">
                      <thead>
                        <tr>
                          <th>Market</th>
                          <th style={{ textAlign: 'right' }}>Over Prob</th>
                        </tr>
                      </thead>
                      <tbody>
                        {prediction.corner_over_probs.filter(c => c.line >= 7.5 && c.line <= 12.5).map((c, idx) => (
                          <tr key={idx}>
                            <td>Total Over {c.line}</td>
                            <td style={{ textAlign: 'right', fontWeight: 600, color: c.total_over_prob > 0.5 ? 'var(--emerald-text)' : 'var(--text-primary)' }} className="tabular-nums">
                              {(c.total_over_prob * 100).toFixed(1)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Head to Head */}
              {prediction && !loading && (
                <div className="card">
                  <h3 className="card-title" style={{ marginBottom: 20 }}>
                    Head to Head Statistics
                    <span style={{ fontWeight: 400, color: 'var(--text-muted)', fontSize: 13, marginLeft: 8 }}>
                      – {prediction.home_team} vs {prediction.away_team}
                    </span>
                  </h3>

                  {h2hData && h2hData.summary && h2hData.summary.total_matches > 0 ? (
                    <div>
                      {/* Teams & Progress Bar */}
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, marginBottom: 24 }}>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '22%' }}>
                          <img src={getTeamLogo(homeTeam)} alt={homeTeam} className="logo-lg" style={{ marginBottom: 8 }}
                            onError={(e) => { e.target.onerror = null; e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(homeTeam)}&background=1e293b&color=94a3b8&size=120&rounded=true`; }}
                          />
                          <div style={{ fontWeight: 600, fontSize: 13, textAlign: 'center', color: 'var(--text-primary)' }}>{homeTeam}</div>
                          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>({((h2hData.summary.home_wins / h2hData.summary.total_matches) * 100).toFixed(0)}%)</div>
                        </div>

                        <div style={{ flex: 1, textAlign: 'center' }}>
                          <div style={{ fontWeight: 700, fontSize: 20, color: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums' }}>{h2hData.summary.total_matches}</div>
                          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Matches</div>
                          <div className="h2h-progress-bar">
                            <div className="h2h-segment h2h-segment-home" style={{ width: `${(h2hData.summary.home_wins / h2hData.summary.total_matches) * 100}%` }}>
                              {h2hData.summary.home_wins > 0 ? `${((h2hData.summary.home_wins / h2hData.summary.total_matches) * 100).toFixed(0)}%` : ''}
                            </div>
                            <div className="h2h-segment h2h-segment-draw" style={{ width: `${(h2hData.summary.draws / h2hData.summary.total_matches) * 100}%` }}>
                              {h2hData.summary.draws > 0 ? `${((h2hData.summary.draws / h2hData.summary.total_matches) * 100).toFixed(0)}%` : ''}
                            </div>
                            <div className="h2h-segment h2h-segment-away" style={{ width: `${(h2hData.summary.away_wins / h2hData.summary.total_matches) * 100}%` }}>
                              {h2hData.summary.away_wins > 0 ? `${((h2hData.summary.away_wins / h2hData.summary.total_matches) * 100).toFixed(0)}%` : ''}
                            </div>
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontSize: 12, color: 'var(--text-secondary)' }}>
                            <span>{h2hData.summary.home_wins} Wins</span>
                            <span>{h2hData.summary.draws} Draws</span>
                            <span>{h2hData.summary.away_wins} Wins</span>
                          </div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '22%' }}>
                          <img src={getTeamLogo(awayTeam)} alt={awayTeam} className="logo-lg" style={{ marginBottom: 8 }}
                            onError={(e) => { e.target.onerror = null; e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(awayTeam)}&background=1e293b&color=94a3b8&size=120&rounded=true`; }}
                          />
                          <div style={{ fontWeight: 600, fontSize: 13, textAlign: 'center', color: 'var(--text-primary)' }}>{awayTeam}</div>
                          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>({((h2hData.summary.away_wins / h2hData.summary.total_matches) * 100).toFixed(0)}%)</div>
                        </div>
                      </div>

                      {/* Summary paragraph */}
                      <p style={{ color: 'var(--text-secondary)', fontSize: 13, lineHeight: 1.6, marginBottom: 24, textAlign: 'center' }}>
                        {homeTeam} vs {awayTeam}'s head to head record shows that in the previous {h2hData.summary.total_matches} meetings,{' '}
                        {homeTeam} has won {h2hData.summary.home_wins} times, {awayTeam} has won {h2hData.summary.away_wins} times,{' '}
                        and {h2hData.summary.draws} ended in a draw.{' '}
                        {homeTeam} scored {h2hData.summary.home_goals} goals and {awayTeam} scored {h2hData.summary.away_goals} goals in these matches.
                      </p>

                      {/* 6 Metric Tiles */}
                      <div className="h2h-stats-grid">
                        {[
                          { pct: ((h2hData.summary.over_1_5 / h2hData.summary.total_matches) * 100).toFixed(0), label: 'Over 1.5', sub: `${h2hData.summary.over_1_5} / ${h2hData.summary.total_matches} matches` },
                          { pct: ((h2hData.summary.over_2_5 / h2hData.summary.total_matches) * 100).toFixed(0), label: 'Over 2.5', sub: `${h2hData.summary.over_2_5} / ${h2hData.summary.total_matches} matches` },
                          { pct: ((h2hData.summary.over_3_5 / h2hData.summary.total_matches) * 100).toFixed(0), label: 'Over 3.5', sub: `${h2hData.summary.over_3_5} / ${h2hData.summary.total_matches} matches` },
                          { pct: ((h2hData.summary.btts / h2hData.summary.total_matches) * 100).toFixed(0), label: 'BTTS', sub: `${h2hData.summary.btts} / ${h2hData.summary.total_matches} matches` },
                          { pct: ((h2hData.summary.home_clean_sheets / h2hData.summary.total_matches) * 100).toFixed(0), label: 'Clean Sheets', sub: homeTeam },
                          { pct: ((h2hData.summary.away_clean_sheets / h2hData.summary.total_matches) * 100).toFixed(0), label: 'Clean Sheets', sub: awayTeam },
                        ].map((tile, i) => (
                          <div key={i} className="h2h-stat-card">
                            <div className="h2h-stat-title tabular-nums">{tile.pct}% <span style={{ fontWeight: 400, color: 'var(--text-secondary)', fontSize: 13 }}>{tile.label}</span></div>
                            <div className="h2h-stat-sub">{tile.sub}</div>
                            <div className="h2h-stat-bar">
                              <div className="h2h-stat-bar-fill" style={{ width: `${tile.pct}%` }}></div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Recent Matches */}
                      <h4 style={{ marginTop: 28, marginBottom: 12, color: 'var(--text-primary)', fontSize: 14, fontWeight: 600 }}>Recent Matches</h4>
                      <div className="h2h-scroll-container">
                        {h2hData.recent_matches.map((m, i) => {
                          const truncHome = m.home_team.length > 13 ? m.home_team.substring(0, 10) + '…' : m.home_team;
                          const truncAway = m.away_team.length > 13 ? m.away_team.substring(0, 10) + '…' : m.away_team;
                          return (
                            <div key={i} className="h2h-card">
                              <div className="h2h-date">{m.date}</div>
                              <div className="h2h-team-row h2h-top-row">
                                <div className="h2h-team-info">
                                  <img src={getTeamLogo(m.home_team)} alt={m.home_team} className="h2h-mini-logo"
                                    onError={(e) => { e.target.onerror = null; e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(m.home_team)}&background=1e293b&color=94a3b8&size=120&rounded=true`; }}
                                  />
                                  <span className="h2h-team-name" title={m.home_team}>{truncHome}</span>
                                </div>
                                <span className="h2h-goals tabular-nums">{m.home_goals}</span>
                              </div>
                              <div className="h2h-team-row">
                                <div className="h2h-team-info">
                                  <img src={getTeamLogo(m.away_team)} alt={m.away_team} className="h2h-mini-logo"
                                    onError={(e) => { e.target.onerror = null; e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(m.away_team)}&background=1e293b&color=94a3b8&size=120&rounded=true`; }}
                                  />
                                  <span className="h2h-team-name" title={m.away_team}>{truncAway}</span>
                                </div>
                                <span className="h2h-goals tabular-nums">{m.away_goals}</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ) : (
                    <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No available data</div>
                  )}
                </div>
              )}

              {/* Team Form + PPG Comparison + BTTS */}
              {prediction && !loading && (
                <div>
                  {(!prediction.home_form || !prediction.away_form) ? (
                    <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>No available data</div>
                  ) : (() => {
                    const hPpg = prediction.home_form?.overall?.ppg || 0;
                    const aPpg = prediction.away_form?.overall?.ppg || 0;
                    const total = hPpg + aPpg;
                    const hPct = total > 0 ? (hPpg / total) * 100 : 50;
                    const aPct = total > 0 ? (aPpg / total) * 100 : 50;

                    let betterTeam = '';
                    let pctDiff = 0;
                    if (hPpg > aPpg) {
                      betterTeam = prediction.home_team;
                      pctDiff = aPpg === 0 ? 100 : (Math.min(100, Math.round(((hPpg - aPpg) / aPpg) * 100)) || 0);
                    } else if (aPpg > hPpg) {
                      betterTeam = prediction.away_team;
                      pctDiff = hPpg === 0 ? 100 : (Math.min(100, Math.round(((aPpg - hPpg) / hPpg) * 100)) || 0);
                    }

                    return (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                        {/* 3-column team form layout */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr minmax(200px, 280px) 1fr', gap: 20, alignItems: 'start' }}>
                          <TeamFormCard
                            teamName={prediction.home_team}
                            formData={prediction.home_form}
                            getTeamLogo={getTeamLogo}
                            isHomeTeam={true}
                          />

                          {/* Center PPG comparison — wrapped in .card so it never floats */}
                          <div className="card" style={{ textAlign: 'center' }}>
                            <div className="card-header" style={{ justifyContent: 'center' }}>
                              <h3 className="card-title">Points Per Game</h3>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginBottom: 16 }}>
                              <div>
                                <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--emerald-text)', fontVariantNumeric: 'tabular-nums' }}>{hPpg.toFixed(2)}</div>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{prediction.home_team}</div>
                              </div>
                              <div style={{ fontSize: 20, color: 'var(--text-muted)', alignSelf: 'center' }}>vs</div>
                              <div>
                                <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--rose-text)', fontVariantNumeric: 'tabular-nums' }}>{aPpg.toFixed(2)}</div>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{prediction.away_team}</div>
                              </div>
                            </div>
                            <div className="ppg-bar-container" style={{ marginBottom: 12 }}>
                              <div className="ppg-bar-home" style={{ width: `${hPct}%` }}></div>
                              <div className="ppg-bar-away" style={{ width: `${aPct}%` }}></div>
                            </div>
                            {betterTeam ? (
                              <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0 }}>
                                <strong style={{ color: 'var(--text-primary)' }}>{betterTeam}</strong> is{' '}
                                <strong style={{ color: 'var(--emerald-text)' }}>+{pctDiff}%</strong> better in PPG
                              </p>
                            ) : (
                              <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0 }}>Teams are equal in Points Per Game</p>
                            )}
                            <div style={{ display: 'flex', justifyContent: 'center', gap: -8, marginTop: 16 }}>
                              <img className="logo-sm" src={getTeamLogo(prediction.home_team)} alt={prediction.home_team} style={{ borderRadius: '50%', border: '2px solid #fff', marginRight: -4 }} />
                              <img className="logo-sm" src={getTeamLogo(prediction.away_team)} alt={prediction.away_team} style={{ borderRadius: '50%', border: '2px solid #fff' }} />
                            </div>
                          </div>

                          <TeamFormCard
                            teamName={prediction.away_team}
                            formData={prediction.away_form}
                            getTeamLogo={getTeamLogo}
                            isHomeTeam={false}
                          />
                        </div>

                        {/* BTTS Predictions */}
                        {prediction.btts_predictions && (
                          <BttsPredictionsCard
                            data={prediction.btts_predictions}
                            homeTeam={prediction.home_team}
                            awayTeam={prediction.away_team}
                          />
                        )}
                      </div>
                    );
                  })()}
                </div>
              )}
            </>
          )}

          {/* ═══════════════════════════════════════════════════
              TAB: LEAGUE STATS
          ═══════════════════════════════════════════════════ */}
          {currentTab === 'leagueStats' && (
            <LeagueStats activeLeague={activeLeague} getTeamLogo={getTeamLogo} />
          )}

          {/* ═══════════════════════════════════════════════════
              TAB: PREDICTIONS (Incoming Fixtures)
          ═══════════════════════════════════════════════════ */}
          {currentTab === 'predictions' && (
            <div id="fixtures-section">
              {/* League filter tab-bar */}
              <div className="tab-bar" style={{ marginBottom: 24 }}>
                {LEAGUES.map(league => (
                  <button
                    key={league}
                    className={`tab-btn${activeLeague === league ? ' active' : ''}`}
                    onClick={() => handleLeagueClick(league)}
                  >
                    {getLeagueLogo(league) && (
                      <img src={getLeagueLogo(league)} alt={league} className="logo-xs" />
                    )}
                    <span>{getLeagueName(league)}</span>
                  </button>
                ))}
              </div>

              {/* Incoming Fixtures header + matchweek pagination */}
              <div className="matchweek-pagination">
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ width: 4, height: 20, backgroundColor: 'var(--brand-accent)', borderRadius: 2, display: 'inline-block' }}></span>
                  Incoming Fixtures
                </h2>
                {availableMatchweeks.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <button
                      className="btn-secondary"
                      onClick={() => setCurrentMatchweekIndex(Math.max(0, currentMatchweekIndex - 1))}
                      disabled={currentMatchweekIndex === 0}
                    >
                      ← Previous
                    </button>
                    <span className="matchweek-label tabular-nums">Matchweek {availableMatchweeks[currentMatchweekIndex]}</span>
                    <button
                      className="btn-secondary"
                      onClick={() => setCurrentMatchweekIndex(Math.min(availableMatchweeks.length - 1, currentMatchweekIndex + 1))}
                      disabled={currentMatchweekIndex === availableMatchweeks.length - 1}
                    >
                      Next →
                    </button>
                  </div>
                )}
              </div>

              {fixturesLoading ? (
                <div style={{ textAlign: 'center', padding: '3rem' }}><div className="loader"></div></div>
              ) : fixturesError ? (
                <div className="card" style={{ padding: '2.5rem', textAlign: 'center' }}>
                  <p style={{ color: 'var(--rose-text)', fontWeight: 600, fontSize: 14, margin: '0 0 8px 0' }}>{fixturesError}</p>
                  <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '0 0 16px 0' }}>
                    Target API: <code>{API_URL}</code>
                  </p>
                  <button className="btn-secondary" onClick={() => fetchFixtures(activeLeague)}>
                    Retry Loading Fixtures
                  </button>
                </div>
              ) : fixtures.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  No upcoming fixtures found for this league.
                </div>
              ) : (
                <div className="grid-fixtures">
                  {fixtures
                    .filter(f => f.matchweek === availableMatchweeks[currentMatchweekIndex])
                    .map((fixture, idx) => {
                      const dateObj = new Date(fixture.date);
                      const formattedTime = !isNaN(dateObj.getTime())
                        ? dateObj.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }) + ' · ' + dateObj.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
                        : fixture.date;
                      return (
                        <div key={idx} className="fixture-card" onClick={() => handleFixtureClick(fixture)}>
                          <div className="fixture-meta">
                            <span>{fixture.league.split('-')[1]}</span>
                            <span className="tabular-nums">{formattedTime}</span>
                          </div>
                          <div className="fixture-teams">
                            <div className="fixture-team-row">
                              <div className="fixture-team-info">
                                <img src={getTeamLogo(fixture.home_team)} alt={fixture.home_team} className="logo-sm"
                                  onError={(e) => { e.target.onerror = null; e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fixture.home_team)}&background=1e293b&color=94a3b8&size=120`; }}
                                />
                                {fixture.home_team}
                              </div>
                              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Home</span>
                            </div>
                            <div className="fixture-team-row">
                              <div className="fixture-team-info">
                                <img src={getTeamLogo(fixture.away_team)} alt={fixture.away_team} className="logo-sm"
                                  onError={(e) => { e.target.onerror = null; e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(fixture.away_team)}&background=1e293b&color=94a3b8&size=120`; }}
                                />
                                {fixture.away_team}
                              </div>
                              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Away</span>
                            </div>
                          </div>
                          <button className="fixture-cta">Predict Match</button>
                        </div>
                      );
                    })}
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default App;
