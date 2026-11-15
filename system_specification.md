# Football Prediction Model - Full System Specification

## Overview
The Football Prediction Model is a comprehensive machine learning and statistical system designed to forecast football match outcomes (Home Win, Draw, Away Win), exact scores, corner counts, and Over/Under/BTTS markets. The system utilizes a hybrid approach, combining stacked ensemble machine learning models for Expected Goals (xG) prediction with a Dixon-Coles adjusted Poisson distribution to derive exact match probabilities.

> [!NOTE]
> **Terminology Clarification:** Throughout this system, "xG" refers *exclusively* to Understat's shot-model output, aggregated at the match level. We are not building a custom shot-tracking model; we are predicting Understat's xG values.

---

## Quick Start & How to Run
The easiest way to start the system, update all data, and launch the dashboard is using the automated startup script.

1.  **Launch the System:** Double-click the `start.bat` file located in the root of the project (or run `.\start.bat` in your terminal).
2.  **What it does:**
    *   Automatically runs `data_ingestion.py` to scrape the latest odds, expected goals (xG), and MatchHistory.
    *   Runs `feature_engineering.py` to recalculate the dynamic Elo, Points Per Game (PPG), and rolling form metrics based on the fresh data.
    *   Starts the Flask backend API server (`api.py`) on port 8000 in a new window.
    *   Starts the React frontend development server (`npm run dev`) in a new window and automatically opens your browser to `http://localhost:5173`.
3.  **Manual Execution (Alternative):** If you prefer to run the components manually without the script, execute the following commands in order:
    ```bash
    python data_ingestion.py
    python feature_engineering.py
    python api.py
    # In a separate terminal:
    cd frontend && npm run dev
    ```

---

## 1. Data Ingestion (`data_ingestion.py`, `check_bundesliga.py`)
The data ingestion pipeline handles the automated fetching of comprehensive football statistics from multiple sources.
*   **Data Sources:**
    *   **Understat:** via `soccerdata` package. Provides match schedules, detailed team match statistics (xG, PPDA, deep completions), and player-level match statistics.
    *   **MatchHistory:** via `soccerdata` package. Provides traditional match statistics including corners, shots, shots on target, and fouls.
    *   **ClubElo:** Historical team Elo ratings (when applicable).
*   **Scope:** Configured to fetch data for the English Premier League (`ENG-Premier League`), Spanish La Liga (`ESP-La Liga`), and German Bundesliga (`GER-Bundesliga`).
*   **Timeframe:** Covers multiple seasons from 2021-2022 through to 2026-2027.
*   **Storage:** Saves raw data locally as CSV files in the `data/` directory (`schedule.csv`, `match_stats.csv`, `match_history.csv`).
*   **Utilities:** `check_bundesliga.py` is an auxiliary script to verify Bundesliga schedule fetch limits independently.

---

## 2. Feature Engineering (`feature_engineering.py`)
This module transforms raw data into a rich set of predictive features, ensuring zero data leakage by strictly using rolling and shifted statistics prior to match kickoff.

*   **Team-Level Form & Rolling Statistics (5-match decayed rolling average):**
    *   Expected Goals: `rolling_xg_for`, `rolling_xg_against`
    *   Non-Penalty Expected Goals: `rolling_np_xg_for`, `rolling_np_xg_against`
    *   Defensive Intensity: `rolling_ppda_for`, `rolling_ppda_against` (Passes allowed Per Defensive Action)
    *   Attacking Penetration: `rolling_deep_completions_for`, `rolling_deep_completions_against`
    *   Results Form: `rolling_ppg` (Points Per Game), `rolling_xPoints` (Expected Points)
    *   Goal Difference Form: `rolling_gd`
*   **Physical Fatigue Metrics:**
    *   `rest_days`: Number of days since the team's last match (capped at 30).
    *   `fatigue_index`: Total number of matches the team has played in the previous 14 days.
*   **Advanced Dynamic Metrics:**
    *   **Elo Rating System:** A custom implementation tracking `home_elo`, `away_elo`, `elo_diff`, and short-term momentum. 
        *   **Dynamic Home Field Advantage (HFA):** Fitted directly per-league using Maximum Likelihood Estimation (MLE) against historical match outcomes with an Exponential Weighted Moving Average (EWMA, half-life=30 days) decay to prevent cutoff cliffs.
        *   **Margin of Victory Scaling:** Updates are scaled by `sqrt(abs(goal_diff))` to reward dominant performances.
    *   **Strength of Schedule (SoS) Adjusted xG:** Adjusts a team's recent xG based on the Elo rating of their opponents over the last 5 matches, applying an exponential decay weight (`sos_xg_for`, `sos_xg_against`).
    *   **Head-to-Head (H2H) History:** Time-decayed win and draw rates between the specific matchup based on up to 10 previous encounters.
    *   **Attack/Defense Interaction:** Explicit attack/defense lambda feature with shrinkage applying global league averages against a team's rolling metrics.

