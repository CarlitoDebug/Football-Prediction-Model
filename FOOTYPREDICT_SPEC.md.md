# FootyPredict — Complete Recovery, Architecture & Soft Light Mode UI Specification

## 1. MANDATORY EXECUTION & SAFETY RULES
You are repairing and redesigning an existing React / Next.js + Vite football analytics application (`FootyPredict` / `Football Analytics Pro`). The previous styling pass broke CSS compilation, caused `<svg>` icons and team logo `<img>` elements to render at full screen width, left dark-mode fragments, and hid/broke fixture views.

**Follow these rules strictly:**
1. **Audit Before Editing:** First inspect `package.json`, `src/main.jsx` (or `src/main.tsx`), `src/App.jsx` (or `src/App.tsx`), `src/index.css`, and all files inside `src/components/` or `src/pages/`.
2. **Use Standard Semantic CSS (No Uncompiled Utility Classes):** Do **NOT** rely on Tailwind utility classes unless you verify Tailwind is actively compiling. Use the explicit semantic CSS classes defined in **Section 2** inside `src/index.css` so styling works 100% deterministically.
3. **Zero Broken Data or State:**
   - **DO NOT** alter API endpoints, `fetch`/`axios` logic, `useState`, `useEffect`, or mathematical/statistical formulas (xG, Poisson scorelines, H2H, PPG, Over/Under).
   - **DO NOT** invent new data fields on objects (e.g., do not add `fixture.fairOdds` if the fixture object does not have `fairOdds`). Bind only to the existing object properties already used in the JSX.
   - **DO NOT** delete, comment out, or hide any view, tab, dropdown, button, table, or pagination control.
4. **Purge All Dark-Mode Leftovers:** Search the entire codebase for `#0B0F17`, `#131A26`, `#0F172A`, `#1E293B` backgrounds, `bg-slate-900`, `bg-gray-900`, or inline dark `style={{ background: ... }}` attributes and replace them with the Soft Light Mode classes below.

---

## 2. MASTER STYLESHEET (`src/index.css`)
Replace `src/index.css` with the complete stylesheet below and ensure `import './index.css'` is present at the top of `src/main.jsx` (or `src/main.tsx`). This fixes broken sizing, giant SVGs/logos, clipped sidebar text, and establishes a calm, low-glare **Soft Light Mode** inspired by Road2Sushi.

