import pandas as pd
import numpy as np
import pickle
import sys
import os
import json
from datetime import datetime

def get_team_form(team_name, df, num_matches=10):
    # Overall
    overall_df = df[((df['home_team'] == team_name) | (df['away_team'] == team_name)) & (df['is_result'] == True)].sort_values('date', ascending=False).head(num_matches)
    # Home
    home_df = df[(df['home_team'] == team_name) & (df['is_result'] == True)].sort_values('date', ascending=False).head(num_matches)
    # Away
    away_df = df[(df['away_team'] == team_name) & (df['is_result'] == True)].sort_values('date', ascending=False).head(num_matches)

    def calc_form(matches_df):
        form = []
        matches = []
        pts = 0
        wins, draws, losses = 0, 0, 0
        total_goals, scored, conceded = 0, 0, 0
        btts_count, cs_count, fts_count = 0, 0, 0
        xg_for, xg_against = 0.0, 0.0

        for _, row in matches_df.iterrows():
            is_home = row['home_team'] == team_name
            opponent = row['away_team'] if is_home else row['home_team']
            home_goals = int(row['home_goals'])
            away_goals = int(row['away_goals'])
            
            t_goals = home_goals if is_home else away_goals
            o_goals = away_goals if is_home else home_goals
            raw_t_xg = row.get('home_xg', 0) if is_home else row.get('away_xg', 0)
            raw_o_xg = row.get('away_xg', 0) if is_home else row.get('home_xg', 0)
            t_xg = float(raw_t_xg) if pd.notnull(raw_t_xg) else 0.0
            o_xg = float(raw_o_xg) if pd.notnull(raw_o_xg) else 0.0

            scored += t_goals
            conceded += o_goals
            total_goals += (t_goals + o_goals)
            xg_for += t_xg
            xg_against += o_xg

            if t_goals > 0 and o_goals > 0:
                btts_count += 1
            if o_goals == 0:
                cs_count += 1
            if t_goals == 0:
                fts_count += 1
            
            # Determine result for the selected team
            result = ''
            if t_goals > o_goals:
                result = 'W'
                pts += 3
                wins += 1
            elif t_goals == o_goals:
                result = 'D'
                pts += 1
                draws += 1
            else:
                result = 'L'
                losses += 1
            
            form.append(result)
            
            # Determine year from date string (e.g. "2024-05-12")
            date_str = str(row['date'])
            year = date_str.split('-')[0] if '-' in date_str else date_str
            
            matches.append({
                "date": date_str,
                "year": year,
                "opponent": opponent,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "result": result,
                "is_home": is_home,
                "home_team": row['home_team'],
                "away_team": row['away_team']
            })

        n = len(matches_df)
        
        # Reverse form array to show oldest to newest (left to right) for the UI form badges
        form.reverse()
        ppg = pts / n if n > 0 else 0
        
        stats = {
            "win_pct": round((wins / n) * 100) if n > 0 else 0,
            "avg_goals": round(total_goals / n, 2) if n > 0 else 0,
            "scored": round(scored / n, 2) if n > 0 else 0,
            "conceded": round(conceded / n, 2) if n > 0 else 0,
            "btts_pct": round((btts_count / n) * 100) if n > 0 else 0,
            "cs_pct": round((cs_count / n) * 100) if n > 0 else 0,
            "fts_pct": round((fts_count / n) * 100) if n > 0 else 0,
            "xg": round(xg_for / n, 2) if n > 0 else 0,
            "xga": round(xg_against / n, 2) if n > 0 else 0
        }

        return {"form": form, "ppg": round(ppg, 2), "matches": matches, "stats": stats}

    return {
        "overall": calc_form(overall_df),
        "home": calc_form(home_df),
        "away": calc_form(away_df)
    }

