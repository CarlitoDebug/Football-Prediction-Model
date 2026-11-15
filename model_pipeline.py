import pandas as pd
import numpy as np
import os
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.linear_model import Ridge, PoissonRegressor
from sklearn.metrics import log_loss, accuracy_score, brier_score_loss
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from scipy.optimize import minimize
import pickle

def dixon_coles_probabilities(home_xg, away_xg, rho, max_goals=6):
    """
    Calculate the probability matrix of exact scores using the Dixon-Coles adjusted Poisson distribution.
    Returns:
        prob_matrix: max_goals x max_goals numpy array of probabilities
        home_win_prob: Sum of probabilities where home_goals > away_goals
        draw_prob: Sum of probabilities where home_goals == away_goals
        away_win_prob: Sum of probabilities where home_goals < away_goals
    """
    from scipy.stats import poisson
    
    # Generate standard Poisson matrix
    home_probs = poisson.pmf(np.arange(max_goals), home_xg)
    away_probs = poisson.pmf(np.arange(max_goals), away_xg)
    
    prob_matrix = np.outer(home_probs, away_probs)
    
    # Apply Dixon-Coles adjustment
    tau_00 = 1 - (home_xg * away_xg * rho)
    tau_01 = 1 + (home_xg * rho)
    tau_10 = 1 + (away_xg * rho)
    tau_11 = 1 - rho
    
    # Ensure tau doesn't push probabilities below 0
    tau_00 = max(0, tau_00)
    tau_01 = max(0, tau_01)
    tau_10 = max(0, tau_10)
    tau_11 = max(0, tau_11)
    
    prob_matrix[0, 0] *= tau_00
    prob_matrix[0, 1] *= tau_01
    prob_matrix[1, 0] *= tau_10
    prob_matrix[1, 1] *= tau_11
    
    # Normalize the matrix so it sums to 1 (adjustments can slightly alter the sum)
    prob_matrix = prob_matrix / np.sum(prob_matrix)
    
    # Calculate 3-way probabilities
    # Rows are home goals, columns are away goals
    home_win_prob = np.sum(np.tril(prob_matrix, -1))
    draw_prob = np.sum(np.diag(prob_matrix))
    away_win_prob = np.sum(np.triu(prob_matrix, 1))
    
    return prob_matrix, home_win_prob, draw_prob, away_win_prob

def optimize_rho(xg_h_arr, xg_a_arr, y_true):
    def objective(rho):
        preds = []
        for h, a in zip(xg_h_arr, xg_a_arr):
            _, p_h, p_d, p_a = dixon_coles_probabilities(h, a, rho[0])
            preds.append([p_a, p_d, p_h]) # 0=Away, 1=Draw, 2=Home
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

