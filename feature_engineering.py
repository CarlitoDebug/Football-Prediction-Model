import pandas as pd
import numpy as np
import os
import json
from scipy.optimize import minimize_scalar

def fit_home_advantage(matches_window, elo_lookup, current_date):
    """Finds the HFA (Elo pts) that minimizes log-loss of match outcomes."""
    if len(matches_window) < 10:
        return 100.0 # Default fallback
        
    def neg_log_likelihood(hfa):
        loss = 0.0
        for m in matches_window:
            r_diff = elo_lookup[m['home']] - elo_lookup[m['away']] + hfa
            p_home = 1 / (1 + 10 ** (-r_diff / 400))
            actual = 1.0 if m['result'] == 'H' else (0.5 if m['result'] == 'D' else 0.0)
            p = min(max(p_home, 1e-9), 1 - 1e-9)
            
            # EWMA weighting: w_i = decay^(days_ago/half_life)
            days_ago = (current_date - m['date']).days
            w = 0.95 ** (days_ago / 30) # half life roughly a month
            
            loss += w * -(actual * np.log(p) + (1 - actual) * np.log(1 - p))
        return loss
    return minimize_scalar(neg_log_likelihood, bounds=(0, 150), method='bounded').x
def compute_decayed_rolling(group: pd.DataFrame, col: str, window: int = 5) -> pd.Series:
    if col not in group.columns or group[col].isnull().all():
        return pd.Series(np.nan, index=group.index)
        
    group = group.sort_values('date')
    return group[col].shift(1).rolling(window=window, min_periods=1).mean()