---

## 3. Corner Prediction Pipeline (`corner_pipeline.py`)
An independent pipeline specifically dedicated to forecasting the number of corner kicks in a match.
*   **Features:** Calculates 5-match rolling averages for `corners_for`, `corners_against`, and `sot_for` (shots on target) for both the home and away teams.
*   **Modeling & Overdispersion Detection:** 
    *   Automatically calculates the variance-to-mean ratio of historical corner counts.
    *   If variance/mean > 1.05 (overdispersion), it trains XGBoost regressors using a Tweedie objective (`reg:tweedie`), running a K-Fold grid search to optimize the `tweedie_variance_power` hyperparameter.
    *   If no overdispersion is detected, it falls back to a standard Poisson objective (`count:poisson`).

> [!NOTE]
> **Corner Pipeline Ceiling**: Corner kicks have a significantly higher noise-to-signal ratio than goals. Factors like tactical fouls, time-wasting, and one-off spells of pressure make corners inherently noisier. This model serves as an estimate but is expected to have a lower predictive ceiling compared to the Match Outcome goals pipeline.

---

## 4. Match Outcome Modeling Pipeline (`model_pipeline.py`)
The core prediction engine uses a Stacking Ensemble approach followed by a statistical distribution adjustment.

*   **Target Variable Clarification:** The base models are trained specifically to predict *Understat's post-match xG* for a given fixture, rather than actual full-time goals. This isolates the model from variance in finishing skill and luck.
*   **Base Models (Poisson Regressors):** For both Home xG and Away xG, four independent machine learning models are trained using Poisson loss functions to maximize ensemble diversity:
    *   `LGBMRegressor` (LightGBM)
    *   `XGBRegressor` (XGBoost)
    *   `CatBoostRegressor` (CatBoost)
    *   `PoissonRegressor` (Generalized Linear Model from scikit-learn)
*   **Meta-Model (Stacking):**
    *   Out-of-fold (OOF) predictions are generated using 5-Fold Cross Validation.
    *   A `Ridge` regression model acts as the meta-model, combining predictions from the tree ensembles and the GLM to output a final refined Expected Goals (xG) figure for both teams.
*   **Dixon-Coles Adjustment:**
    *   The predicted xG values are fed into a Poisson distribution to generate a probability matrix of exact scores (up to 6 goals per team).
    *   A Dixon-Coles adjustment is applied to correct the standard Poisson model's under-prediction of low-scoring matches (0-0, 1-0, 0-1, 1-1).
    *   The Dixon-Coles dependency parameter (`rho`) is optimized dynamically using `scipy.optimize.minimize` to minimize the overall Log-Loss against true 3-way match outcomes.
*   **Outputs & Calibration:** 
    *   Evaluates overall Log-Loss and Accuracy.
    *   Evaluates ordinal accuracy using **Ranked Probability Score (RPS)**, which properly rewards "near-misses" (e.g. predicting a Draw when the actual outcome is a Home Win).
    *   Evaluates **Draw Calibration** specifically using Brier Score across Home Win, Draw, and Away Win classes.
    *   Saves the trained models and optimal `rho` to the `models/` directory.

---

