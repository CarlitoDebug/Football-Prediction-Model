import React, { useState } from 'react';

const TeamFormCard = ({ teamName, formData, getTeamLogo }) => {
  const [page, setPage] = useState(0);
  const itemsPerPage = 5;

  if (!formData || !formData.overall) return null;

  const getFormBadgeClass = (result) => {
    switch (result) {
      case 'W': return 'form-badge form-w';
      case 'D': return 'form-badge form-d';
      case 'L': return 'form-badge form-l';
      default:  return 'form-badge pill-neutral';
    }
  };

  const getScoreStyle = (result) => {
    switch (result) {
      case 'W': return { backgroundColor: 'var(--emerald-bg)', color: 'var(--emerald-text)', border: '1px solid var(--emerald-border)' };
      case 'D': return { backgroundColor: 'var(--amber-bg)',   color: 'var(--amber-text)',   border: '1px solid var(--amber-border)' };
      case 'L': return { backgroundColor: 'var(--rose-bg)',    color: 'var(--rose-text)',    border: '1px solid var(--rose-border)' };
      default:  return { backgroundColor: 'var(--bg-subtle)',  color: 'var(--text-secondary)' };
    }
  };

  const getPpgPillClass = (ppg) => {
    if (ppg >= 2.0) return 'pill pill-emerald';
    if (ppg >= 1.0) return 'pill pill-amber';
    return 'pill pill-rose';
  };

  const oStats = formData.overall.stats || {};
  const hStats = formData.home.stats || {};
  const aStats = formData.away.stats || {};

  const statRows = [
    { label: 'Win %',    key: 'win_pct',    format: v => `${v}%` },
    { label: 'AVG',      key: 'avg_goals',  format: v => v.toFixed(2) },
    { label: 'Scored',   key: 'scored',     format: v => v.toFixed(2) },
    { label: 'Conceded', key: 'conceded',   format: v => v.toFixed(2) },
    { label: 'BTTS',     key: 'btts_pct',   format: v => `${v}%` },
    { label: 'CS',       key: 'cs_pct',     format: v => `${v}%` },
    { label: 'FTS',      key: 'fts_pct',    format: v => `${v}%` },
    { label: 'xG',       key: 'xg',         format: v => v.toFixed(2) },
    { label: 'xGA',      key: 'xga',        format: v => v.toFixed(2) },
  ];

  const matches = formData.overall.matches;
  const totalPages = Math.ceil(matches.length / itemsPerPage);
  const paginatedMatches = matches.slice(page * itemsPerPage, (page + 1) * itemsPerPage);

  const groupedMatches = [];
  let currentYear = null;
  paginatedMatches.forEach(match => {
    if (match.year !== currentYear) {
      currentYear = match.year;
      groupedMatches.push({ type: 'header', text: currentYear });
    }
    groupedMatches.push({ type: 'match', data: match });
  });

  const renderFormBadges = (formArray) => {
    const recent = formArray.slice(-5);
    return (
      <div style={{ display: 'flex', gap: 4, justifyContent: 'center' }}>
        {recent.map((result, i) => (
          <span key={i} className={getFormBadgeClass(result)}>{result}</span>
        ))}
      </div>
    );
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
      {/* Light card header — no dark navy banner */}
      <div className="card-header" style={{ padding: '16px 20px', margin: 0, borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 40, height: 40, borderRadius: '50%', border: '1px solid var(--border-subtle)', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <img src={getTeamLogo(teamName)} alt={teamName} className="logo-md" />
          </div>
          <div>
            <div className="card-title" style={{ fontSize: 14 }}>{teamName}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>Team Form &amp; Stats</div>
          </div>
        </div>
      </div>

      {/* Form Table */}
      <div style={{ padding: 0, borderBottom: '1px solid var(--border-subtle)' }}>
        <table className="data-table" style={{ fontSize: 12 }}>
          <thead>
            <tr>
              <th>Form</th>
              <th style={{ textAlign: 'center' }}>Results</th>
              <th style={{ textAlign: 'center' }}>PPG</th>
            </tr>
          </thead>
          <tbody>
            {['overall', 'home', 'away'].map(type => {
              const fData = formData[type];
              return (
                <tr key={type}>
                  <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{type}</td>
                  <td style={{ textAlign: 'center' }}>{renderFormBadges(fData.form)}</td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={getPpgPillClass(fData.ppg)}>{fData.ppg.toFixed(2)}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Stats Table */}
      <div style={{ borderBottom: '1px solid var(--border-subtle)' }}>
        <table className="data-table" style={{ fontSize: 12 }}>
          <thead>
            <tr>
              <th>Stats</th>
              <th style={{ textAlign: 'center' }}>Overall</th>
              <th style={{ textAlign: 'center' }}>Home</th>
              <th style={{ textAlign: 'center' }}>Away</th>
            </tr>
          </thead>
          <tbody>
            {statRows.map((row, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 600 }}>{row.label}</td>
                <td style={{ textAlign: 'center', fontWeight: 700, color: 'var(--brand-accent)' }}>{row.format(oStats[row.key] || 0)}</td>
                <td style={{ textAlign: 'center' }}>{row.format(hStats[row.key] || 0)}</td>
                <td style={{ textAlign: 'center' }}>{row.format(aStats[row.key] || 0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Matches List */}
      <div style={{ maxHeight: 200, overflowY: 'auto', flex: 1 }}>
        {groupedMatches.map((item, idx) => {
          if (item.type === 'header') {
            return (
              <div key={idx} style={{ position: 'sticky', top: 0, background: 'var(--bg-subtle)', padding: '4px 16px', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>
                {item.text}
              </div>
            );
          }
          const m = item.data;
          const dateObj = new Date(m.date);
          const formattedDate = dateObj.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
          return (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', padding: '7px 16px', gap: 8, borderBottom: '1px solid var(--bg-subtle)', background: 'var(--bg-surface)' }}>
              <div style={{ width: 42, fontSize: 10, color: 'var(--text-muted)', fontWeight: 500, flexShrink: 0 }}>{formattedDate}</div>
              <div style={{ flex: 1, fontSize: 12, fontWeight: 500, textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-primary)' }}>{m.home_team}</div>
              <div style={{ flexShrink: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 12, fontVariantNumeric: 'tabular-nums', padding: '2px 8px', borderRadius: 'var(--radius-sm)', minWidth: 44, ...getScoreStyle(m.result) }}>
                  {m.home_goals} - {m.away_goals}
                </div>
              </div>
              <div style={{ flex: 1, fontSize: 12, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{m.away_team}</div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      {matches.length > itemsPerPage && (
        <div style={{ padding: '10px 16px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, background: 'var(--bg-surface)' }}>
          <button
            className="btn-secondary"
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            style={{ padding: '4px 10px', fontSize: 12 }}
          >
            « Prev
          </button>
          <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', fontVariantNumeric: 'tabular-nums' }}>{page + 1} / {totalPages}</span>
          <button
            className="btn-secondary"
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            style={{ padding: '4px 10px', fontSize: 12 }}
          >
            Next »
          </button>
        </div>
      )}
    </div>
  );
};

export default TeamFormCard;
