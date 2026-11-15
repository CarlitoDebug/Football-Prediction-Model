from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime
from predict import get_prediction_data

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes & origins

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "service": "FootyPredict API",
        "endpoints": [
            "/api/teams",
            "/api/fixtures",
            "/api/predict",
            "/api/h2h",
            "/api/league-stats"
        ]
    })

@app.route('/api/teams', methods=['GET'])
def get_teams():
    all_teams = set()
    if os.path.exists("team_mapping.json"):
        try:
            with open("team_mapping.json", "r") as f:
                mapping = json.load(f)
            all_teams.update(mapping.values())
        except Exception as e:
            print("Error loading team_mapping.json:", e)

    if os.path.exists("data/schedule.csv"):
        try:
            df = pd.read_csv("data/schedule.csv")
            all_teams.update(df['home_team'].dropna().unique())
            all_teams.update(df['away_team'].dropna().unique())
        except Exception as e:
            print("Error loading schedule teams:", e)

    teams = sorted(list(all_teams))
    return jsonify({"teams": teams})

def sanitize_nans(obj):
    """Recursively replaces float('nan') with None/0.0 to produce valid JSON."""
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return 0.0
    elif isinstance(obj, dict):
        return {k: sanitize_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_nans(item) for item in obj]
    return obj

@app.route('/api/predict', methods=['GET'])
def predict():
    home_team = request.args.get('home_team')
    away_team = request.args.get('away_team')
    
    if not home_team or not away_team:
        return jsonify({"detail": "home_team and away_team parameters are required"}), 400
        
    data = get_prediction_data(home_team, away_team)
    if "error" in data:
        return jsonify({"detail": data["error"]}), 400
    return jsonify(sanitize_nans(data))

@app.route('/api/h2h', methods=['GET'])
def get_h2h():
    home_team = request.args.get('home_team')
    away_team = request.args.get('away_team')
    
    if not home_team or not away_team:
        return jsonify({"detail": "home_team and away_team parameters are required"}), 400
        
    if not os.path.exists("data/schedule.csv"):
        return jsonify({"detail": "data/schedule.csv not found"}), 404
        
    df = pd.read_csv("data/schedule.csv")
    
    mask = (((df['home_team'] == home_team) & (df['away_team'] == away_team)) |
            ((df['home_team'] == away_team) & (df['away_team'] == home_team)))
    
    h2h = df[mask & (df['is_result'] == True)].copy()
    
    if len(h2h) == 0:
        return jsonify({"summary": None, "recent_matches": []})
        
    h2h['date'] = pd.to_datetime(h2h['date'])
    h2h = h2h.sort_values('date', ascending=False)
    
    total_matches = len(h2h)
    home_wins = 0
    away_wins = 0
    draws = 0
    
    home_goals_total = 0
    away_goals_total = 0
    over_1_5 = 0
    over_2_5 = 0
    over_3_5 = 0
    btts = 0
    home_clean_sheets = 0
    away_clean_sheets = 0
    
    for _, row in h2h.iterrows():
        h_goals = int(row['home_goals'])
        a_goals = int(row['away_goals'])
        
        if h_goals > a_goals:
            if row['home_team'] == home_team:
                home_wins += 1
            else:
                away_wins += 1
        elif h_goals < a_goals:
            if row['away_team'] == away_team:
                away_wins += 1
            else:
                home_wins += 1
        else:
            draws += 1
            
        total_match_goals = h_goals + a_goals
        if total_match_goals > 1.5: over_1_5 += 1
        if total_match_goals > 2.5: over_2_5 += 1
        if total_match_goals > 3.5: over_3_5 += 1
        
        if h_goals > 0 and a_goals > 0:
            btts += 1
            
        if row['home_team'] == home_team:
            home_goals_total += h_goals
            away_goals_total += a_goals
            if a_goals == 0: home_clean_sheets += 1
            if h_goals == 0: away_clean_sheets += 1
        else:
            home_goals_total += a_goals
            away_goals_total += h_goals
            if h_goals == 0: home_clean_sheets += 1
            if a_goals == 0: away_clean_sheets += 1
            
    recent = h2h.head(10)
    recent_matches = []
    
    for _, row in recent.iterrows():
        recent_matches.append({
            "date": row['date'].strftime("%b %d, %Y"),
            "home_team": row['home_team'],
            "away_team": row['away_team'],
            "home_goals": int(row['home_goals']),
            "away_goals": int(row['away_goals'])
        })
        
    return jsonify(sanitize_nans({
        "summary": {
            "total_matches": total_matches,
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": draws,
            "home_goals": home_goals_total,
            "away_goals": away_goals_total,
            "over_1_5": over_1_5,
            "over_2_5": over_2_5,
            "over_3_5": over_3_5,
            "btts": btts,
            "home_clean_sheets": home_clean_sheets,
            "away_clean_sheets": away_clean_sheets
        },
        "recent_matches": recent_matches
    }))

