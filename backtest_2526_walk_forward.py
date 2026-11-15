import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.linear_model import Ridge, PoissonRegressor
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from scipy.optimize import minimize
from scipy.stats import poisson
import json
import time

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

def optimize_rho(xg_h_arr, xg_a_arr, y_true):
    from sklearn.metrics import log_loss
    def objective(rho):
        preds = []
        for h, a in zip(xg_h_arr, xg_a_arr):
            _, p_h, p_d, p_a = dixon_coles_probabilities(h, a, rho[0])
            preds.append([p_a, p_d, p_h])
        return log_loss(y_true, preds)
    
    res = minimize(objective, x0=[0.0], bounds=[(-0.5, 0.5)])
    return res.x[0]

def rps(predicted_probs, actual_index):
    cum_pred = cum_actual = total = 0.0
    for i in range(len(predicted_probs) - 1):
        cum_pred += predicted_probs[i]
        cum_actual += 1.0 if i == actual_index else 0.0
        total += (cum_pred - cum_actual) ** 2
    return total / (len(predicted_probs) - 1)

def devig(odds_h, odds_d, odds_a):
    inv = [1/odds_h, 1/odds_d, 1/odds_a]
    overround = sum(inv)
    return [p / overround for p in inv]

def get_closing_odds(row):
    if 'PSCH' in row and pd.notna(row['PSCH']):
        return float(row['PSCH']), float(row['PSCD']), float(row['PSCA']), 'pinnacle_close'
    elif 'AvgCH' in row and pd.notna(row['AvgCH']):
        return float(row['AvgCH']), float(row['AvgCD']), float(row['AvgCA']), 'market_avg_close'
    elif 'AvgH' in row and pd.notna(row['AvgH']):
        return float(row['AvgH']), float(row['AvgD']), float(row['AvgA']), 'pre_match_avg_fallback'
    else:
        return None, None, None, 'none'