def get_team_hit_rates(team_name, df, num_matches=20):
    matches_df = df[((df['home_team'] == team_name) | (df['away_team'] == team_name)) & (df['is_result'] == True)].sort_values('date', ascending=False).head(num_matches)
    n = len(matches_df)
    if n == 0:
        return {
            'over_0_5': 0, 'over_1_5': 0, 'over_2_5': 0, 'over_3_5': 0, 'over_4_5': 0,
            'btts': 0, 'btts_and_win': 0, 'btts_and_draw': 0, 'btts_and_o25': 0, 'btts_no_and_o25': 0
        }

    team_matches = []
    for _, row in matches_df.iterrows():
        is_home = row['home_team'] == team_name
        if is_home:
            team_matches.append((int(row['home_goals']), int(row['away_goals'])))
        else:
            team_matches.append((int(row['away_goals']), int(row['home_goals'])))
            
    totals = [gf + ga for gf, ga in team_matches]
    
    return {
        'over_0_5': sum(t > 0.5 for t in totals) / n,
        'over_1_5': sum(t > 1.5 for t in totals) / n,
        'over_2_5': sum(t > 2.5 for t in totals) / n,
        'over_3_5': sum(t > 3.5 for t in totals) / n,
        'over_4_5': sum(t > 4.5 for t in totals) / n,
        'btts': sum((gf > 0 and ga > 0) for gf, ga in team_matches) / n,
        'btts_and_win': sum((gf > 0 and ga > 0) and gf > ga for gf, ga in team_matches) / n,
        'btts_and_draw': sum((gf > 0 and ga > 0) and gf == ga for gf, ga in team_matches) / n,
        'btts_and_o25': sum((gf > 0 and ga > 0) and (gf + ga > 2.5) for gf, ga in team_matches) / n,
        'btts_no_and_o25': sum(not (gf > 0 and ga > 0) and (gf + ga > 2.5) for gf, ga in team_matches) / n,
    }

def dixon_coles_probabilities(home_xg, away_xg, rho, max_goals=6):
    from scipy.stats import poisson
    home_probs = poisson.pmf(np.arange(max_goals), home_xg)
    away_probs = poisson.pmf(np.arange(max_goals), away_xg)
    
    prob_matrix = np.outer(home_probs, away_probs)
    
    tau_00 = 1 - (home_xg * away_xg * rho)
    tau_01 = 1 + (home_xg * rho)
    tau_10 = 1 + (away_xg * rho)
    tau_11 = 1 - rho
    
    tau_00 = max(0, tau_00)
    tau_01 = max(0, tau_01)
    tau_10 = max(0, tau_10)
    tau_11 = max(0, tau_11)
    
    prob_matrix[0, 0] *= tau_00
    prob_matrix[0, 1] *= tau_01
    prob_matrix[1, 0] *= tau_10
    prob_matrix[1, 1] *= tau_11
    
    prob_matrix = prob_matrix / np.sum(prob_matrix)
    
    home_win_prob = np.sum(np.tril(prob_matrix, -1))
    draw_prob = np.sum(np.diag(prob_matrix))
    away_win_prob = np.sum(np.triu(prob_matrix, 1))
    
    return prob_matrix, home_win_prob, draw_prob, away_win_prob