@app.route('/api/fixtures', methods=['GET'])
def get_fixtures():
    league = request.args.get('league')
    
    if not os.path.exists("data/schedule.csv"):
        return jsonify({"detail": "data/schedule.csv not found"}), 404
        
    df = pd.read_csv("data/schedule.csv")
    
    # Calculate absolute matchweek per league and season
    df['date_dt'] = pd.to_datetime(df['date'])
    df['iso_week'] = df['date_dt'].dt.isocalendar().year * 100 + df['date_dt'].dt.isocalendar().week
    df['matchweek'] = df.groupby(['league', 'season'])['iso_week'].transform(lambda x: x.map({w: i+1 for i, w in enumerate(sorted(x.unique()))}))
    
    upcoming = df[df['is_result'] == False].copy()
    upcoming['date'] = pd.to_datetime(upcoming['date'])
    upcoming = upcoming.sort_values('date')
    
    if league and league != "All":
        upcoming = upcoming[upcoming['league'] == league]
        
    fixtures = []
    for _, row in upcoming.iterrows():
        fixtures.append({
            "date": row['date'].strftime("%Y-%m-%d %H:%M"),
            "matchweek": int(row['matchweek']),
            "home_team": row['home_team'],
            "away_team": row['away_team'],
            "league": row['league']
        })
        
    return jsonify(sanitize_nans({"fixtures": fixtures}))