```css
/* ==========================================================================
   1. DESIGN TOKENS (SOFT LIGHT MODE — LOW GLARE, QUANTITATIVE CLARITY)
   ========================================================================== */
:root {
  --bg-canvas: #F4F5F7;           /* Matte off-white page background */
  --bg-surface: #FAFBFD;          /* Soft elevated card & sidebar surface */
  --bg-subtle: #F1F3F6;           /* Inner wells, table headers, hover fills */
  --border-subtle: #E2E8F0;       /* Crisp 1px card & divider borders */
  --border-strong: #CBD5E1;       /* Input & interactive hover borders */

  --text-primary: #1E293B;        /* Soft charcoal primary text (no harsh black) */
  --text-secondary: #475569;      /* Muted slate secondary text */
  --text-muted: #94A3B8;          /* Metadata, timestamps, disclaimers */

  --brand-primary: #1E293B;       /* Active nav & primary CTA fill */
  --brand-accent: #2563EB;        /* Subtle analytical highlight */

  --emerald-bg: #ECFDF5;
  --emerald-text: #047857;
  --emerald-border: #A7F3D0;
  --emerald-bar: #10B981;

  --amber-bg: #FFFBEB;
  --amber-text: #B45309;
  --amber-border: #FDE68A;
  --amber-bar: #F59E0B;

  --rose-bg: #FFF1F2;
  --rose-text: #BE123C;
  --rose-border: #FECDD3;
  --rose-bar: #F43F5E;

  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-card: 0 1px 2px rgba(15, 23, 42, 0.03), 0 1px 1px rgba(15, 23, 42, 0.02);
}

/* ==========================================================================
   2. GLOBAL RESETS & SVG / IMAGE SAFETY CONSTRAINTS
   ========================================================================== */
*, *::before, *::after {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-canvas);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* Prevent raw SVGs from ever expanding to full screen width */
svg {
  width: 18px;
  height: 18px;
  max-width: 24px;
  max-height: 24px;
  flex-shrink: 0;
  vertical-align: middle;
}

/* Prevent raw team logos from expanding to full screen width */
img {
  max-width: 100%;
  height: auto;
  display: inline-block;
}

.logo-xs { width: 16px; height: 16px; object-fit: contain; flex-shrink: 0; }
.logo-sm { width: 22px; height: 22px; object-fit: contain; flex-shrink: 0; }
.logo-md { width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; }
.logo-lg { width: 44px; height: 44px; object-fit: contain; flex-shrink: 0; }

.tabular-nums {
  font-variant-numeric: tabular-nums;
}

/* ==========================================================================
   3. APP SHELL, SIDEBAR & COMPACT TOP HEADER
   ========================================================================== */
.app-shell {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background-color: var(--bg-canvas);
}

.sidebar {
  width: 248px;
  flex-shrink: 0;
  background-color: var(--bg-surface);
  border-right: 1px solid var(--border-subtle);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px 20px 12px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.sidebar-section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  padding: 16px 12px 6px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
  outline: none;
}

.nav-item:hover {
  background-color: var(--bg-subtle);
  color: var(--text-primary);
}

.nav-item.active {
  background-color: var(--brand-primary);
  color: #FFFFFF;
  font-weight: 600;
}

.main-wrapper {
  flex: 1;
  min-width: 0;
  padding: 24px 32px 48px 32px;
}

.main-container {
  max-width: 1360px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Compact Top Bar (Replaces oversized blue hero banner) */
.top-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.top-header-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.top-header-subtitle {
  margin: 2px 0 0 0;
  font-size: 12.5px;
  color: var(--text-muted);
}

.top-header-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* ==========================================================================
   4. UNIFIED CARDS, GRIDS & CONTROLS
   ========================================================================== */
.card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-card);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--bg-subtle);
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.grid-fixtures {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(275px, 1fr));
  gap: 20px;
}

@media (max-width: 1024px) {
  .grid-3 { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .app-shell { flex-direction: column; }
  .sidebar { width: 100%; height: auto; position: static; border-right: none; border-bottom: 1px solid var(--border-subtle); }
  .main-wrapper { padding: 16px; }
}

/* Buttons & Selects */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: var(--radius-md);
  background-color: var(--brand-primary);
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid var(--brand-primary);
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.btn-primary:hover { opacity: 0.9; }

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  background-color: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.btn-secondary:hover {
  background-color: var(--bg-subtle);
  color: var(--text-primary);
}

.select-input {
  padding: 9px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  background-color: #FFFFFF;
  color: var(--text-primary);
  font-size: 13.5px;
  font-weight: 500;
  min-width: 190px;
  outline: none;
}

.select-input:focus {
  border-color: var(--border-strong);
}

/* Segmented Filter Tabs */
.tab-bar {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 4px;
  background-color: #E8ECF1;
  border-radius: 10px;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn.active {
  background-color: #FFFFFF;
  color: var(--text-primary);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}

/* ==========================================================================
   5. FIXTURE CARDS (ROAD2SUSHI SCANNABLE HIERARCHY)
   ========================================================================== */
.fixture-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow-card);
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.fixture-card:hover {
  border-color: var(--border-strong);
}

.fixture-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  padding-bottom: 10px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--bg-subtle);
}

.fixture-teams {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.fixture-team-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.fixture-team-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.fixture-cta {
  margin-top: 14px;
  width: 100%;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  background-color: var(--bg-subtle);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 12.5px;
  font-weight: 600;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.fixture-card:hover .fixture-cta,
.fixture-cta:hover {
  background-color: var(--brand-primary);
  border-color: var(--brand-primary);
  color: #FFFFFF;
}

/* ==========================================================================
   6. CLEAN DATA TABLES & MUTED SEMANTIC PILLS (NO FULL-ROW NEON FILLS)
   ========================================================================== */
.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}

.data-table th {
  background-color: var(--bg-subtle);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
  white-space: nowrap;
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--bg-subtle);
  color: var(--text-primary);
  background-color: var(--bg-surface);
  white-space: nowrap;
}

.data-table tr:hover td {
  background-color: #F8FAFC;
}

/* Compact Semantic Pills */
.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.pill-emerald { background-color: var(--emerald-bg); color: var(--emerald-text); border: 1px solid var(--emerald-border); }
.pill-amber   { background-color: var(--amber-bg);   color: var(--amber-text);   border: 1px solid var(--amber-border); }
.pill-rose    { background-color: var(--rose-bg);    color: var(--rose-text);    border: 1px solid var(--rose-border); }
.pill-neutral { background-color: var(--bg-subtle);  color: var(--text-secondary); border: 1px solid var(--border-subtle); }

/* W / D / L Form Mini-Badges */
.form-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}
.form-w { background-color: var(--emerald-bg); color: var(--emerald-text); border: 1px solid var(--emerald-border); }
.form-d { background-color: var(--amber-bg);   color: var(--amber-text);   border: 1px solid var(--amber-border); }
.form-l { background-color: var(--rose-bg);    color: var(--rose-text);    border: 1px solid var(--rose-border); }

/* Micro-Disclaimer Footer */
.micro-disclaimer {
  margin-top: 12px;
  font-size: 11.5px;
  color: var(--text-muted);
}
```

---

## 3. COMPLETE FEATURE & VIEW INVENTORY (ALL MUST REMAIN VISIBLE)
Verify that all 4 areas below are wired up, rendered cleanly, and never hidden:

1. **Left Sidebar (`<aside className="sidebar">`):**
   - Brand header (`FootyPredict`)
   - Primary links (`Dashboard`, `Predictions`) with `nav-item` and conditional `active` class.
   - Collapsible `LEAGUE STATS` section (`Premier League`, `La Liga`, `Bundesliga`) — clicking any league switches to the League Stats view for that league without clipping any text.
2. **League Stats View:**
   - League Header + Season badge (`Season 2627`).
   - Full Standings `.data-table` (`#`, `TEAM` with `.logo-sm`, `MP`, `W`, `D`, `L`, `GF`, `GA`, `GD`, `PTS`, `LAST 5` using `.form-badge`, `PPG`, `CS`, `BTTS`, `XGF`, `1.5+`, `2.5+`, `AVG`).
   - `.grid-3` Summary Cards (`MATCH RESULTS` stacked bar, `FREQUENT SCORELINES` horizontal bars, `TOTAL GOALS (FULL-TIME)` horizontal bars).
   - `OVER +` / `UNDER -` Goal Line Distribution `.data-table` (`Over 0.5` through `Over 4.5+`).
3. **Predictions / Incoming Fixtures View:**
   - `.tab-bar` League Filter Tabs (`All Leagues`, `English Premier League`, `La Liga`, `Bundesliga`).
   - `Incoming Fixtures` header bar + Matchweek Pagination (`← Previous`, `Matchweek X`, `Next →`) using `.btn-secondary`.
   - `.grid-fixtures` grid of `.fixture-card` items. Each card displays League, Date/Time (`.tabular-nums`), Home Team (`.logo-sm` + name), Away Team (`.logo-sm` + name), and `.fixture-cta` (`Predict Match`) preserving the exact `onClick` handler that opens the Match Prediction Detail view.
4. **Match Prediction Detail View:**
   - **Match Selector Card (`.card`):** `Home Team` `<select className="select-input">`, `VS`, `Away Team` `<select className="select-input">`, `Generate Prediction` (`.btn-primary`), and `← Back to Fixtures` (`.btn-secondary`).
   - **Top Analytics Row (`.grid-3`):**
     - `Match Overview` (Home xG vs Away xG in `.tabular-nums` + 3-way probability stacked bar using `--brand-accent`, `--text-muted`, and `--emerald-bar`).
     - `Top 3 Exact Scores` (clean rows with `.pill-neutral` / `.pill-emerald` percentage badges).
     - `Expected Corners` (Home & Away corner projections in `.bg-subtle` boxes + `Total Over 7.5` to `12.5` clean rows).
   - **`Head to Head Statistics` (`.card`):**
     - Total matches, Win/Draw bar, summary paragraph.
     - 6 uniform metric tiles (`Over 1.5`, `Over 2.5`, `Over 3.5`, `BTTS`, Home `Clean Sheets`, Away `Clean Sheets`) styled with clean `1px solid var(--border-subtle)` borders and thin `4px` progress bars (**remove** thick bright green/yellow/red bottom borders).
     - `Recent Matches` 4-column sub-grid with `.logo-xs` crests.
   - **Team Comparison Row (3-column layout: `1fr 260px 1fr`):**
     - Left & Right `Team Form & Stats` `.card` components: use a clean light `.card-header` with `.logo-md` (**remove** dark navy header banners), `.form-badge` W/D/L rows, stats table (`Win %` through `xGA`), recent match history, and `« Prev 1 / 2 Next »` pagination.
     - Center `Points Per Game` comparison wrapped inside a proper `.card` container so it never floats unstyled.
   - **`Over 2.5 & BTTS Predictions` Matrix (`.card`):**
     - Use `.data-table` with clean `#FAFBFD` rows (**remove** full-row red/yellow/green background fills). Wrap the percentage values in `.pill-emerald` (`>= 65%`), `.pill-amber` (`45%–64%`), or `.pill-neutral` (`< 45%`).
     - Add `<p className="micro-disclaimer">Model probabilities are statistical estimates derived from historical xG and Poisson distributions.</p>` at the bottom of the card.

---

## 4. FINAL SELF-VERIFICATION BEFORE RESPONDING
Before finishing your edits, verify all 5 checks:
1. Are there any remaining Tailwind utility classes (`flex`, `grid-cols-3`, `bg-slate-900`, `w-64`, etc.) on elements where Tailwind is not active? Replace them with the semantic classes in Section 2.
2. Do all `<svg>` icons render at `18px–24px` and all team logos render at `16px–44px`?
3. Is the giant blue `"Football Analytics Pro"` banner replaced with the compact `.top-header`?
4. Do all sidebar links (`Dashboard`, `Predictions`, `Premier League`, `La Liga`, `Bundesliga`) switch views properly without horizontal text clipping?
5. Do all fixture cards render in a multi-column `.grid-fixtures` layout and open the Match Prediction Detail view when clicked?