## 5. Prediction Engine & Inference (`predict.py`)
A Command-Line Interface (CLI) application and backend engine used to predict upcoming fixtures.
*   **Usage:** `python predict.py "Home Team" "Away Team"`
*   **Detailed UI Computations:**
    *   **Match Probabilities (Home, Draw, Away):** The predicted Home xG and Away xG are fed into `scipy.stats.poisson.pmf` to build a 6x6 probability matrix (0 to 5 goals). The Dixon-Coles `tau` correction factors are applied to the 0-0, 1-0, 0-1, and 1-1 cells using the optimized `rho` parameter. The matrix is then normalized to sum to 1. Finally, `np.tril` (lower triangle) is summed for the Home Win probability, `np.diag` (diagonal) for the Draw probability, and `np.triu` (upper triangle) for the Away Win probability.
    *   **Top 3 Exact Scores:** The system iterates over all 36 combinations in the 6x6 adjusted probability matrix, extracts the individual probability of each exact score (e.g., 2-1), sorts the list in descending order, and extracts the top 3 highest probabilities to display on the dashboard.
    *   **Expected Corners & Market Probabilities:** The XGBoost corner models output `exp_home_corners` and `exp_away_corners`. These are summed to create `exp_total_corners`. To calculate the probability of the "Over k.5" markets (e.g., Over 9.5), the system uses the Poisson Cumulative Distribution Function: `1 - scipy.stats.poisson.cdf(k, exp_total_corners)`.
    *   **Over/Under & BTTS Slicing:** By creating masks over the 6x6 Poisson probability matrix, the system extracts precise probabilities for Both Teams to Score (BTTS), BTTS & Win/Draw combinations, and all Over/Under goal markets (0.5 to 4.5).
    *   **Team Hit Rates:** Calculates historical occurrence rates (hit rates) for Over/Under and BTTS markets over the team's last 20 matches.
    *   **Team Form & PPG:** The `get_team_form()` function extracts the last 5 completed matches from `schedule.csv` for both teams. It dynamically filters these into three subsets: Overall, Home matches only, and Away matches only. For each subset, it iterates through the results, awarding 3 points for a Win, 1 for a Draw, and 0 for a Loss. The W/D/L badges are reversed to display chronologically (oldest to newest), and the Points Per Game (PPG) is calculated as `Total Points / Number of Matches`.

---

## 6. Backtesting & Validation (`backtest_2526_walk_forward.py`, `backtest.py`)
A rigorous backtesting suite designed to simulate real-world betting conditions and calculate Expected Value (EV).
*   **Methodologies:** 
    *   `backtest_2526_walk_forward.py`: Strict Zero-Leakage Walk-Forward Evaluation iteratively training through an entire season.
    *   `backtest.py`: Fast validation script on specific matchweeks to generate localized reporting (e.g. `matchweek_1_backtest.md`).
*   **Value Betting Strategy Simulation (+EV Engine):**
    *   **Closing Line Value (CLV) Extraction:** Extracts the sharpest available closing odds using a 3-tier fallback system: Pinnacle Close (`PSCH` / `PSCD` / `PSCA`) -> Market Average Close (`AvgCH` / `AvgCD` / `AvgCA`) -> Pre-match Average Fallback (`AvgH` / `AvgD` / `AvgA`).
    *   **De-vigging:** Removes the bookmaker's overround (vigorish) proportionally from the closing odds to calculate the true *fair implied probabilities*.
    *   **Expected Value (Edge):** Calculates true edge: `Model_Probability - Fair_Implied_Probability`.
    *   Simulates placing a flat bet ($100) on outcomes where the true edge exceeds a defined threshold (e.g., > 5%).
*   **Reporting:** Generates comprehensive markdown reports detailing total games processed, overall prediction accuracy, total bets placed, total amount staked, total profit/loss, and Return on Investment (ROI).

---

## 7. Web API & Backend Service (`api.py`)
A lightweight Flask backend that bridges the prediction engine with the user interface.
*   **Endpoints:**
    *   `/api/teams`: Returns a sorted list of all unique teams available in the dataset, mapped via `team_mapping.json`.
    *   `/api/fixtures`: Reads `schedule.csv`, identifies unplayed games (`is_result == False`), and groups them into chronological matchweeks (using `iso_week` logic). Supports filtering by specific leagues.
    *   `/api/predict`: Dynamically invokes `predict.py` logic on the fly when given a `home_team` and `away_team` parameter, returning JSON-formatted probabilities, exact scores, corners, BTTS slicing, and form data.
    *   `/api/h2h`: Returns historical head-to-head match history between two teams, including a goals summary (total goals, clean sheets, over X.5, BTTS) and a list of recent matches.
    *   `/api/league-stats`: Computes and returns the dynamic league table for the requested league's latest season. It includes ranks, points, PPG, goal differences, BTTS/Clean Sheet percentages, xGF, Over 1.5/2.5 percentages, and league-wide score/goal distribution metrics.
*   **Integration:** Uses `flask_cors` to securely communicate with the React frontend.

---

