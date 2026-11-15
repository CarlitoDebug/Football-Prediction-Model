import React, { useState, useEffect } from 'react';

const LeagueStats = ({ activeLeague, getTeamLogo }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/league-stats?league=${encodeURIComponent(activeLeague)}`);
        if (!response.ok) {
          throw new Error('Failed to fetch league stats');
        }
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (activeLeague) {
      fetchStats();
    }
  }, [activeLeague]);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        <div className="loader" style={{ marginBottom: 12 }}></div>
        <span style={{ fontSize: 12, fontWeight: 500 }}>Loading league statistics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        {error}
      </div>
    );
  }

  if (!stats) return null;

  // Rank badge: semantic pill classes
  const getRankBadgeClass = (rank) => {
    if (rank <= 4) return 'pill pill-emerald';        // UCL
    if (rank === 5) return 'pill pill-amber';          // UEL
    if (rank === 6) return 'pill pill-neutral';        // UECL
    if (rank >= stats.table.length - 2) return 'pill pill-rose'; // Relegation
    return 'pill pill-neutral';
  };

  // Form badge: semantic form-badge classes
  const getFormBadgeClass = (f) => {
    if (f === 'W') return 'form-badge form-w';
    if (f === 'D') return 'form-badge form-d';
    if (f === 'L') return 'form-badge form-l';
    return 'form-badge form-d';
  };

  const leagueTitle = activeLeague.includes('-') ? activeLeague.split('-')[1] : activeLeague;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, paddingBottom: 48 }}>

      {/* Compact Header */}
      <div style={{
        display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between',
        gap: 12, borderBottom: '1px solid var(--border-subtle)', paddingBottom: 16
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              {leagueTitle} Standings
            </h2>
            <span className="pill pill-neutral tabular-nums">Season {stats.season}</span>
          </div>
          <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--text-muted)' }}>
            Comprehensive team efficiency, xG, and hitting rates.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 11, color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--emerald-text)', display: 'inline-block' }}></span>
            UCL (1–4)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--amber-text)', display: 'inline-block' }}></span>
            UEL (5)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--rose-text)', display: 'inline-block' }}></span>
            Relegation
          </span>
        </div>
      </div>

      {/* Main Standings Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ whiteSpace: 'nowrap' }}>
            <thead>
              <tr>
                <th>#</th>
                <th>Club</th>
                <th style={{ textAlign: 'center' }}>MP</th>
                <th style={{ textAlign: 'center' }}>W</th>
                <th style={{ textAlign: 'center' }}>D</th>
                <th style={{ textAlign: 'center' }}>L</th>
                <th style={{ textAlign: 'center', color: 'var(--emerald-text)' }}>GF</th>
                <th style={{ textAlign: 'center', color: 'var(--rose-text)' }}>GA</th>
                <th style={{ textAlign: 'center' }}>GD</th>
                <th style={{ textAlign: 'center', fontWeight: 700, color: 'var(--text-primary)' }}>Pts</th>
                <th style={{ textAlign: 'center' }}>Last 5</th>
                <th style={{ textAlign: 'center' }}>PPG</th>
                <th style={{ textAlign: 'center' }}>CS%</th>
                <th style={{ textAlign: 'center' }}>BTTS%</th>
                <th style={{ textAlign: 'center' }}>xGF</th>
                <th style={{ textAlign: 'center' }}>1.5+</th>
                <th style={{ textAlign: 'center' }}>2.5+</th>
                <th style={{ textAlign: 'center' }}>AVG</th>
              </tr>
            </thead>
            <tbody>
              {stats.table.map((row) => (
                <tr key={row.team}>
                  <td>
                    <span className={getRankBadgeClass(row.rank)} style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', minWidth: 20, height: 20, fontSize: 10 }}>
                      {row.rank}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <img
                        src={getTeamLogo(row.team)}
                        alt={row.team}
                        className="logo-sm"
                        onError={(e) => { e.target.onerror = null; e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(row.team)}&background=1e293b&color=94a3b8&size=120&rounded=true`; }}
                      />
                      <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{row.team}</span>
                    </div>
                  </td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.mp}</td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.w}</td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.d}</td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.l}</td>
                  <td style={{ textAlign: 'center', color: 'var(--emerald-text)', fontWeight: 600 }} className="tabular-nums">{row.gf}</td>
                  <td style={{ textAlign: 'center', color: 'var(--rose-text)', fontWeight: 500 }} className="tabular-nums">{row.ga}</td>
                  <td style={{ textAlign: 'center', fontWeight: 500, color: 'var(--text-secondary)' }} className="tabular-nums">
                    {row.gd > 0 ? `+${row.gd}` : row.gd}
                  </td>
                  <td style={{ textAlign: 'center', fontWeight: 700, color: 'var(--text-primary)' }} className="tabular-nums">{row.pts}</td>
                  <td style={{ textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: 3, justifyContent: 'center' }}>
                      {row.form.map((f, i) => (
                        <span key={i} className={getFormBadgeClass(f)} style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 16, height: 16, fontSize: 9 }}>
                          {f}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className="pill pill-neutral tabular-nums">{row.ppg.toFixed(2)}</span>
                  </td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.cs_pct}%</td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.btts_pct}%</td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.xgf.toFixed(2)}</td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.over_15}%</td>
                  <td style={{ textAlign: 'center' }} className="tabular-nums">{row.over_25}%</td>
                  <td style={{ textAlign: 'center', fontWeight: 600, color: 'var(--text-primary)' }} className="tabular-nums">{row.avg.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom 3-column grid */}
      <div className="grid-3">

        {/* League Outcome Distribution */}
        <div className="card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div className="card-header">
            <span className="card-title">League Outcome Distribution</span>
          </div>
          <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div className="odds-bar-container" style={{ height: 32 }}>
              <div
                className="odds-segment odds-home"
                style={{ width: `${stats.metrics.home_win_pct}%`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 600 }}
              >
                {stats.metrics.home_win_pct}%
              </div>
              <div
                className="odds-segment odds-draw"
                style={{ width: `${stats.metrics.draw_pct}%`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 600 }}
              >
                {stats.metrics.draw_pct}%
              </div>
              <div
                className="odds-segment odds-away"
                style={{ width: `${stats.metrics.away_win_pct}%`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 600 }}
              >
                {stats.metrics.away_win_pct}%
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12, fontSize: 11, fontWeight: 500, color: 'var(--text-secondary)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--emerald-text)', display: 'inline-block' }}></span>
                Home Win
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--amber-text)', display: 'inline-block' }}></span>
                Draw
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--rose-text)', display: 'inline-block' }}></span>
                Away Win
              </span>
            </div>
          </div>
        </div>

        {/* Most Frequent Scorelines */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="card-header">
            <span className="card-title">Most Frequent Scorelines</span>
          </div>
          <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
            {stats.frequent_scores.slice(0, 5).map(fs => (
              <div key={fs.score} style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 12 }}>
                <div style={{ width: 36, fontWeight: 700, color: 'var(--text-primary)' }} className="tabular-nums">{fs.score}</div>
                <div style={{ flex: 1, background: 'var(--bg-subtle)', borderRadius: 999, height: 6, overflow: 'hidden', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ background: 'var(--text-secondary)', height: '100%', borderRadius: 999, width: `${(fs.pct / stats.frequent_scores[0].pct) * 100}%` }}></div>
                </div>
                <div style={{ width: 100, textAlign: 'right', flexShrink: 0 }} className="tabular-nums">
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{fs.pct}%</span>{' '}
                  <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>({fs.count})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Total Goals */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="card-header">
            <span className="card-title">Total Goals (Full-Time)</span>
          </div>
          <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
            {stats.frequent_goals.slice(0, 5).map(fg => (
              <div key={fg.goals} style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 12 }}>
                <div style={{ width: 52, fontWeight: 500, color: 'var(--text-secondary)' }}>{fg.goals} Goals</div>
                <div style={{ flex: 1, background: 'var(--bg-subtle)', borderRadius: 999, height: 6, overflow: 'hidden', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ background: 'var(--text-secondary)', height: '100%', borderRadius: 999, width: `${(fg.pct / stats.frequent_goals[0].pct) * 100}%` }}></div>
                </div>
                <div style={{ width: 100, textAlign: 'right', flexShrink: 0 }} className="tabular-nums">
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{fg.pct}%</span>{' '}
                  <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>({fg.count})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Goal Line Distribution (Over / Under) */}
      {stats.ou && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="card-header" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', margin: 0 }}>
            <span className="card-title">Goal Line Distribution (Over / Under)</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Goal Line</th>
                  <th style={{ textAlign: 'center' }}>Over %</th>
                  <th style={{ textAlign: 'center' }}>Under %</th>
                  <th style={{ minWidth: 200 }}>Distribution</th>
                </tr>
              </thead>
              <tbody>
                {[0.5, 1.5, 2.5, 3.5, 4.5].map((threshold) => {
                  const overPct = stats.ou[`over_${threshold}`] ?? 0;
                  const underPct = stats.ou[`under_${threshold}`] ?? (100 - overPct);
                  const pillClass = overPct >= 65 ? 'pill pill-emerald' : overPct >= 45 ? 'pill pill-amber' : 'pill pill-neutral';
                  return (
                    <tr key={threshold}>
                      <td style={{ fontWeight: 600 }}>Over / Under {threshold}</td>
                      <td style={{ textAlign: 'center' }}>
                        <span className={pillClass}>{overPct}%</span>
                      </td>
                      <td style={{ textAlign: 'center' }} className="tabular-nums">
                        {underPct}%
                      </td>
                      <td>
                        <div style={{ display: 'flex', width: '100%', height: 10, borderRadius: 5, overflow: 'hidden', background: 'var(--bg-subtle)' }}>
                          <div style={{ width: `${overPct}%`, background: 'var(--emerald-bar)' }}></div>
                          <div style={{ width: `${underPct}%`, background: 'var(--border-strong)' }}></div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};

export default LeagueStats;