def get_prediction_data(home_team, away_team):
    try:
        # Load models
        with open("models/lgb_home.pkl", "rb") as f: lgb_home = pickle.load(f)
        with open("models/xgb_home.pkl", "rb") as f: xgb_home = pickle.load(f)
        with open("models/cat_home.pkl", "rb") as f: cat_home = pickle.load(f)
        with open("models/glm_home.pkl", "rb") as f: glm_home = pickle.load(f)
        with open("models/meta_home.pkl", "rb") as f: meta_home = pickle.load(f)
            
        with open("models/lgb_away.pkl", "rb") as f: lgb_away = pickle.load(f)
        with open("models/xgb_away.pkl", "rb") as f: xgb_away = pickle.load(f)
        with open("models/cat_away.pkl", "rb") as f: cat_away = pickle.load(f)
        with open("models/glm_away.pkl", "rb") as f: glm_away = pickle.load(f)
        with open("models/meta_away.pkl", "rb") as f: meta_away = pickle.load(f)
            
        with open("models/optimal_rho.pkl", "rb") as f: optimal_rho = pickle.load(f)
            
        # Load latest stats
        if not os.path.exists("data/team_latest_stats.csv"):
            return {"error": "team_latest_stats.csv not found! Run feature_engineering.py."}
            
        stats = pd.read_csv("data/team_latest_stats.csv")
        stats['date'] = pd.to_datetime(stats['date'])
        
        def get_team_stats(t_name):
            if t_name in stats['team'].values:
                return stats[stats['team'] == t_name].sort_values('date').iloc[-1]
            # Dynamic fallback for newly promoted or unprofiled teams: reasonable league baseline
            return pd.Series({
                'rolling_xg_for': 1.25,
                'rolling_xg_against': 1.65,
                'rolling_np_xg_for': 1.20,
                'rolling_np_xg_against': 1.55,
                'rolling_ppda_for': 12.5,
                'rolling_deep_completions_for': 5.5,
                'rolling_deep_completions_against': 7.5,
                'rolling_ppg': 1.10,
                'rolling_xPoints': 1.15,
                'rolling_gd': -0.40,
                'rest_days': 7.0,
                'fatigue_index': 2.0,
            })
            
        home_stats = get_team_stats(home_team)
        away_stats = get_team_stats(away_team)
        
        # --- Corner Stats ---
        corner_stats = pd.read_csv("data/team_latest_corner_stats.csv")
        corner_stats['date'] = pd.to_datetime(corner_stats['date'])
        
        hc_filter = corner_stats[corner_stats['team'] == home_team]
        if len(hc_filter) == 0:
            home_corner_stats = pd.Series({'rolling_corners_for': 5.0, 'rolling_corners_against': 5.0, 'rolling_sot_for': 4.0})
        else:
            home_corner_stats = hc_filter.sort_values('date').iloc[-1]
            
        ac_filter = corner_stats[corner_stats['team'] == away_team]
        if len(ac_filter) == 0:
            away_corner_stats = pd.Series({'rolling_corners_for': 5.0, 'rolling_corners_against': 5.0, 'rolling_sot_for': 4.0})
        else:
            away_corner_stats = ac_filter.sort_values('date').iloc[-1]
        
        c_features = [
            home_corner_stats['rolling_corners_for'], home_corner_stats['rolling_corners_against'], home_corner_stats['rolling_sot_for'],
            away_corner_stats['rolling_corners_for'], away_corner_stats['rolling_corners_against'], away_corner_stats['rolling_sot_for']
        ]
        X_corner = pd.DataFrame([c_features], columns=[
            'home_rolling_corners_for', 'home_rolling_corners_against', 'home_rolling_sot_for',
            'away_rolling_corners_for', 'away_rolling_corners_against', 'away_rolling_sot_for'
        ]).fillna(0)
        
        with open("models/xgb_home_corners.pkl", "rb") as f: xgb_home_corners = pickle.load(f)
        with open("models/xgb_away_corners.pkl", "rb") as f: xgb_away_corners = pickle.load(f)
        
        exp_home_corners = xgb_home_corners.predict(X_corner)[0]
        exp_away_corners = xgb_away_corners.predict(X_corner)[0]
        
        # --- Form Data ---
        try:
            schedule_df = pd.read_csv("data/schedule.csv")
            home_form = get_team_form(home_team, schedule_df)
            away_form = get_team_form(away_team, schedule_df)
            home_hit_rates = get_team_hit_rates(home_team, schedule_df)
            away_hit_rates = get_team_hit_rates(away_team, schedule_df)
        except Exception as e:
            print("Error loading form data:", e)
            home_form = None
            away_form = None
            home_hit_rates = None
            away_hit_rates = None
        
        # Load advanced histories
        with open("data/team_history.json", "r") as f:
            team_history = json.load(f)
        with open("data/h2h_history.json", "r") as f:
            h2h_history = json.load(f)
            
        elo_df = pd.read_csv("data/team_latest_elo.csv")
        home_elo = elo_df[elo_df['team'] == home_team]['elo'].values[0] if home_team in elo_df['team'].values else 1500
        away_elo = elo_df[elo_df['team'] == away_team]['elo'].values[0] if away_team in elo_df['team'].values else 1500
        elo_diff = home_elo - away_elo
        
        h_hist = team_history.get(home_team, [])
        a_hist = team_history.get(away_team, [])
        
        home_elo_mom = home_elo - h_hist[-5]['elo'] if len(h_hist) >= 5 else home_elo - 1500
        away_elo_mom = away_elo - a_hist[-5]['elo'] if len(a_hist) >= 5 else away_elo - 1500
        
        def get_sos_xg(hist, key):
            if not hist: return np.nan
            recent = hist[-5:]
            w = np.array([0.95**(len(recent)-1-i) for i in range(len(recent))])
            sos = np.array([h['opp_elo']/1500.0 for h in recent])
            vals = np.array([h[key] for h in recent])
            return np.sum(vals * sos * w) / np.sum(w)
            
        home_sos_xg_for = get_sos_xg(h_hist, 'xg_for')
        home_sos_xg_against = get_sos_xg(h_hist, 'xg_ag')
        away_sos_xg_for = get_sos_xg(a_hist, 'xg_for')
        away_sos_xg_against = get_sos_xg(a_hist, 'xg_ag')
        
        matchup1 = f"{home_team}|{away_team}"
        matchup2 = f"{away_team}|{home_team}"
        h2h = h2h_history.get(matchup1, h2h_history.get(matchup2, []))
        
        h2h_home_win = 0.0
        h2h_draw = 0.0
        if len(h2h) >= 4:
            recent = h2h[-10:]
            recent_dates = pd.to_datetime([h['date'] for h in recent])
            current_date = pd.to_datetime(datetime.now().date())
            days_diff = (current_date - recent_dates).days
            weights = np.exp(-0.001 * days_diff)
            
            home_wins = np.array([1 if h['winner'] == home_team else 0 for h in recent])
            draws = np.array([1 if h['winner'] == 'Draw' else 0 for h in recent])
            total_weight = np.sum(weights)
            
            h2h_home_win = np.sum(home_wins * weights) / total_weight
            h2h_draw = np.sum(draws * weights) / total_weight
        
        # Explicit Attack/Defense Interaction with Shrinkage
        # We need league averages for the current season.
        # As an approximation for inference, we'll use a static 1.45 or load it.
        # Actually, since it's inference, let's use 1.45 which is typical, or we can look it up.
        league_avg_xg = 1.45
        N = 5; K = 8
        
        shrunk_home_atk = (home_stats['rolling_xg_for'] * N + league_avg_xg * K) / (N + K)
        shrunk_away_def = (away_stats['rolling_xg_against'] * N + league_avg_xg * K) / (N + K)
        home_attack_defense_lambda = (shrunk_home_atk * shrunk_away_def) / league_avg_xg
        
        shrunk_away_atk = (away_stats['rolling_xg_for'] * N + league_avg_xg * K) / (N + K)
        shrunk_home_def = (home_stats['rolling_xg_against'] * N + league_avg_xg * K) / (N + K)
        away_attack_defense_lambda = (shrunk_away_atk * shrunk_home_def) / league_avg_xg
        
        # --- Missing Players ---
        home_missing_score = 0.0
        away_missing_score = 0.0
        if os.path.exists("data/missing_players_upcoming.csv"):
            try:
                with open('team_mapping.json', 'r') as f:
                    t_map = json.load(f)
                miss_df = pd.read_csv("data/missing_players_upcoming.csv")
                miss_df['team_mapped'] = miss_df['team'].apply(lambda x: t_map.get(x, x))
                miss_df['status_weight'] = np.where(miss_df['status'].astype(str).str.lower().str.contains('doubtful'), 0.5, 1.0)
                
                # Player importance
                if os.path.exists("data/player_season_stats.csv"):
                    try:
                        from thefuzz import process
                        p_stats = pd.read_csv("data/player_season_stats.csv")
                        team_col = 'team' if 'team' in p_stats.columns else ('h_team' if 'h_team' in p_stats.columns else None)
                        if team_col and 'minutes' in p_stats.columns and 'player' in p_stats.columns:
                            p_stats['team_mapped'] = p_stats[team_col].apply(lambda x: t_map.get(x, x))
                            player_mins = p_stats.groupby(['team_mapped', 'player'])['minutes'].sum().reset_index()
                            team_max = player_mins.groupby('team_mapped')['minutes'].max().reset_index().rename(columns={'minutes': 'max_time'})
                            player_mins = pd.merge(player_mins, team_max, on='team_mapped')
                            player_mins['importance'] = player_mins['minutes'] / player_mins['max_time'].clip(lower=1)
                            
                            cache = {team: group for team, group in player_mins.groupby('team_mapped')}
                            def match_imp(row):
                                t = row['team_mapped']
                                if t not in cache: return row['status_weight']
                                choices = cache[t]['player'].tolist()
                                best = process.extractOne(str(row['player']), choices)
                                if best and best[1] >= 70:
                                    imp = cache[t][cache[t]['player'] == best[0]]['importance'].iloc[0]
                                    return row['status_weight'] * max(imp, 0.2)
                                return row['status_weight'] * 0.2
                                
                            miss_df['status_weight'] = miss_df.apply(match_imp, axis=1)
                    except Exception as e:
                        print("Fuzzy importance match failed in prediction:", e)
                
                home_missing = miss_df[miss_df['team_mapped'] == home_team]
                if not home_missing.empty:
                    if 'game_id' in home_missing.columns:
                        home_missing_score = float(home_missing.groupby('game_id')['status_weight'].sum().iloc[0])
                    else:
                        home_missing_score = float(home_missing['status_weight'].sum())
                    
                away_missing = miss_df[miss_df['team_mapped'] == away_team]
                if not away_missing.empty:
                    if 'game_id' in away_missing.columns:
                        away_missing_score = float(away_missing.groupby('game_id')['status_weight'].sum().iloc[0])
                    else:
                        away_missing_score = float(away_missing['status_weight'].sum())
            except Exception as e:
                print("Error calculating missing players score for prediction:", e)
                
        features = [
            home_sos_xg_for, home_sos_xg_against, home_stats['rolling_ppda_for'],
            home_stats['rolling_ppg'], home_stats['rolling_xPoints'], home_stats['rolling_gd'], home_stats['rest_days'], home_stats['fatigue_index'],
            home_stats['rolling_np_xg_for'], home_stats['rolling_np_xg_against'], home_stats['rolling_deep_completions_for'], home_stats['rolling_deep_completions_against'],
            away_sos_xg_for, away_sos_xg_against, away_stats['rolling_ppda_for'],
            away_stats['rolling_ppg'], away_stats['rolling_xPoints'], away_stats['rolling_gd'], away_stats['rest_days'], away_stats['fatigue_index'],
            away_stats['rolling_np_xg_for'], away_stats['rolling_np_xg_against'], away_stats['rolling_deep_completions_for'], away_stats['rolling_deep_completions_against'],
            home_elo, away_elo, elo_diff, home_elo_mom, away_elo_mom,
            h2h_home_win, h2h_draw,
            home_attack_defense_lambda, away_attack_defense_lambda,
            home_missing_score, away_missing_score
        ]
        
        X = pd.DataFrame([features], columns=[
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
        ]).fillna(0)
        
        # Predict xG
        lgb_h_pred = lgb_home.predict(X)
        xgb_h_pred = xgb_home.predict(X)
        cat_h_pred = cat_home.predict(X)
        glm_h_pred = glm_home.predict(X)
        home_xg = meta_home.predict(np.column_stack((lgb_h_pred, xgb_h_pred, cat_h_pred, glm_h_pred)))[0]
        home_xg = max(0.01, home_xg)
        
        lgb_a_pred = lgb_away.predict(X)
        xgb_a_pred = xgb_away.predict(X)
        cat_a_pred = cat_away.predict(X)
        glm_a_pred = glm_away.predict(X)
        away_xg = meta_away.predict(np.column_stack((lgb_a_pred, xgb_a_pred, cat_a_pred, glm_a_pred)))[0]
        away_xg = max(0.01, away_xg)
        
        # Calculate Probabilities
        prob_matrix, p_h, p_d, p_a = dixon_coles_probabilities(home_xg, away_xg, optimal_rho)
        
        # Find Top 3 Exact Scores
        scores = []
        for i in range(6):
            for j in range(6):
                scores.append((i, j, prob_matrix[i, j]))
                
        scores.sort(key=lambda x: x[2], reverse=True)
        top_scores = [{"home_goals": int(s[0]), "away_goals": int(s[1]), "probability": float(s[2])} for s in scores[:3]]
        
        # --- Over 2.5 & BTTS Predictions Slicing ---
        n_goals = prob_matrix.shape[0]
        hg = np.arange(n_goals)[:, None]
        ag = np.arange(n_goals)[None, :]
        tg = hg + ag

        btts_mask = (hg >= 1) & (ag >= 1)
        h_win_mask = hg > ag
        a_win_mask = ag > hg
        draw_mask = hg == ag

        def p_mask(mask):
            return float(prob_matrix[mask].sum())

        btts_preds = {
            'over_0_5': p_mask(tg > 0.5),
            'over_1_5': p_mask(tg > 1.5),
            'over_2_5': p_mask(tg > 2.5),
            'over_3_5': p_mask(tg > 3.5),
            'over_4_5': p_mask(tg > 4.5),
            'btts': p_mask(btts_mask),
            'btts_and_win': p_mask(btts_mask & (h_win_mask | a_win_mask)),
            'btts_and_draw': p_mask(btts_mask & draw_mask),
            'btts_and_o25': p_mask(btts_mask & (tg > 2.5)),
            'btts_no_and_o25': p_mask(~btts_mask & (tg > 2.5))
        }
        
        btts_predictions = {
            "home_rates": home_hit_rates,
            "away_rates": away_hit_rates,
            "prediction": btts_preds
        }
        
        # --- Corner Output ---
        from scipy.stats import poisson
        exp_total_corners = exp_home_corners + exp_away_corners
        
        corner_probs = []
        for k in range(5, 16):
            prob_home = (1 - poisson.cdf(k, exp_home_corners))
            prob_away = (1 - poisson.cdf(k, exp_away_corners))
            prob_total = (1 - poisson.cdf(k, exp_total_corners))
            corner_probs.append({
                "line": float(k + 0.5),
                "home_over_prob": float(prob_home),
                "away_over_prob": float(prob_away),
                "total_over_prob": float(prob_total)
            })
            
        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_xg": float(home_xg),
            "away_xg": float(away_xg),
            "home_win_prob": float(p_h),
            "draw_prob": float(p_d),
            "away_win_prob": float(p_a),
            "top_exact_scores": top_scores,
            "exp_home_corners": float(exp_home_corners),
            "exp_away_corners": float(exp_away_corners),
            "exp_total_corners": float(exp_total_corners),
            "corner_over_probs": corner_probs,
            "home_form": home_form,
            "away_form": away_form,
            "btts_predictions": btts_predictions
        }
        
    except Exception as e:
        return {"error": f"Error predicting match: {e}"}