def engineer_features():
    print("Starting feature engineering (Best Architecture)...")
    
    if not os.path.exists("data/match_stats.csv"):
        print("match_stats.csv not found. Waiting for data ingestion...")
        return
        
    df = pd.read_csv("data/match_stats.csv")
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
        
    team_lineup_strength = None
        
    home_df = df[['date', 'game_id', 'home_team', 'away_team', 'home_goals', 'away_goals', 
                  'home_xg', 'away_xg', 'home_np_xg', 'away_np_xg', 'home_ppda', 'away_ppda', 
                  'home_deep_completions', 'away_deep_completions', 'home_points', 'home_expected_points']].copy()
    home_df.rename(columns={
        'home_team': 'team', 'away_team': 'opponent', 'home_goals': 'goals_for', 'away_goals': 'goals_against', 
        'home_xg': 'xg_for', 'away_xg': 'xg_against', 'home_np_xg': 'np_xg_for', 'away_np_xg': 'np_xg_against',
        'home_ppda': 'ppda_for', 'away_ppda': 'ppda_against', 'home_deep_completions': 'deep_completions_for', 'away_deep_completions': 'deep_completions_against',
        'home_points': 'points', 'home_expected_points': 'xPoints'
    }, inplace=True)
    home_df['is_home'] = 1
    
    if team_lineup_strength is not None:
        home_df = home_df.merge(team_lineup_strength, on=['game_id', 'team'], how='left')
        home_df['starting_xi_strength'] = home_df['starting_xi_strength'].fillna(0)
    
    away_df = df[['date', 'game_id', 'away_team', 'home_team', 'away_goals', 'home_goals', 
                  'away_xg', 'home_xg', 'away_np_xg', 'home_np_xg', 'away_ppda', 'home_ppda', 
                  'away_deep_completions', 'home_deep_completions', 'away_points', 'away_expected_points']].copy()
    away_df.rename(columns={
        'away_team': 'team', 'home_team': 'opponent', 'away_goals': 'goals_for', 'home_goals': 'goals_against', 
        'away_xg': 'xg_for', 'home_xg': 'xg_against', 'away_np_xg': 'np_xg_for', 'home_np_xg': 'np_xg_against',
        'away_ppda': 'ppda_for', 'home_ppda': 'ppda_against', 'away_deep_completions': 'deep_completions_for', 'home_deep_completions': 'deep_completions_against',
        'away_points': 'points', 'away_expected_points': 'xPoints'
    }, inplace=True)
    away_df['is_home'] = 0
    
    if team_lineup_strength is not None:
        away_df = away_df.merge(team_lineup_strength, on=['game_id', 'team'], how='left')
        away_df['starting_xi_strength'] = away_df['starting_xi_strength'].fillna(0)
    
    team_matches = pd.concat([home_df, away_df]).sort_values(['team', 'date']).reset_index(drop=True)
    
    rolling_features = []
    
    for team, group in team_matches.groupby('team'):
        group = group.sort_values('date')
        
        group['rest_days'] = group['date'].diff().dt.days
        group['rest_days'] = group['rest_days'].fillna(7).clip(upper=30)
        
        dates = group['date'].values
        fatigue = []
        for i, current_date in enumerate(dates):
            cutoff = current_date - np.timedelta64(14, 'D')
            count = np.sum((dates[:i] >= cutoff))
            fatigue.append(count)
        group['fatigue_index'] = fatigue
        
        group['rolling_xg_for'] = compute_decayed_rolling(group, 'xg_for', window=5)
        group['rolling_xg_against'] = compute_decayed_rolling(group, 'xg_against', window=5)
        group['rolling_np_xg_for'] = compute_decayed_rolling(group, 'np_xg_for', window=5)
        group['rolling_np_xg_against'] = compute_decayed_rolling(group, 'np_xg_against', window=5)
        group['rolling_ppda_for'] = compute_decayed_rolling(group, 'ppda_for', window=5)
        group['rolling_deep_completions_for'] = compute_decayed_rolling(group, 'deep_completions_for', window=5)
        group['rolling_deep_completions_against'] = compute_decayed_rolling(group, 'deep_completions_against', window=5)
        
        group['rolling_ppg'] = group['points'].shift(1).rolling(window=5, min_periods=1).mean()
        group['rolling_xPoints'] = group['xPoints'].shift(1).rolling(window=5, min_periods=1).mean()
        
        group['goal_diff'] = group['goals_for'] - group['goals_against']
        group['rolling_gd'] = group['goal_diff'].shift(1).rolling(window=5, min_periods=1).mean()
        
        
        rolling_features.append(group)
        
    team_matches_enriched = pd.concat(rolling_features)
    
    # Save the team_matches_enriched for inference script to easily grab latest team stats!
    team_matches_enriched.to_csv("data/team_latest_stats.csv", index=False)
    
    home_features = team_matches_enriched[team_matches_enriched['is_home'] == 1].add_prefix('home_')
    away_features = team_matches_enriched[team_matches_enriched['is_home'] == 0].add_prefix('away_')
    
    home_features_cols = ['home_game_id', 'home_rest_days', 'home_fatigue_index', 'home_rolling_xg_for', 'home_rolling_xg_against', 'home_rolling_np_xg_for', 'home_rolling_np_xg_against', 'home_rolling_ppda_for', 'home_rolling_deep_completions_for', 'home_rolling_deep_completions_against', 'home_rolling_ppg', 'home_rolling_xPoints', 'home_rolling_gd']
    away_features_cols = ['away_game_id', 'away_rest_days', 'away_fatigue_index', 'away_rolling_xg_for', 'away_rolling_xg_against', 'away_rolling_np_xg_for', 'away_rolling_np_xg_against', 'away_rolling_ppda_for', 'away_rolling_deep_completions_for', 'away_rolling_deep_completions_against', 'away_rolling_ppg', 'away_rolling_xPoints', 'away_rolling_gd']
    
    
    merged = pd.merge(df, home_features[home_features_cols], 
                      left_on='game_id', right_on='home_game_id', how='left')
    merged = pd.merge(merged, away_features[away_features_cols], 
                      left_on='game_id', right_on='away_game_id', how='left')
                      
    merged['outcome'] = np.where(merged['home_goals'] > merged['away_goals'], 2, 
                                 np.where(merged['home_goals'] == merged['away_goals'], 1, 0))

    # --- Integrate Missing Players ---
    missing_dfs = []
    if os.path.exists("data/missing_players_hist.csv"):
        missing_dfs.append(pd.read_csv("data/missing_players_hist.csv"))
    if os.path.exists("data/missing_players_upcoming.csv"):
        missing_dfs.append(pd.read_csv("data/missing_players_upcoming.csv"))
        
    if missing_dfs:
        try:
            missing_df = pd.concat(missing_dfs, ignore_index=True)
            missing_df['date'] = pd.to_datetime(missing_df['date'], format='ISO8601', utc=True).dt.tz_localize(None)
            missing_df['date_day'] = missing_df['date'].dt.date
            
            with open('team_mapping.json', 'r') as f:
                t_map = json.load(f)
                
            missing_df['team_mapped'] = missing_df['team'].apply(lambda x: t_map.get(x, x))
            
            # Calculate base severity score: Doubtful = 0.5, Out/Suspended = 1.0
            missing_df['status_weight'] = np.where(missing_df['status'].astype(str).str.lower().str.contains('doubtful'), 0.5, 1.0)
            
            # --- START PLAYER IMPORTANCE (thefuzz) ---
            if os.path.exists("data/player_season_stats.csv"):
                print("Computing player importance via fuzzy matching...")
                try:
                    from thefuzz import process
                except ImportError:
                    print("thefuzz not installed. Falling back to basic 1.0/0.5 weighting.")
                    process = None
                    
                if process is not None:
                    p_stats = pd.read_csv("data/player_season_stats.csv")
                    # First, map team names in p_stats just like we mapped WhoScored
                    if 'team' in p_stats.columns:
                        p_stats['team_mapped'] = p_stats['team'].apply(lambda x: t_map.get(x, x))
                    elif 'home_team' in p_stats.columns: # Sometimes it splits home/away in Understat
                        pass # Handle if necessary
                        
                    # Find team column
                    team_col = 'team' if 'team' in p_stats.columns else ('h_team' if 'h_team' in p_stats.columns else None)
                    
                    if team_col and 'minutes' in p_stats.columns and 'player' in p_stats.columns:
                        p_stats['team_mapped'] = p_stats[team_col].apply(lambda x: t_map.get(x, x))
                        player_mins = p_stats.groupby(['team_mapped', 'player'])['minutes'].sum().reset_index()
                        team_max_mins = player_mins.groupby('team_mapped')['minutes'].max().reset_index()
                        team_max_mins.rename(columns={'minutes': 'max_time'}, inplace=True)
                        player_mins = pd.merge(player_mins, team_max_mins, on='team_mapped')
                        
                        # Importance = player minutes / maximum minutes played by any player in that team
                        player_mins['importance'] = player_mins['minutes'] / player_mins['max_time'].clip(lower=1)
                        
                        # Cache for speed
                        team_rosters_cache = {team: group for team, group in player_mins.groupby('team_mapped')}
                        
                        def match_player_importance(row):
                            team = row['team_mapped']
                            ws_name = str(row['player'])
                            
                            if team not in team_rosters_cache:
                                return row['status_weight'] # fallback
                                
                            team_roster = team_rosters_cache[team]
                            choices = team_roster['player'].tolist()
                            best_match = process.extractOne(ws_name, choices)
                            
                            if best_match and best_match[1] >= 70: # 70% confidence threshold
                                matched_name = best_match[0]
                                importance = team_roster[team_roster['player'] == matched_name]['importance'].iloc[0]
                                # Final score = severity * importance. (We ensure minimum 0.2 so backups still count)
                                return row['status_weight'] * max(importance, 0.2)
                            else:
                                return row['status_weight'] * 0.2 # fallback: assume low importance if unmatchable
                                
                        print("Fuzzy matching WhoScored names to Understat names... this might take a minute.")
                        missing_df['status_weight'] = missing_df.apply(match_player_importance, axis=1)
            # --- END PLAYER IMPORTANCE ---
            
            # Group by team and date to get total missing score
            missing_scores = missing_df.groupby(['team_mapped', 'date_day'])['status_weight'].sum().reset_index()
            missing_scores.rename(columns={'status_weight': 'missing_score'}, inplace=True)
            
            merged['date_day'] = merged['date'].dt.date
            
            # Merge for home team
            merged = pd.merge(merged, missing_scores, left_on=['home_team', 'date_day'], right_on=['team_mapped', 'date_day'], how='left')
            merged.rename(columns={'missing_score': 'home_missing_score'}, inplace=True)
            merged.drop(columns=['team_mapped'], inplace=True)
            
            # Merge for away team
            merged = pd.merge(merged, missing_scores, left_on=['away_team', 'date_day'], right_on=['team_mapped', 'date_day'], how='left')
            merged.rename(columns={'missing_score': 'away_missing_score'}, inplace=True)
            merged.drop(columns=['team_mapped', 'date_day'], inplace=True)
            
            merged['home_missing_score'] = merged['home_missing_score'].fillna(0.0)
            merged['away_missing_score'] = merged['away_missing_score'].fillna(0.0)
        except Exception as e:
            print("Failed to process missing players:", e)
            merged['home_missing_score'] = 0.0
            merged['away_missing_score'] = 0.0
    else:
        merged['home_missing_score'] = 0.0
        merged['away_missing_score'] = 0.0
                                 
    merged = merged.sort_values('date').reset_index(drop=True)
    
    # 1. Calculate Elo Ratings and H2H
    elo_dict = {}
    league_matches = {}
    K = 20
    
    home_elo_list = []
    away_elo_list = []
    elo_diff_list = []
    home_elo_mom_list = []
    away_elo_mom_list = []
    hfa_list = []
    
    home_sos_xg_for_list = []
    home_sos_xg_ag_list = []
    away_sos_xg_for_list = []
    away_sos_xg_ag_list = []
    
    h2h_home_win_list = []
    h2h_draw_list = []
    
    h2h_history = {}
    team_history = {}
    
    for idx, row in merged.iterrows():
        home = row['home_team']
        away = row['away_team']
        league = row.get('league', 'ENG-Premier League')
        current_date = row['date']
        
        # --- ELO ---
        if home not in elo_dict: elo_dict[home] = 1500
        if away not in elo_dict: elo_dict[away] = 1500
        if home not in team_history: team_history[home] = []
        if away not in team_history: team_history[away] = []
        if league not in league_matches: league_matches[league] = []
        
        if 'league_hfa_cache' not in locals():
            league_hfa_cache = {}
        
        home_elo = elo_dict[home]
        away_elo = elo_dict[away]
        
        home_elo_list.append(home_elo)
        away_elo_list.append(away_elo)
        elo_diff_list.append(home_elo - away_elo)
        
        # Momentum
        home_elo_mom_list.append(home_elo - team_history[home][-5]['elo'] if len(team_history[home]) >= 5 else home_elo - 1500)
        away_elo_mom_list.append(away_elo - team_history[away][-5]['elo'] if len(team_history[away]) >= 5 else away_elo - 1500)
        
        # SoS Adjusted Exponential Form
        def get_sos_xg(hist, key):
            if not hist: return np.nan
            recent = hist[-5:]
            w = np.array([0.95**(len(recent)-1-i) for i in range(len(recent))])
            sos = np.array([h['opp_elo']/1500.0 for h in recent])
            vals = np.array([h[key] for h in recent])
            return np.sum(vals * sos * w) / np.sum(w)
            
        home_sos_xg_for_list.append(get_sos_xg(team_history[home], 'xg_for'))
        home_sos_xg_ag_list.append(get_sos_xg(team_history[home], 'xg_ag'))
        away_sos_xg_for_list.append(get_sos_xg(team_history[away], 'xg_for'))
        away_sos_xg_ag_list.append(get_sos_xg(team_history[away], 'xg_ag'))
        
        # Dynamic HFA
        if len(league_matches[league]) % 100 == 0:
            league_hfa_cache[league] = fit_home_advantage(league_matches[league], elo_dict, current_date)
        dynamic_hfa = league_hfa_cache.get(league, 100.0)
        hfa_list.append(dynamic_hfa)
        
        dr = (home_elo + dynamic_hfa) - away_elo
        E_home = 1 / (1 + 10 ** (-dr / 400))
        E_away = 1 - E_home
        
        if row['home_goals'] > row['away_goals']:
            S_home, S_away = 1, 0
            winner = home
            result_char = 'H'
        elif row['home_goals'] == row['away_goals']:
            S_home, S_away = 0.5, 0.5
            winner = 'Draw'
            result_char = 'D'
        else:
            S_home, S_away = 0, 1
            winner = away
            result_char = 'A'
            
        # Margin of Victory multiplier
        goal_diff = abs(row['home_goals'] - row['away_goals'])
        mov_multiplier = np.sqrt(goal_diff) if goal_diff > 0 else 1.0
            
        elo_dict[home] = home_elo + K * mov_multiplier * (S_home - E_home)
        elo_dict[away] = away_elo + K * mov_multiplier * (S_away - E_away)
        
        league_matches[league].append({
            'date': current_date,
            'home': home,
            'away': away,
            'result': result_char
        })
        
        # --- H2H ---
        matchup = tuple(sorted([home, away]))
        if matchup not in h2h_history:
            h2h_history[matchup] = []
            
        history = h2h_history[matchup]
        
        if len(history) < 4:
            h2h_home_win_list.append(0.0)
            h2h_draw_list.append(0.0)
        else:
            recent = history[-10:]
            recent_dates = pd.to_datetime([h['date'] for h in recent])
            days_diff = (row['date'] - recent_dates).days
            weights = np.exp(-0.001 * days_diff)
            
            home_wins = np.array([1 if h['winner'] == home else 0 for h in recent])
            draws = np.array([1 if h['winner'] == 'Draw' else 0 for h in recent])
            
            total_weight = np.sum(weights)
            
            h2h_home_win_list.append(np.sum(home_wins * weights) / total_weight)
            h2h_draw_list.append(np.sum(draws * weights) / total_weight)
            
        h2h_history[matchup].append({'date': row['date'], 'winner': winner})
        
        # Update team history after match
        team_history[home].append({'xg_for': row['home_xg'], 'xg_ag': row['away_xg'], 'opp_elo': away_elo, 'elo': home_elo})
        team_history[away].append({'xg_for': row['away_xg'], 'xg_ag': row['home_xg'], 'opp_elo': home_elo, 'elo': away_elo})

    merged['home_elo'] = home_elo_list
    merged['away_elo'] = away_elo_list
    merged['elo_diff'] = elo_diff_list
    merged['home_elo_momentum'] = home_elo_mom_list
    merged['away_elo_momentum'] = away_elo_mom_list
    merged['league_hfa'] = hfa_list
    
    merged['home_sos_xg_for'] = home_sos_xg_for_list
    merged['home_sos_xg_against'] = home_sos_xg_ag_list
    merged['away_sos_xg_for'] = away_sos_xg_for_list
    merged['away_sos_xg_against'] = away_sos_xg_ag_list
    
    merged['h2h_home_win'] = h2h_home_win_list
    merged['h2h_draw'] = h2h_draw_list
    
    # --- Explicit Attack/Defense Interaction with Shrinkage ---
    # Global league averages
    league_avg_hxg = merged['home_xg'].mean()
    league_avg_axg = merged['away_xg'].mean()
    
    # Assuming window=5, let's use K=8 for shrinkage weight as requested
    N = 5
    K = 8
    
    # Home's expected goals
    shrunk_home_atk = (merged['home_rolling_xg_for'] * N + league_avg_hxg * K) / (N + K)
    shrunk_away_def = (merged['away_rolling_xg_against'] * N + league_avg_hxg * K) / (N + K)
    merged['home_attack_defense_lambda'] = (shrunk_home_atk * shrunk_away_def) / league_avg_hxg
    
    # Away's expected goals
    shrunk_away_atk = (merged['away_rolling_xg_for'] * N + league_avg_axg * K) / (N + K)
    shrunk_home_def = (merged['home_rolling_xg_against'] * N + league_avg_axg * K) / (N + K)
    merged['away_attack_defense_lambda'] = (shrunk_away_atk * shrunk_home_def) / league_avg_axg
                                 
    merged.to_csv("data/features.csv", index=False)
    
    # Save current ELO for inference
    pd.DataFrame(list(elo_dict.items()), columns=['team', 'elo']).to_csv('data/team_latest_elo.csv', index=False)
    
    # Save team_history and h2h_history for inference
    # Convert datetime to string for json serialization in h2h_history
    h2h_serializable = {}
    for k, v in h2h_history.items():
        key_str = f"{k[0]}|{k[1]}"
        h2h_serializable[key_str] = [{'date': str(x['date']), 'winner': x['winner']} for x in v]
        
    with open('data/h2h_history.json', 'w') as f:
        json.dump(h2h_serializable, f)
        
    with open('data/team_history.json', 'w') as f:
        json.dump(team_history, f)
    
    print("Feature engineering complete. Saved to data/features.csv")

if __name__ == "__main__":
    engineer_features()