## 8. Frontend Dashboard UI (`frontend/`)
A modern, responsive single-page application built with React and Vite, designed to visualize match predictions.
*   **Design System:** Utilizes a premium dark mode, glassmorphism UI aesthetic, featuring custom CSS grids and responsive "cards" for each fixture.
*   **Key Features:**
    *   **League Navigation:** Tabbed interface to switch between All Leagues, Premier League, La Liga, and Bundesliga.
    *   **Matchweek Filtering:** Organizes incoming fixtures chronologically by matchweek instead of a massive unsorted list.
    *   **Visual Enhancements:** 
        *   Renders high-quality local SVG logos for teams and leagues (served statically from `public/logos/` to bypass external network dependencies).
        *   Displays the Top 3 Exact Score predictions and percentages.
    *   **Team Form Tracker:** Dynamically calculates and displays recent form (e.g., W-D-L badges colored green/yellow/red) and overall Points Per Game (PPG) for both teams directly on the prediction card.
    *   **Advanced Prediction Cards:** Dedicated cards for Both Teams To Score (BTTS), Over/Under goal markets, and detailed head-to-head match histories.
    *   **League Stats View:** Dynamic league standings table with deep statistical coverage (BTTS%, CS%, Over%, xG).

---

## Appendix: Core Mathematical Formulas

The prediction engine relies on several core statistical and mathematical formulas to translate raw Expected Goals (xG) and performance metrics into probabilistic forecasts and betting edges.

### 1. Expected Value (EV)
Used in the backtesting module to determine if a bet holds positive value against the bookmaker's odds.
```text
EV = (P(Outcome) * Decimal_Odds) - 1
```
*Where `P(Outcome)` is the model's calculated probability (e.g., 0.55 for Home Win) and `Decimal_Odds` is the bookmaker's payout multiplier (e.g., 2.10).*

### 2. Poisson Distribution for Goal Probabilities
Calculates the probability of a team scoring exactly `x` goals given their expected goals (`λ` or `xG`).
```text
P(x; λ) = (e^-λ * λ^x) / x!
```
*Where `e` is Euler's number (~2.71828), `λ` is the predicted xG for the team, and `x!` is the factorial of the exact number of goals.*

### 3. Dixon-Coles Adjustment Factor (τ)
Corrects the flaw in standard independent Poisson models that underestimate the frequency of low-scoring draws and narrow wins (0-0, 1-0, 0-1, 1-1). The adjustment factor `τ(x, y)` is applied to the joint probability of Home goals (`x`) and Away goals (`y`).
```text
τ(0, 0) = 1 - (λ_home * λ_away * ρ)
τ(0, 1) = 1 + (λ_home * ρ)
τ(1, 0) = 1 + (λ_away * ρ)
τ(1, 1) = 1 - ρ
τ(x, y) = 1   (for all other values of x and y)
```
*Where `λ_home` and `λ_away` are the predicted xG for each team, and `ρ` (rho) is the optimized dependency parameter.*
**Adjusted Joint Probability:** `P_adj(x, y) = P(x; λ_home) * P(y; λ_away) * τ(x, y)`

### 4. Corner Over/Under Probabilities (Poisson CDF)
Used in the corner prediction pipeline to calculate the probability of total corners exceeding a specific betting line (e.g., Over 9.5).
```text
P(Total Corners > k) = 1 - Σ [ (e^-λ * λ^i) / i! ]  for i = 0 to floor(k)
```
*Where `λ` is the sum of Expected Home Corners + Expected Away Corners, and `k` is the betting line (e.g., 9.5).*

### 5. Ranked Probability Score (RPS)
Used to evaluate probabilistic forecasts of ordinal variables (Away -> Draw -> Home), correctly penalizing forecasts less if they are close to the actual outcome.
```text
RPS = (1 / (N - 1)) * Σ [ ( Σ p_i - Σ e_i )^2 ]
```
*Where `p_i` is the forecasted probability for outcome `i`, `e_i` is the actual outcome indicator (1 if outcome `i` happened, 0 otherwise), and the inner sums are cumulative.*

### 6. Odds De-vigging (Proportional)
Used to remove the bookmaker's built-in margin from raw decimal odds to reveal the true "fair" probability implied by the market.
```text
Overround = (1 / Odds_H) + (1 / Odds_D) + (1 / Odds_A)
Fair_Prob_H = (1 / Odds_H) / Overround
```

### 7. Points Per Game (PPG) Form
Used in the feature engineering and frontend team form tracker.
```text
PPG = ( (Wins * 3) + (Draws * 1) ) / Total_Matches_Played
```
