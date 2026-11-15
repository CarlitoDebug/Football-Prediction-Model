import React from 'react';

const BttsPredictionsCard = ({ data, homeTeam, awayTeam }) => {
  if (!data || !data.home_rates || !data.away_rates || !data.prediction) return null;

  const { home_rates, away_rates, prediction } = data;

  const rows = [
    { label: 'Over 0.5',          key: 'over_0_5' },
    { label: 'Over 1.5',          key: 'over_1_5' },
    { label: 'Over 2.5',          key: 'over_2_5' },
    { label: 'Over 3.5',          key: 'over_3_5' },
    { label: 'Over 4.5',          key: 'over_4_5' },
    { label: 'BTTS',              key: 'btts' },
    { label: 'BTTS & Win',        key: 'btts_and_win' },
    { label: 'BTTS & Draw',       key: 'btts_and_draw' },
    { label: 'BTTS & Over 2.5',   key: 'btts_and_o25' },
    { label: 'BTTS No & Over 2.5', key: 'btts_no_and_o25' },
  ];

  const formatPct = (val) => `${Math.round(val * 100)}%`;

  const getPillClass = (val) => {
    const pct = val * 100;
    if (pct >= 65) return 'pill pill-emerald';
    if (pct >= 45) return 'pill pill-amber';
    return 'pill pill-neutral';
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            Over 2.5 &amp; BTTS Predictions
            <span style={{ fontWeight: 400, color: 'var(--text-muted)', fontSize: 13, marginLeft: 8 }}>How many goals in this match?</span>
          </h2>
          <p style={{ margin: '4px 0 0 0', fontSize: 12, color: 'var(--text-secondary)' }}>
            {homeTeam} and {awayTeam}'s Over 0.5 ~ 4.5 and BTTS data.
          </p>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Match Goals</th>
              <th style={{ textAlign: 'center' }}>{homeTeam}</th>
              <th style={{ textAlign: 'center' }}>{awayTeam}</th>
              <th style={{ textAlign: 'center' }}>Prediction</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => {
              const hVal = home_rates[row.key] || 0;
              const aVal = away_rates[row.key] || 0;
              const pVal = prediction[row.key] || 0;
              return (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>{row.label}</td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={getPillClass(hVal)}>{formatPct(hVal)}</span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={getPillClass(aVal)}>{formatPct(aVal)}</span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={getPillClass(pVal)} style={{ fontWeight: 700 }}>{formatPct(pVal)}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="micro-disclaimer">
        Model probabilities are statistical estimates derived from historical xG and Poisson distributions.
      </p>
    </div>
  );
};

export default BttsPredictionsCard;