@app.get("/api/league-stats")
def get_league_stats():
    league = request.args.get('league')
    if not league:
        return jsonify({"error": "league parameter is required"}), 400
        
    df = pd.read_csv('data/schedule.csv')
    
    # Get the latest season for this league
    df_league_all = df[df['league'] == league]
    if df_league_all.empty:
        return jsonify({"error": "League not found"}), 404
        
    latest_season = int(df_league_all['season'].max())
    df_league = df_league_all[(df_league_all['season'] == latest_season) & (df_league_all['is_result'] == True)].copy()
    
    if df_league.empty:
        return jsonify({"error": f"No results found for {league} in season {latest_season}"}), 404
        
    teams = pd.concat([df_league['home_team'], df_league['away_team']]).unique()
    
    table = []
    for team in teams:
        home_matches = df_league[df_league['home_team'] == team]
        away_matches = df_league[df_league['away_team'] == team]
        
        mp = len(home_matches) + len(away_matches)
        if mp == 0: continue
        
        wins = len(home_matches[home_matches['home_goals'] > home_matches['away_goals']]) + \
               len(away_matches[away_matches['away_goals'] > away_matches['home_goals']])
               
        draws = len(home_matches[home_matches['home_goals'] == home_matches['away_goals']]) + \
                len(away_matches[away_matches['away_goals'] == away_matches['home_goals']])
                
        losses = len(home_matches[home_matches['home_goals'] < home_matches['away_goals']]) + \
                 len(away_matches[away_matches['away_goals'] < away_matches['home_goals']])
                 
        gf = home_matches['home_goals'].sum() + away_matches['away_goals'].sum()
        ga = home_matches['away_goals'].sum() + away_matches['home_goals'].sum()
        gd = gf - ga
        pts = (wins * 3) + (draws * 1)
        ppg = pts / mp if mp > 0 else 0
        
        clean_sheets = len(home_matches[home_matches['away_goals'] == 0]) + \
                       len(away_matches[away_matches['home_goals'] == 0])
        cs_pct = clean_sheets / mp if mp > 0 else 0
        
        btts_home = len(home_matches[(home_matches['home_goals'] > 0) & (home_matches['away_goals'] > 0)])
        btts_away = len(away_matches[(away_matches['home_goals'] > 0) & (away_matches['away_goals'] > 0)])
        btts_pct = (btts_home + btts_away) / mp if mp > 0 else 0
        
        xgf = home_matches['home_xg'].sum() + away_matches['away_xg'].sum()
        avg_xgf = xgf / mp if mp > 0 else 0
        
        over_15_home = len(home_matches[(home_matches['home_goals'] + home_matches['away_goals']) > 1.5])
        over_15_away = len(away_matches[(away_matches['home_goals'] + away_matches['away_goals']) > 1.5])
        over_15_pct = (over_15_home + over_15_away) / mp if mp > 0 else 0
        
        over_25_home = len(home_matches[(home_matches['home_goals'] + home_matches['away_goals']) > 2.5])
        over_25_away = len(away_matches[(away_matches['home_goals'] + away_matches['away_goals']) > 2.5])
        over_25_pct = (over_25_home + over_25_away) / mp if mp > 0 else 0
        
        avg_goals = (gf + ga) / mp if mp > 0 else 0
        
        all_matches = pd.concat([home_matches, away_matches]).sort_values(by='date', ascending=False)
        last_5 = all_matches.head(5)
        form = []
        for _, row in last_5.iterrows():
            if row['home_team'] == team:
                if row['home_goals'] > row['away_goals']: form.append('W')
                elif row['home_goals'] < row['away_goals']: form.append('L')
                else: form.append('D')
            else:
                if row['away_goals'] > row['home_goals']: form.append('W')
                elif row['away_goals'] < row['home_goals']: form.append('L')
                else: form.append('D')
                
        table.append({
            'team': team, 'mp': mp, 'w': wins, 'd': draws, 'l': losses, 'gf': float(gf), 'ga': float(ga), 'gd': float(gd),
            'pts': pts, 'ppg': float(round(ppg, 2)), 'cs_pct': int(round(cs_pct * 100)), 'btts_pct': int(round(btts_pct * 100)),
            'xgf': float(round(avg_xgf, 2)), 'over_15': int(round(over_15_pct * 100)), 'over_25': int(round(over_25_pct * 100)),
            'avg': float(round(avg_goals, 2)), 'form': form[::-1]
        })

    table.sort(key=lambda x: (x['pts'], x['gd'], x['gf']), reverse=True)
    for idx, row in enumerate(table):
        row['rank'] = idx + 1

    total_matches = len(df_league)
    home_wins = len(df_league[df_league['home_goals'] > df_league['away_goals']])
    draws = len(df_league[df_league['home_goals'] == df_league['away_goals']])
    away_wins = len(df_league[df_league['home_goals'] < df_league['away_goals']])

    league_metrics = {
        'total_matches': total_matches,
        'home_win_pct': int(round((home_wins / total_matches) * 100)) if total_matches > 0 else 0,
        'draw_pct': int(round((draws / total_matches) * 100)) if total_matches > 0 else 0,
        'away_win_pct': int(round((away_wins / total_matches) * 100)) if total_matches > 0 else 0,
    }

    ou_metrics = {}
    df_league['total_goals'] = df_league['home_goals'] + df_league['away_goals']
    for threshold in [0.5, 1.5, 2.5, 3.5, 4.5]:
        over = len(df_league[df_league['total_goals'] > threshold])
        ou_metrics[f'over_{threshold}'] = int(round((over / total_matches) * 100)) if total_matches > 0 else 0
        ou_metrics[f'under_{threshold}'] = 100 - ou_metrics[f'over_{threshold}']
        
    freq_goals = df_league['total_goals'].value_counts(normalize=True).head(6).to_dict()
    freq_goals_formatted = [{'goals': int(k), 'pct': float(round(v * 100, 1)), 'count': int(df_league['total_goals'].value_counts()[k])} for k, v in freq_goals.items()]

    df_league['scoreline'] = df_league.apply(lambda x: f"{int(max(x['home_goals'], x['away_goals']))}-{int(min(x['home_goals'], x['away_goals']))}", axis=1)
    freq_scores = df_league['scoreline'].value_counts(normalize=True).head(6).to_dict()
    freq_scores_formatted = [{'score': k, 'pct': float(round(v * 100, 1)), 'count': int(df_league['scoreline'].value_counts()[k])} for k, v in freq_scores.items()]

    final_data = {
        'league': league,
        'season': latest_season,
        'table': table,
        'metrics': league_metrics,
        'ou': ou_metrics,
        'frequent_goals': freq_goals_formatted,
        'frequent_scores': freq_scores_formatted
    }

    return jsonify(sanitize_nans(final_data))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