def train_models():
    print("Starting Hybrid ML + Dixon-Coles Training Pipeline...")
    if not os.path.exists("data/features.csv"):
        print("features.csv not found. Please run feature_engineering.py first.")
        return
        
    df = pd.read_csv("data/features.csv")
    
    features = [
        'home_sos_xg_for', 'home_sos_xg_against', 'home_rolling_ppda_for', 
        'home_rolling_ppg', 'home_rolling_xPoints', 'home_rolling_gd', 'home_rest_days', 'home_fatigue_index',
        'home_rolling_np_xg_for', 'home_rolling_np_xg_against', 'home_rolling_deep_completions_for', 'home_rolling_deep_completions_against',
        'away_sos_xg_for', 'away_sos_xg_against', 'away_rolling_ppda_for', 
        'away_rolling_ppg', 'away_rolling_xPoints', 'away_rolling_gd', 'away_rest_days', 'away_fatigue_index',
        'away_rolling_np_xg_for', 'away_rolling_np_xg_against', 'away_rolling_deep_completions_for', 'away_rolling_deep_completions_against',
        'home_elo', 'away_elo', 'elo_diff', 'home_elo_momentum', 'away_elo_momentum',
        'h2h_home_win', 'h2h_draw',
        'home_attack_defense_lambda', 'away_attack_defense_lambda',
        'home_missing_score', 'away_missing_score'
    ]
    
    df = df.dropna(subset=features)
    
    train_df = df[df['season'] != 2627]
    
    X = train_df[features]
    y_home = train_df['home_xg']
    y_away = train_df['away_xg']
    y_outcome = train_df['outcome'] # 2=Home, 1=Draw, 0=Away
    
    print(f"Training on {len(X)} samples with {len(features)} features.")
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # Train Home Goals Regressors
    lgb_home = LGBMRegressor(objective='poisson', n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
    xgb_home = XGBRegressor(objective='count:poisson', n_estimators=100, random_state=42, n_jobs=-1, eval_metric='poisson-nloglik')
    cat_home = CatBoostRegressor(loss_function='Poisson', iterations=100, random_seed=42, verbose=False)
    glm_home = PoissonRegressor(alpha=0.1, max_iter=1000)
    
    lgb_oof_home = cross_val_predict(lgb_home, X, y_home, cv=kf)
    xgb_oof_home = cross_val_predict(xgb_home, X, y_home, cv=kf)
    cat_oof_home = cross_val_predict(cat_home, X, y_home, cv=kf)
    glm_oof_home = cross_val_predict(glm_home, X, y_home, cv=kf)
    
    meta_home = Ridge(alpha=1.0)
    meta_home.fit(np.column_stack((lgb_oof_home, xgb_oof_home, cat_oof_home, glm_oof_home)), y_home)
    oof_xg_home = meta_home.predict(np.column_stack((lgb_oof_home, xgb_oof_home, cat_oof_home, glm_oof_home)))
    oof_xg_home = np.clip(oof_xg_home, 0.01, 10.0) # Prevent negative or insane xG
    
    # Train Away Goals Regressors
    lgb_away = LGBMRegressor(objective='poisson', n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
    xgb_away = XGBRegressor(objective='count:poisson', n_estimators=100, random_state=42, n_jobs=-1, eval_metric='poisson-nloglik')
    cat_away = CatBoostRegressor(loss_function='Poisson', iterations=100, random_seed=42, verbose=False)
    glm_away = PoissonRegressor(alpha=0.1, max_iter=1000)
    
    lgb_oof_away = cross_val_predict(lgb_away, X, y_away, cv=kf)
    xgb_oof_away = cross_val_predict(xgb_away, X, y_away, cv=kf)
    cat_oof_away = cross_val_predict(cat_away, X, y_away, cv=kf)
    glm_oof_away = cross_val_predict(glm_away, X, y_away, cv=kf)
    
    meta_away = Ridge(alpha=1.0)
    meta_away.fit(np.column_stack((lgb_oof_away, xgb_oof_away, cat_oof_away, glm_oof_away)), y_away)
    oof_xg_away = meta_away.predict(np.column_stack((lgb_oof_away, xgb_oof_away, cat_oof_away, glm_oof_away)))
    oof_xg_away = np.clip(oof_xg_away, 0.01, 10.0)
    
    print("Optimizing Dixon-Coles Rho parameter...")
    optimal_rho = optimize_rho(oof_xg_home, oof_xg_away, y_outcome)
    print(f"Optimal Rho: {optimal_rho:.4f}")
    
    # Evaluate 3-Way Accuracy and Log-Loss using OOF predictions
    final_preds = []
    final_classes = []
    rps_scores = []
    for (h, a), actual_outcome in zip(zip(oof_xg_home, oof_xg_away), y_outcome):
        _, p_h, p_d, p_a = dixon_coles_probabilities(h, a, optimal_rho)
        # 0=Away, 1=Draw, 2=Home
        final_preds.append([p_a, p_d, p_h])
        final_classes.append(np.argmax([p_a, p_d, p_h]))
        rps_scores.append(rps([p_a, p_d, p_h], actual_outcome))
        
    ll = log_loss(y_outcome, final_preds)
    acc = accuracy_score(y_outcome, final_classes)
    mean_rps = np.mean(rps_scores)
    
    y_outcome_bin_a = (y_outcome == 0).astype(int)
    y_outcome_bin_d = (y_outcome == 1).astype(int)
    y_outcome_bin_h = (y_outcome == 2).astype(int)
    
    final_preds_arr = np.array(final_preds)
    bs_a = brier_score_loss(y_outcome_bin_a, final_preds_arr[:, 0])
    bs_d = brier_score_loss(y_outcome_bin_d, final_preds_arr[:, 1])
    bs_h = brier_score_loss(y_outcome_bin_h, final_preds_arr[:, 2])
    
    print(f"=====================================")
    print(f"Hybrid ML + Dixon-Coles Log-Loss: {ll:.4f}")
    print(f"Hybrid ML + Dixon-Coles Accuracy: {acc:.4f}")
    print(f"Hybrid ML + Dixon-Coles RPS:      {mean_rps:.4f}")
    print(f"-------------------------------------")
    print(f"Calibration (Brier Score, lower is better):")
    print(f"  Home Win Brier: {bs_h:.4f}")
    print(f"  Draw Brier:     {bs_d:.4f}")
    print(f"  Away Win Brier: {bs_a:.4f}")
    print(f"=====================================")
    
    print("Training base models on full data for production...")
    lgb_home.fit(X, y_home)
    xgb_home.fit(X, y_home)
    cat_home.fit(X, y_home)
    glm_home.fit(X, y_home)
    lgb_away.fit(X, y_away)
    xgb_away.fit(X, y_away)
    cat_away.fit(X, y_away)
    glm_away.fit(X, y_away)
    
    os.makedirs("models", exist_ok=True)
    with open("models/lgb_home.pkl", "wb") as f: pickle.dump(lgb_home, f)
    with open("models/xgb_home.pkl", "wb") as f: pickle.dump(xgb_home, f)
    with open("models/cat_home.pkl", "wb") as f: pickle.dump(cat_home, f)
    with open("models/glm_home.pkl", "wb") as f: pickle.dump(glm_home, f)
    with open("models/meta_home.pkl", "wb") as f: pickle.dump(meta_home, f)
        
    with open("models/lgb_away.pkl", "wb") as f: pickle.dump(lgb_away, f)
    with open("models/xgb_away.pkl", "wb") as f: pickle.dump(xgb_away, f)
    with open("models/cat_away.pkl", "wb") as f: pickle.dump(cat_away, f)
    with open("models/glm_away.pkl", "wb") as f: pickle.dump(glm_away, f)
    with open("models/meta_away.pkl", "wb") as f: pickle.dump(meta_away, f)
    
    with open("models/optimal_rho.pkl", "wb") as f: pickle.dump(optimal_rho, f)
        
    print("Models saved to models/ directory.")

if __name__ == "__main__":
    train_models()
