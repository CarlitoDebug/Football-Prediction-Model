import pandas as pd
import numpy as np
import pickle
from scipy.stats import poisson

def dixon_coles_probabilities(home_xg, away_xg, rho, max_goals=6):
    home_probs = poisson.pmf(np.arange(max_goals), home_xg)
    away_probs = poisson.pmf(np.arange(max_goals), away_xg)
    
    prob_matrix = np.outer(home_probs, away_probs)
    
    tau_00 = max(0, 1 - (home_xg * away_xg * rho))
    tau_01 = max(0, 1 + (home_xg * rho))
    tau_10 = max(0, 1 + (away_xg * rho))
    tau_11 = max(0, 1 - rho)
    
    prob_matrix[0, 0] *= tau_00
    prob_matrix[0, 1] *= tau_01
    prob_matrix[1, 0] *= tau_10
    prob_matrix[1, 1] *= tau_11
    
    prob_matrix = prob_matrix / np.sum(prob_matrix)
    
    home_win_prob = np.sum(np.tril(prob_matrix, -1))
    draw_prob = np.sum(np.diag(prob_matrix))
    away_win_prob = np.sum(np.triu(prob_matrix, 1))
    
    return prob_matrix, home_win_prob, draw_prob, away_win_prob

def run_backtest():
    print("Loading data and models...")
    
    # Load Models
    with open("models/lgb_home.pkl", "rb") as f: lgb_home = pickle.load(f)
    with open("models/xgb_home.pkl", "rb") as f: xgb_home = pickle.load(f)
    with open("models/meta_home.pkl", "rb") as f: meta_home = pickle.load(f)
        
    with open("models/cat_home.pkl", "rb") as f: cat_home = pickle.load(f)
    with open("models/lgb_away.pkl", "rb") as f: lgb_away = pickle.load(f)
    with open("models/xgb_away.pkl", "rb") as f: xgb_away = pickle.load(f)
    with open("models/cat_away.pkl", "rb") as f: cat_away = pickle.load(f)
    with open("models/meta_away.pkl", "rb") as f: meta_away = pickle.load(f)
    with open("models/optimal_rho.pkl", "rb") as f: optimal_rho = pickle.load(f)
        
    with open("models/xgb_home_corners.pkl", "rb") as f: xgb_home_corners = pickle.load(f)
    with open("models/xgb_away_corners.pkl", "rb") as f: xgb_away_corners = pickle.load(f)

    # 1. Load Features (Goals)
    features_df = pd.read_csv("data/features.csv")
    
    # 2. Reconstruct Corner Features for 2627
    hist_df = pd.read_csv("data/match_history.csv")
    hist_df['date'] = pd.to_datetime(hist_df['date'], format='mixed', dayfirst=True)
    hist_df = hist_df.dropna(subset=['HC', 'AC'])
    
    home_df = hist_df[['date', 'home_team', 'away_team', 'HC', 'AC', 'HS', 'AS', 'HST', 'AST']].copy()
    home_df.rename(columns={'home_team': 'team', 'away_team': 'opponent', 'HC': 'corners_for', 'AC': 'corners_against', 'HS': 'shots_for', 'AS': 'shots_against', 'HST': 'sot_for', 'AST': 'sot_against'}, inplace=True)
    home_df['is_home'] = 1
    
    away_df = hist_df[['date', 'away_team', 'home_team', 'AC', 'HC', 'AS', 'HS', 'AST', 'HST']].copy()
    away_df.rename(columns={'away_team': 'team', 'home_team': 'opponent', 'AC': 'corners_for', 'HC': 'corners_against', 'AS': 'shots_for', 'HS': 'shots_against', 'AST': 'sot_for', 'HST': 'sot_against'}, inplace=True)
    away_df['is_home'] = 0
    
    team_matches = pd.concat([home_df, away_df]).sort_values(['team', 'date']).reset_index(drop=True)
    
    rolling_features = []
    for team, group in team_matches.groupby('team'):
        group = group.sort_values('date')
        group['rolling_corners_for'] = group['corners_for'].shift(1).rolling(window=5, min_periods=1).mean()
        group['rolling_corners_against'] = group['corners_against'].shift(1).rolling(window=5, min_periods=1).mean()
        group['rolling_sot_for'] = group['sot_for'].shift(1).rolling(window=5, min_periods=1).mean()
        rolling_features.append(group)
        
    team_matches_enriched = pd.concat(rolling_features)
    home_cf = team_matches_enriched[team_matches_enriched['is_home'] == 1].add_prefix('home_')
    away_cf = team_matches_enriched[team_matches_enriched['is_home'] == 0].add_prefix('away_')
    
    hist_df = pd.merge(hist_df, home_cf[['home_date', 'home_team', 'home_rolling_corners_for', 'home_rolling_corners_against', 'home_rolling_sot_for']], left_on=['date', 'home_team'], right_on=['home_date', 'home_team'], how='left')
    hist_df = pd.merge(hist_df, away_cf[['away_date', 'away_team', 'away_rolling_corners_for', 'away_rolling_corners_against', 'away_rolling_sot_for']], left_on=['date', 'away_team'], right_on=['away_date', 'away_team'], how='left')
    
    # 3. Merge Goal Features with Corner Features
    # The team names might differ slightly between understat and match_history.
    # To be safe, we merge by sorting date and team, or just string matching.
    # Let's clean the team names to ensure merge works.
    def clean_name(name):
        name = name.lower()
        if "nott'm" in name:
            name = name.replace("nott'm", "nottingham")
        if name.startswith("man "):
            name = name.replace("man ", "manchester ")
        return name.replace(' ', '').replace('united', '').replace('city', '')
        
    features_df['merge_key'] = features_df['home_team'].apply(clean_name)
    hist_df['merge_key'] = hist_df['home_team'].apply(clean_name)
    
    leagues = ['ENG-Premier League', 'ESP-La Liga']
    
    for league in leagues:
        print(f"Generating backtest report for {league}...")
        bt_features = features_df[(features_df['season'] == 2627) & (features_df['league'] == league)].copy()
        hist_df_2627 = hist_df[(hist_df['season'] == 2627) & (hist_df['league'] == league)]
        
        merged = pd.merge(bt_features, hist_df_2627, on='merge_key', suffixes=('', '_hist'))
        
        # Features to evaluate goals
        goal_features_cols = [
            'home_sos_xg_for', 'home_sos_xg_against', 'home_rolling_ppda_for', 
            'home_rolling_ppg', 'home_rolling_xPoints', 'home_rolling_gd', 'home_rest_days', 'home_fatigue_index',
            'home_rolling_np_xg_for', 'home_rolling_np_xg_against', 'home_rolling_deep_completions_for', 'home_rolling_deep_completions_against',
            'home_lineup_delta',
            'away_sos_xg_for', 'away_sos_xg_against', 'away_rolling_ppda_for', 
            'away_rolling_ppg', 'away_rolling_xPoints', 'away_rolling_gd', 'away_rest_days', 'away_fatigue_index',
            'away_rolling_np_xg_for', 'away_rolling_np_xg_against', 'away_rolling_deep_completions_for', 'away_rolling_deep_completions_against',
            'away_lineup_delta',
            'home_elo', 'away_elo', 'elo_diff', 'home_elo_momentum', 'away_elo_momentum',
            'h2h_home_win', 'h2h_draw'
        ]
        
        # Features to evaluate corners
        corner_features_cols = [
            'home_rolling_corners_for', 'home_rolling_corners_against', 'home_rolling_sot_for',
            'away_rolling_corners_for', 'away_rolling_corners_against', 'away_rolling_sot_for'
        ]
        
        results = []
        
        # Betting tracking
        total_bets = 0
        total_staked = 0
        total_profit = 0
        winning_bets = 0
        
        for idx, row in merged.iterrows():
            X_goal = pd.DataFrame([row[goal_features_cols].values], columns=goal_features_cols)
            X_corner = pd.DataFrame([row[corner_features_cols].values], columns=corner_features_cols)
            
            # 3. Predict Goals (xG) using Meta-Learner
            lgb_pred_h = lgb_home.predict(X_goal)
            xgb_pred_h = xgb_home.predict(X_goal)
            cat_pred_h = cat_home.predict(X_goal)
            meta_X_h = np.column_stack((lgb_pred_h, xgb_pred_h, cat_pred_h))
            home_xg = np.clip(meta_home.predict(meta_X_h), 0.01, 10.0)[0]
            
            lgb_pred_a = lgb_away.predict(X_goal)
            xgb_pred_a = xgb_away.predict(X_goal)
            cat_pred_a = cat_away.predict(X_goal)
            meta_X_a = np.column_stack((lgb_pred_a, xgb_pred_a, cat_pred_a))
            away_xg = np.clip(meta_away.predict(meta_X_a), 0.01, 10.0)[0]
            
            prob_matrix, p_h, p_d, p_a = dixon_coles_probabilities(home_xg, away_xg, optimal_rho)
            pred_outcome = "Home Win" if p_h > p_a and p_h > p_d else "Away Win" if p_a > p_h and p_a > p_d else "Draw"
            
            pred_h_goals, pred_a_goals = np.unravel_index(np.argmax(prob_matrix), prob_matrix.shape)
            pred_score = f"{pred_h_goals} - {pred_a_goals}"
            
            # Actual Goals
            act_home_g = int(row['home_goals'])
            act_away_g = int(row['away_goals'])
            act_outcome = "Home Win" if act_home_g > act_away_g else "Away Win" if act_away_g > act_home_g else "Draw"
            
            # Predict Corners
            exp_hc = xgb_home_corners.predict(X_corner)[0]
            exp_ac = xgb_away_corners.predict(X_corner)[0]
            exp_total_c = exp_hc + exp_ac
            
            act_hc = int(row['HC'])
            act_ac = int(row['AC'])
            act_total_c = act_hc + act_ac
            
            # 4. Betting Simulator (+EV Engine)
            bet_placed = None
            bet_odds = 0
            bet_result = 0
            max_ev = 0
            
            # Check if odds exist
            if 'AvgH' in row and not pd.isna(row['AvgH']):
                avg_h = float(row['AvgH'])
                avg_d = float(row['AvgD'])
                avg_a = float(row['AvgA'])
                
                ev_h = (p_h * avg_h) - 1
                ev_d = (p_d * avg_d) - 1
                ev_a = (p_a * avg_a) - 1
                
                max_ev = max(ev_h, ev_d, ev_a)
                if max_ev > 0.05:  # 5% threshold
                    if max_ev == ev_h:
                        bet_placed = "Home Win"
                        bet_odds = avg_h
                    elif max_ev == ev_d:
                        bet_placed = "Draw"
                        bet_odds = avg_d
                    else:
                        bet_placed = "Away Win"
                        bet_odds = avg_a
                        
                    if bet_placed == act_outcome:
                        bet_result = 100 * (bet_odds - 1)
                    else:
                        bet_result = -100
                        
                    total_bets += 1
                    total_staked += 100
                    total_profit += bet_result
                    if bet_result > 0:
                        winning_bets += 1
                        
            results.append({
                'Match': f"{row['home_team']} vs {row['away_team']}",
                'Pred Prob': f"{p_h*100:.1f}% / {p_d*100:.1f}% / {p_a*100:.1f}%",
                'Pred Outcome': pred_outcome,
                'Pred Score': pred_score,
                'Act Score': f"{act_home_g} - {act_away_g}",
                'Act Outcome': act_outcome,
                'Exp Total Corners': f"{exp_total_c:.1f}",
                'Act Total Corners': f"{act_total_c}",
                'Bet Placed': f"{bet_placed} (@ {bet_odds:.2f})" if bet_placed else "None",
                'Bet EV': f"{max_ev*100:.1f}%" if bet_placed else "-",
                'Bet P/L': f"${bet_result:.2f}" if bet_placed else "-"
            })

        # Generate Markdown Report
        file_name = "laliga_matchweek_1_backtest.md" if league == 'ESP-La Liga' else "matchweek_1_backtest.md"
        title = "🇪🇸 La Liga" if league == 'ESP-La Liga' else "⚽ Premier League"
        
        with open(f"C:/Users/mcdre/.gemini/antigravity-ide/brain/ce489575-816c-49c1-98fc-39d383156c8e/{file_name}", "w", encoding="utf-8") as f:
            f.write(f"# {title} Matchweek 1 (2026-2027) Backtest Report\n\n")
            f.write("This report validates the Zero-Leakage predictions of our model against the actual Matchweek 1 results.\n\n")
            f.write("| Match | Predicted Win/Draw/Loss | Predicted Score | Actual Score | Actual Outcome | Expected Corners | Actual Corners | Bet Placed | EV | P/L |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|\n")
            for r in results:
                match_outcome_emoji = "✅" if r['Pred Outcome'] == r['Act Outcome'] else "❌"
                f.write(f"| {r['Match']} | {r['Pred Prob']} | **{r['Pred Score']}** | {r['Act Score']} | {r['Act Outcome']} {match_outcome_emoji} | {r['Exp Total Corners']} | {r['Act Total Corners']} | {r['Bet Placed']} | {r['Bet EV']} | {r['Bet P/L']} |\n")
                
            f.write("\n## 💰 Betting Performance Summary (+EV Engine)\n\n")
            f.write(f"- **Total Matches Evaluated:** {len(results)}\n")
            f.write(f"- **Total +EV Bets Placed:** {total_bets}\n")
            
            if total_bets > 0:
                win_rate = (winning_bets / total_bets) * 100
                roi = (total_profit / total_staked) * 100
                f.write(f"- **Win Rate on +EV Bets:** {win_rate:.1f}%\n")
                f.write(f"- **Total Staked:** ${total_staked:.2f}\n")
                f.write(f"- **Total Profit/Loss:** ${total_profit:.2f}\n")
                f.write(f"- **Total ROI:** **{roi:.2f}%**\n")
            else:
                f.write("No bets placed (no matches met the >5% EV threshold).\n")

    print("Backtest complete. Reports generated.")

if __name__ == "__main__":
    run_backtest()