def run_walk_forward():
    print("Starting Walk-Forward Backtest for 2025-2026 Premier League...", flush=True)
    
    df = pd.read_csv("data/features.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    goal_features = [
        'home_sos_xg_for', 'home_sos_xg_against', 'home_rolling_ppda_for', 
        'home_rolling_ppg', 'home_rolling_xPoints', 'home_rolling_gd', 'home_rest_days', 'home_fatigue_index',
        'home_rolling_np_xg_for', 'home_rolling_np_xg_against', 'home_rolling_deep_completions_for', 'home_rolling_deep_completions_against',
        'away_sos_xg_for', 'away_sos_xg_against', 'away_rolling_ppda_for', 
        'away_rolling_ppg', 'away_rolling_xPoints', 'away_rolling_gd', 'away_rest_days', 'away_fatigue_index',
        'away_rolling_np_xg_for', 'away_rolling_np_xg_against', 'away_rolling_deep_completions_for', 'away_rolling_deep_completions_against',
        'home_elo', 'away_elo', 'elo_diff', 'home_elo_momentum', 'away_elo_momentum',
        'h2h_home_win', 'h2h_draw'
    ]
    df = df.dropna(subset=goal_features)
    
    hist_df = pd.read_csv("data/match_history.csv")
    hist_df['date'] = pd.to_datetime(hist_df['date'], format='mixed', dayfirst=True)
    
    with open('team_mapping.json', 'r') as f:
        team_mapping = json.load(f)
        
    hist_df['home_team'] = hist_df['home_team'].map(lambda x: team_mapping.get(x, x))
    hist_df['away_team'] = hist_df['away_team'].map(lambda x: team_mapping.get(x, x))
    
    hist_df = hist_df.dropna(subset=['HC', 'AC'])
    
    team_matches = []
    for is_home, prefix in [(1, 'home_'), (0, 'away_')]:
        tdf = hist_df[['date', f'{prefix}team', 'HC' if is_home else 'AC', 'AC' if is_home else 'HC', 'HS' if is_home else 'AS', 'AS' if is_home else 'HS', 'HST' if is_home else 'AST', 'AST' if is_home else 'HST']].copy()
        tdf.columns = ['date', 'team', 'corners_for', 'corners_against', 'shots_for', 'shots_against', 'sot_for', 'sot_against']
        tdf['is_home'] = is_home
        team_matches.append(tdf)
    
    team_matches = pd.concat(team_matches).sort_values(['team', 'date'])
    team_matches['rolling_corners_for'] = team_matches.groupby('team')['corners_for'].shift(1).rolling(window=5, min_periods=1).mean()
    team_matches['rolling_corners_against'] = team_matches.groupby('team')['corners_against'].shift(1).rolling(window=5, min_periods=1).mean()
    team_matches['rolling_sot_for'] = team_matches.groupby('team')['sot_for'].shift(1).rolling(window=5, min_periods=1).mean()
    
    home_cf = team_matches[team_matches['is_home'] == 1].add_prefix('home_')
    away_cf = team_matches[team_matches['is_home'] == 0].add_prefix('away_')
    
    hist_df = pd.merge(hist_df, home_cf[['home_date', 'home_team', 'home_rolling_corners_for', 'home_rolling_corners_against', 'home_rolling_sot_for']], left_on=['date', 'home_team'], right_on=['home_date', 'home_team'], how='left')
    hist_df = pd.merge(hist_df, away_cf[['away_date', 'away_team', 'away_rolling_corners_for', 'away_rolling_corners_against', 'away_rolling_sot_for']], left_on=['date', 'away_team'], right_on=['away_date', 'away_team'], how='left')
    
    corner_features = [
        'home_rolling_corners_for', 'home_rolling_corners_against', 'home_rolling_sot_for',
        'away_rolling_corners_for', 'away_rolling_corners_against', 'away_rolling_sot_for'
    ]
    hist_df = hist_df.dropna(subset=corner_features)
    
    df['date'] = df['date'].dt.tz_localize(None).dt.floor('D')
    hist_df['date'] = hist_df['date'].dt.tz_localize(None).dt.floor('D')
    
    merged = pd.merge(df, hist_df, on=['home_team', 'date'], suffixes=('', '_hist'))
    print(f"Total merged valid records: {len(merged)}", flush=True)
    
    target_league = 'ENG-Premier League'
    target_season = 2526
    
    target_matches = merged[(merged['season'] == target_season) & (merged['league'] == target_league)].copy()
    target_matches = target_matches.sort_values('date')
    
    unique_dates = target_matches['date'].unique()
    print(f"Found {len(unique_dates)} unique match dates in season {target_season}. Proceeding to walk-forward evaluation...", flush=True)
    
    results = []
    total_bets = 0
    total_staked = 0
    total_profit = 0
    winning_bets = 0
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    winning_bets = 0
    results = []
    rps_scores = []
    clv_tiers_used = {'pinnacle_close': 0, 'market_avg_close': 0, 'pre_match_avg_fallback': 0, 'none': 0}
    
    start_time = time.time()
    
    for i, current_date in enumerate(unique_dates):
        train_df = merged[merged['date'] < current_date].copy()
        
        X_train_g = train_df[goal_features]
        y_train_h = train_df['home_xg']
        y_train_a = train_df['away_xg']
        y_train_out = train_df['outcome']
        
        X_train_c = train_df[corner_features]
        y_train_hc = train_df['HC']
        y_train_ac = train_df['AC']
        
        lgb_h = LGBMRegressor(objective='poisson', n_estimators=50, random_state=42, n_jobs=-1, verbose=-1)
        xgb_h = XGBRegressor(objective='count:poisson', n_estimators=50, random_state=42, n_jobs=-1, eval_metric='poisson-nloglik')
        cat_h = CatBoostRegressor(loss_function='Poisson', iterations=50, random_seed=42, verbose=False)
        glm_h = PoissonRegressor(alpha=0.1, max_iter=1000)
        
        lgb_a = LGBMRegressor(objective='poisson', n_estimators=50, random_state=42, n_jobs=-1, verbose=-1)
        xgb_a = XGBRegressor(objective='count:poisson', n_estimators=50, random_state=42, n_jobs=-1, eval_metric='poisson-nloglik')
        cat_a = CatBoostRegressor(loss_function='Poisson', iterations=50, random_seed=42, verbose=False)
        glm_a = PoissonRegressor(alpha=0.1, max_iter=1000)
        
        xgb_hc = XGBRegressor(objective='count:poisson', n_estimators=50, random_state=42, n_jobs=-1)
        xgb_ac = XGBRegressor(objective='count:poisson', n_estimators=50, random_state=42, n_jobs=-1)
        
        lgb_oof_h = cross_val_predict(lgb_h, X_train_g, y_train_h, cv=kf)
        xgb_oof_h = cross_val_predict(xgb_h, X_train_g, y_train_h, cv=kf)
        cat_oof_h = cross_val_predict(cat_h, X_train_g, y_train_h, cv=kf)
        glm_oof_h = cross_val_predict(glm_h, X_train_g, y_train_h, cv=kf)
        
        meta_h = Ridge(alpha=1.0)
        meta_h.fit(np.column_stack((lgb_oof_h, xgb_oof_h, cat_oof_h, glm_oof_h)), y_train_h)
        oof_xg_h = meta_h.predict(np.column_stack((lgb_oof_h, xgb_oof_h, cat_oof_h, glm_oof_h)))
        oof_xg_h = np.clip(oof_xg_h, 0.01, 10.0)
        
        lgb_oof_a = cross_val_predict(lgb_a, X_train_g, y_train_a, cv=kf)
        xgb_oof_a = cross_val_predict(xgb_a, X_train_g, y_train_a, cv=kf)
        cat_oof_a = cross_val_predict(cat_a, X_train_g, y_train_a, cv=kf)
        glm_oof_a = cross_val_predict(glm_a, X_train_g, y_train_a, cv=kf)
        
        meta_a = Ridge(alpha=1.0)
        meta_a.fit(np.column_stack((lgb_oof_a, xgb_oof_a, cat_oof_a, glm_oof_a)), y_train_a)
        oof_xg_a = meta_a.predict(np.column_stack((lgb_oof_a, xgb_oof_a, cat_oof_a, glm_oof_a)))
        oof_xg_a = np.clip(oof_xg_a, 0.01, 10.0)
        
        rho = optimize_rho(oof_xg_h, oof_xg_a, y_train_out)
        
        lgb_h.fit(X_train_g, y_train_h)
        xgb_h.fit(X_train_g, y_train_h)
        cat_h.fit(X_train_g, y_train_h)
        glm_h.fit(X_train_g, y_train_h)
        lgb_a.fit(X_train_g, y_train_a)
        xgb_a.fit(X_train_g, y_train_a)
        cat_a.fit(X_train_g, y_train_a)
        glm_a.fit(X_train_g, y_train_a)
        xgb_hc.fit(X_train_c, y_train_hc)
        xgb_ac.fit(X_train_c, y_train_ac)
        
        test_df = target_matches[target_matches['date'] == current_date]
        
        for idx, row in test_df.iterrows():
            X_test_g = pd.DataFrame([row[goal_features].values], columns=goal_features)
            X_test_c = pd.DataFrame([row[corner_features].values], columns=corner_features)
            
            p_lgb_h = lgb_h.predict(X_test_g)
            p_xgb_h = xgb_h.predict(X_test_g)
            p_cat_h = cat_h.predict(X_test_g)
            p_glm_h = glm_h.predict(X_test_g)
            h_xg = np.clip(meta_h.predict(np.column_stack((p_lgb_h, p_xgb_h, p_cat_h, p_glm_h))), 0.01, 10.0)[0]
            
            p_lgb_a = lgb_a.predict(X_test_g)
            p_xgb_a = xgb_a.predict(X_test_g)
            p_cat_a = cat_a.predict(X_test_g)
            p_glm_a = glm_a.predict(X_test_g)
            a_xg = np.clip(meta_a.predict(np.column_stack((p_lgb_a, p_xgb_a, p_cat_a, p_glm_a))), 0.01, 10.0)[0]
            
            prob_matrix, p_h, p_d, p_a = dixon_coles_probabilities(h_xg, a_xg, rho)
            
            pred_outcome = "Home Win" if p_h > p_a and p_h > p_d else "Away Win" if p_a > p_h and p_a > p_d else "Draw"
            act_home_g = int(row['home_goals'])
            act_away_g = int(row['away_goals'])
            act_outcome = "Home Win" if act_home_g > act_away_g else "Away Win" if act_away_g > act_home_g else "Draw"
            
            actual_index = 2 if act_outcome == "Home Win" else 1 if act_outcome == "Draw" else 0
            rps_scores.append(rps([p_a, p_d, p_h], actual_index))
            
            bet_placed = None
            bet_odds = 0
            bet_result = 0
            max_ev = 0
            
            odds_h, odds_d, odds_a, tier = get_closing_odds(row)
            clv_tiers_used[tier] += 1
            
            if odds_h is not None:
                fair_h, fair_d, fair_a = devig(odds_h, odds_d, odds_a)
                
                # Edge is model prob - fair implied prob
                edge_h = p_h - fair_h
                edge_d = p_d - fair_d
                edge_a = p_a - fair_a
                
                max_edge = max(edge_h, edge_d, edge_a)
                
                if max_edge > 0.05: # Require a 5% true edge against fair closing line
                    if max_edge == edge_h:
                        bet_placed = "Home Win"
                        bet_odds = odds_h
                    elif max_edge == edge_d:
                        bet_placed = "Draw"
                        bet_odds = odds_d
                    else:
                        bet_placed = "Away Win"
                        bet_odds = odds_a
                        
                    if bet_placed == act_outcome:
                        bet_result = 100 * (bet_odds - 1)
                    else:
                        bet_result = -100
                        
                    total_bets += 1
                    total_staked += 100
                    total_profit += bet_result
                    if bet_result > 0: winning_bets += 1
            
            results.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Match': f"{row['home_team']} vs {row['away_team']}",
                'Pred': pred_outcome,
                'Act': act_outcome,
                'Bet': bet_placed if bet_placed else "None",
                'P/L': bet_result if bet_placed else 0
            })
            
        print(f"[{i+1}/{len(unique_dates)}] Processed {current_date.strftime('%Y-%m-%d')} ({len(test_df)} matches). Cumulative ROI: {(total_profit/(total_staked if total_staked>0 else 1))*100:.1f}%", flush=True)

    end_time = time.time()
    print(f"Finished in {(end_time - start_time):.1f}s", flush=True)
    
    correct_preds = sum(1 for r in results if r['Pred'] == r['Act'])
    
    with open("C:/Users/mcdre/.gemini/antigravity-ide/brain/ce489575-816c-49c1-98fc-39d383156c8e/full_season_2526_walk_forward.md", "w", encoding='utf-8') as f:
        f.write("# 2025-2026 Premier League: Walk-Forward Zero-Leakage Backtest\n\n")
        f.write(f"- **Total Games:** {len(results)}\n")
        f.write(f"- **Correct Predictions:** {correct_preds} ({(correct_preds/len(results))*100:.1f}%)\n")
        f.write(f"- **Average Ranked Probability Score (RPS):** {np.mean(rps_scores):.4f}\n")
        f.write("\n### Betting Simulation (True Edge > 5% vs De-vigged Closing Line)\n")
        f.write(f"- **Total Bets Placed:** {total_bets}\n")
        if total_bets > 0:
            f.write(f"- **Total Staked:** ${total_staked:.2f}\n")
            f.write(f"- **Total Profit:** ${total_profit:.2f}\n")
            f.write(f"- **ROI:** **{(total_profit/total_staked)*100:.2f}%**\n")
        f.write("\n### Closing Line Value (CLV) Data Quality\n")
        f.write("- Shows which odds were used to determine market price:\n")
        for tier, count in clv_tiers_used.items():
            f.write(f"  - {tier}: {count} matches\n")
        f.write("\nNote: ML models were re-trained before every single matchday strictly using historical data.\n")

if __name__ == "__main__":
    run_walk_forward()
