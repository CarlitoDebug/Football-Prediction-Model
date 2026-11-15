import pandas as pd
import numpy as np
import os
from xgboost import XGBRegressor
import pickle
import json

def compute_decayed_rolling(group: pd.DataFrame, col: str, window: int = 5) -> pd.Series:
    if col not in group.columns or group[col].isnull().all():
        return pd.Series(np.nan, index=group.index)
        
    group = group.sort_values('date')
    return group[col].shift(1).rolling(window=window, min_periods=1).mean()

def build_corner_pipeline():
    print("Starting Corner Prediction Pipeline...")
    
    if not os.path.exists("data/match_history.csv"):
        print("match_history.csv not found!")
        return
        
    df = pd.read_csv("data/match_history.csv")
    df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True)
    
    with open('team_mapping.json', 'r') as f:
        team_mapping = json.load(f)
        
    df['home_team'] = df['home_team'].map(lambda x: team_mapping.get(x, x))
    df['away_team'] = df['away_team'].map(lambda x: team_mapping.get(x, x))
    
    # Fill any NaNs in corners with 0 temporarily or drop them
    df = df.dropna(subset=['HC', 'AC'])
    
    # 1. Melt to team-match level
    home_df = df[['date', 'home_team', 'away_team', 'HC', 'AC', 'HS', 'AS', 'HST', 'AST']].copy()
    home_df.rename(columns={
        'home_team': 'team', 'away_team': 'opponent', 
        'HC': 'corners_for', 'AC': 'corners_against',
        'HS': 'shots_for', 'AS': 'shots_against',
        'HST': 'sot_for', 'AST': 'sot_against'
    }, inplace=True)
    home_df['is_home'] = 1
    
    away_df = df[['date', 'away_team', 'home_team', 'AC', 'HC', 'AS', 'HS', 'AST', 'HST']].copy()
    away_df.rename(columns={
        'away_team': 'team', 'home_team': 'opponent', 
        'AC': 'corners_for', 'HC': 'corners_against',
        'AS': 'shots_for', 'HS': 'shots_against',
        'AST': 'sot_for', 'HST': 'sot_against'
    }, inplace=True)
    away_df['is_home'] = 0
    
    team_matches = pd.concat([home_df, away_df]).sort_values(['team', 'date']).reset_index(drop=True)
    
    # 2. Compute rolling features
    rolling_features = []
    
    for team, group in team_matches.groupby('team'):
        group = group.sort_values('date')
        
        group['rolling_corners_for'] = compute_decayed_rolling(group, 'corners_for', window=5)
        group['rolling_corners_against'] = compute_decayed_rolling(group, 'corners_against', window=5)
        group['rolling_sot_for'] = compute_decayed_rolling(group, 'sot_for', window=5)
        
        rolling_features.append(group)
        
    team_matches_enriched = pd.concat(rolling_features)
    
    # Save the latest stats for inference
    team_matches_enriched.to_csv("data/team_latest_corner_stats.csv", index=False)
    
    # 3. Reconstruct match dataset
    home_features = team_matches_enriched[team_matches_enriched['is_home'] == 1].add_prefix('home_')
    away_features = team_matches_enriched[team_matches_enriched['is_home'] == 0].add_prefix('away_')
    
    # We must merge back on index or date+team
    df = pd.merge(df, home_features[['home_date', 'home_team', 'home_rolling_corners_for', 'home_rolling_corners_against', 'home_rolling_sot_for']], 
                  left_on=['date', 'home_team'], right_on=['home_date', 'home_team'], how='left')
    df = pd.merge(df, away_features[['away_date', 'away_team', 'away_rolling_corners_for', 'away_rolling_corners_against', 'away_rolling_sot_for']], 
                  left_on=['date', 'away_team'], right_on=['away_date', 'away_team'], how='left')
                  
    features = [
        'home_rolling_corners_for', 'home_rolling_corners_against', 'home_rolling_sot_for',
        'away_rolling_corners_for', 'away_rolling_corners_against', 'away_rolling_sot_for'
    ]
    
    df = df.dropna(subset=features)
    
    train_df = df[df['season'] != 2627]
    
    X = train_df[features]
    y_home = train_df['HC']
    y_away = train_df['AC']
    
    print(f"Training Corner Models on {len(X)} samples...")
    
    # Check overdispersion
    var_mean_ratio = np.var(y_home) / np.mean(y_home)
    print(f"Home Corner Variance/Mean Ratio: {var_mean_ratio:.3f}")
    
    if var_mean_ratio > 1.05:
        print("Corners exhibit overdispersion. Tuning reg:tweedie...")
        from sklearn.model_selection import KFold
        from sklearn.metrics import mean_squared_error
        
        best_power = 1.2
        best_loss = float('inf')
        
        kf = KFold(n_splits=3, shuffle=True, random_state=42)
        for power in [1.1, 1.3, 1.5, 1.7, 1.9]:
            fold_losses = []
            for train_idx, val_idx in kf.split(X):
                X_tr, y_tr = X.iloc[train_idx], y_home.iloc[train_idx]
                X_va, y_va = X.iloc[val_idx], y_home.iloc[val_idx]
                
                model = XGBRegressor(objective='reg:tweedie', tweedie_variance_power=power, n_estimators=50, random_state=42)
                model.fit(X_tr, y_tr)
                preds = model.predict(X_va)
                # Approximation of log-loss for tweedie
                # We can just use MSE or Poisson deviance as a proxy for tuning
                loss = mean_squared_error(y_va, preds)
                fold_losses.append(loss)
                
            avg_loss = np.mean(fold_losses)
            if avg_loss < best_loss:
                best_loss = avg_loss
                best_power = power
                
        print(f"Best Tweedie Variance Power selected: {best_power}")
        xgb_home_corners = XGBRegressor(objective='reg:tweedie', tweedie_variance_power=best_power, n_estimators=100, random_state=42)
        xgb_away_corners = XGBRegressor(objective='reg:tweedie', tweedie_variance_power=best_power, n_estimators=100, random_state=42)
        
        xgb_home_corners.fit(X, y_home)
        xgb_away_corners.fit(X, y_away)
    else:
        print("No significant overdispersion detected. Using count:poisson.")
        xgb_home_corners = XGBRegressor(objective='count:poisson', n_estimators=100, random_state=42, eval_metric='poisson-nloglik')
        xgb_home_corners.fit(X, y_home)
        
        xgb_away_corners = XGBRegressor(objective='count:poisson', n_estimators=100, random_state=42, eval_metric='poisson-nloglik')
        xgb_away_corners.fit(X, y_away)
    
    os.makedirs("models", exist_ok=True)
    with open("models/xgb_home_corners.pkl", "wb") as f: pickle.dump(xgb_home_corners, f)
    with open("models/xgb_away_corners.pkl", "wb") as f: pickle.dump(xgb_away_corners, f)
    
    print("Corner models trained and saved successfully.")

if __name__ == "__main__":
    build_corner_pipeline()