def predict_match(home_team, away_team):
    data = get_prediction_data(home_team, away_team)
    if "error" in data:
        print(data["error"])
        return
        
    home_xg = data["home_xg"]
    away_xg = data["away_xg"]
    p_h = data["home_win_prob"]
    p_d = data["draw_prob"]
    p_a = data["away_win_prob"]
    
    print(f"\n=====================================")
    print(f" Prediction: {home_team} vs {away_team}")
    print(f"=====================================")
    print(f" Expected Goals: {home_team} {home_xg:.2f} - {away_xg:.2f} {away_team}")
    print(f"-------------------------------------")
    print(f" Match Odds:")
    print(f"   Home Win ({home_team}): {p_h*100:.2f}%")
    print(f"   Draw: {p_d*100:.2f}%")
    print(f"   Away Win ({away_team}): {p_a*100:.2f}%")
    print(f"-------------------------------------")
    
    print(f" Top 3 Most Likely Exact Scores:")
    for score in data["top_exact_scores"]:
        print(f"   {home_team} {score['home_goals']} - {score['away_goals']} {away_team}  ({score['probability']*100:.2f}%)")
        
    print(f"=====================================")
    
    print(f"\n=====================================")
    print(f" Corner Prediction: {home_team} vs {away_team}")
    print(f"=====================================")
    print(f" Expected Corners: {home_team} {data['exp_home_corners']:.2f} - {data['exp_away_corners']:.2f} {away_team} (Total: {data['exp_total_corners']:.2f})")
    print(f"--------------------------------------------------")
    print(f"{'Match Corners':<20} | {home_team:<10} | {away_team:<10} | Total")
    print(f"--------------------------------------------------")
    
    for c in data["corner_over_probs"]:
        label = f"Over {c['line']}"
        print(f"{label:<20} | {c['home_over_prob']*100:>5.1f}%     | {c['away_over_prob']*100:>5.1f}%     | {c['total_over_prob']*100:>5.1f}%")
        
    print(f"==================================================\n")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        predict_match(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python predict.py 'Home Team' 'Away Team'")
        print("Example: python predict.py 'Arsenal' 'Chelsea'")
