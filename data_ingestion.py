import json
import os
import pathlib
import urllib.request
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import pandas as pd
import soccerdata as sd
from soccerdata._config import DATA_DIR

# Create data directory
os.makedirs("data", exist_ok=True)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _purge_corrupt_cache(cache_dir: str) -> None:
    """Delete any soccerdata JSON cache files that contain HTML instead of JSON."""
    purged = 0
    for f in pathlib.Path(cache_dir).rglob("*.json"):
        try:
            with f.open("rb") as fh:
                first = fh.read(16).lstrip()
            if first.startswith(b"<"):          # HTML, not JSON
                f.unlink()
                print(f"  Purged corrupt cache: {f.name}")
                purged += 1
        except Exception:
            pass
    if purged:
        print(f"  Removed {purged} corrupt cache file(s).")


# ---------------------------------------------------------------------------
# Fast Missing Players Scraper (SportsGambler — ~2 seconds, No Selenium)
# ---------------------------------------------------------------------------

INJURY_URLS = {
    "ENG-Premier League": "https://www.sportsgambler.com/injuries/football/england-premier-league/",
    "ESP-La Liga": "https://www.sportsgambler.com/injuries/football/spain-la-liga/",
    "GER-Bundesliga": "https://www.sportsgambler.com/injuries/football/germany-bundesliga/",
}


def fetch_missing_players() -> pd.DataFrame:
    """Fetches real-time injuries and suspensions via direct HTTP request (~2s)."""
    print("Fetching missing players & injuries (fast HTTP)...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    now_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")
    rows = []

    for league, url in INJURY_URLS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                soup = BeautifulSoup(resp.read(), "html.parser")

            blocks = soup.find_all("div", class_="injury-block")
            for block in blocks:
                h3 = block.find("h3", class_="injuries-title")
                if not h3:
                    continue
                team = h3.get_text(strip=True)
                for row in block.find_all("div", class_="inj-row"):
                    c = row.find("div", class_="inj-container")
                    if not c:
                        c = row
                    type_span = c.find("span", class_="inj-type")
                    player_span = c.find("span", class_="inj-player")
                    info_span = c.find("span", class_="inj-info")
                    if not player_span:
                        continue

                    inj_classes = type_span.get("class", []) if type_span else []
                    reason_text = info_span.get_text(strip=True) if info_span else ""

                    if any(x in inj_classes for x in ["redcard", "yellowcard", "yellowredcard"]):
                        status = "Suspended"
                    elif "doubtful" in reason_text.lower() or "doubt" in reason_text.lower():
                        status = "Doubtful"
                    else:
                        status = "Out"

                    rows.append({
                        "league": league,
                        "team": team,
                        "player": player_span.get_text(strip=True),
                        "reason": reason_text,
                        "status": status,
                        "date": now_str,
                    })
        except Exception as e:
            print(f"  Warning: Could not fetch injuries for {league}: {e}")

    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv("data/missing_players_upcoming.csv", index=False)
        print(f"  Saved {len(df)} missing players to data/missing_players_upcoming.csv")
    else:
        print("  Warning: No missing players found or connection timed out.")
    return df


# ---------------------------------------------------------------------------
# Upcoming Fixtures Ingestion (2026/27 Season Schedule)
# ---------------------------------------------------------------------------

FIXTURE_FEEDS = [
    ("ENG-Premier League", "epl-2026", 1),
    ("ESP-La Liga", "la-liga-2026", 3),
    ("GER-Bundesliga", "bundesliga-2026", 4),
]

TEAM_NAME_OVERRIDES = {
    "Spurs": "Tottenham", "Man Utd": "Manchester United", "Man City": "Manchester City",
    "Nott'm Forest": "Nottingham Forest", "Newcastle": "Newcastle United",
    "Wolves": "Wolverhampton Wanderers", "Brighton": "Brighton", "West Ham": "West Ham",
    "Leicester": "Leicester", "Leeds": "Leeds", "Coventry": "Coventry", "Sunderland": "Sunderland",
    "Atlético de Madrid": "Atletico Madrid", "CA Osasuna": "Osasuna", "Deportivo Alavés": "Alaves",
    "Elche CF": "Elche", "FC Barcelona": "Barcelona", "Getafe CF": "Getafe", "Levante UD": "Levante",
    "R. Racing Club": "Racing Santander", "RC Deportivo": "Deportivo La Coruna",
    "RCD Espanyol de Barcelona": "Espanyol", "Sevilla FC": "Sevilla", "Valencia CF": "Valencia",
    "Villarreal CF": "Villarreal", "Real Betis": "Real Betis", "Real Madrid": "Real Madrid",
    "Real Sociedad": "Real Sociedad", "Rayo Vallecano": "Rayo Vallecano", "Girona FC": "Girona",
    "RCD Mallorca": "Mallorca", "Celta de Vigo": "Celta Vigo", "Athletic Club": "Athletic Club",
    "Real Valladolid": "Real Valladolid", "CD Leganés": "Leganes", "UD Las Palmas": "Las Palmas",
    "Málaga CF": "Malaga",
    "1. FC Köln": "FC Cologne", "1. FC Union Berlin": "Union Berlin", "1. FSV Mainz 05": "Mainz 05",
    "Bayer 04 Leverkusen": "Bayer Leverkusen", "Borussia Dortmund": "Borussia Dortmund",
    "Borussia Mönchengladbach": "Borussia M.Gladbach", "Eintracht Frankfurt": "Eintracht Frankfurt",
    "FC Augsburg": "Augsburg", "FC Bayern München": "Bayern Munich", "FC St. Pauli": "St. Pauli",
    "Hamburger SV": "Hamburger SV", "RB Leipzig": "RasenBallsport Leipzig",
    "SV Werder Bremen": "Werder Bremen", "Sport-Club Freiburg": "Freiburg",
    "TSG Hoffenheim": "Hoffenheim", "VfB Stuttgart": "VfB Stuttgart", "VfL Wolfsburg": "Wolfsburg",
    "VfL Bochum 1848": "Bochum", "1. FC Heidenheim 1846": "FC Heidenheim",
    "Holstein Kiel": "Holstein Kiel", "SV Darmstadt 98": "Darmstadt",
    "Fortuna Düsseldorf": "Fortuna Duesseldorf", "SV Elversberg": "Elversberg",
    "FC Schalke 04": "Schalke 04", "SC Paderborn 07": "Paderborn"
}


def fetch_upcoming_fixtures() -> pd.DataFrame:
    """
    Fetches the 2026/27 upcoming fixtures across EPL, La Liga, and Bundesliga.
    Returns a dataframe compatible with schedule.csv schema.
    """
    print("Fetching upcoming fixtures (2026/27 season)...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    t_map = {}
    if os.path.exists("team_mapping.json"):
        with open("team_mapping.json", "r") as f:
            t_map = json.load(f)
    full_map = {**t_map, **TEAM_NAME_OVERRIDES}

    fixtures = []
    for league_name, code, l_id in FIXTURE_FEEDS:
        try:
            url = f"https://fixturedownload.com/feed/json/{code}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for m in data:
                is_result = m.get("HomeTeamScore") is not None
                h_team = full_map.get(m["HomeTeam"], m["HomeTeam"])
                a_team = full_map.get(m["AwayTeam"], m["AwayTeam"])
                date_str = m["DateUtc"].replace("Z", "").replace("T", " ")
                game_title = f"{date_str[:10]} {h_team}-{a_team}"

                fixtures.append({
                    "league": league_name,
                    "season": 2627,
                    "game": game_title,
                    "league_id": l_id,
                    "season_id": 2026,
                    "game_id": 100000 + m["MatchNumber"],
                    "date": date_str,
                    "home_team_id": 0,
                    "away_team_id": 0,
                    "home_team": h_team,
                    "away_team": a_team,
                    "away_team_code": "",
                    "home_team_code": "",
                    "home_goals": m.get("HomeTeamScore") if is_result else None,
                    "away_goals": m.get("AwayTeamScore") if is_result else None,
                    "home_xg": None,
                    "away_xg": None,
                    "is_result": is_result,
                    "has_data": False,
                    "url": "",
                })
        except Exception as e:
            print(f"  Warning: Could not fetch upcoming fixtures for {league_name}: {e}")

    df = pd.DataFrame(fixtures)
    unplayed = df[df["is_result"] == False] if not df.empty else df
    print(f"  Fetched {len(unplayed)} upcoming unplayed fixtures across 3 leagues.")
    return df


# ---------------------------------------------------------------------------
# Ingestion Orchestration
# ---------------------------------------------------------------------------

def ingest_data(leagues=["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga"],
                seasons=["2425", "2526"]):
    print("Checking for corrupt cache files...")
    _purge_corrupt_cache(str(DATA_DIR / "Understat"))

    # Check if local Understat & MatchHistory cache is available
    schedule_file = "data/schedule.csv"
    match_stats_file = "data/match_stats.csv"
    player_stats_file = "data/player_season_stats.csv"
    match_history_file = "data/match_history.csv"

    # Try live fetch from Understat, but fall back gracefully to local data if Understat is down
    try:
        print(f"Fetching historical stats for {leagues}, seasons: {seasons}...")
        understat = sd.Understat(leagues=leagues, seasons=seasons)
        schedule = understat.read_schedule().reset_index(drop=True)
        match_stats = understat.read_team_match_stats()
        player_stats = understat.read_player_season_stats().reset_index()

        schedule.to_csv(schedule_file, index=False)
        match_stats.to_csv(match_stats_file)
        player_stats.to_csv(player_stats_file, index=False)
    except Exception as e:
        print(f"  Understat temporarily unavailable ({e}). Using existing historical data in data/.")
        if os.path.exists(schedule_file):
            schedule = pd.read_csv(schedule_file)
            # Filter out any previously appended 2627 upcoming matches to prevent duplicates
            schedule = schedule[schedule["season"] != 2627].reset_index(drop=True)
        else:
            schedule = pd.DataFrame()

    # Try MatchHistory fetch
    try:
        print("  Reading MatchHistory (corners, fouls)...")
        history_dfs = []
        for s in seasons:
            try:
                h = sd.MatchHistory(leagues=leagues, seasons=s)
                history_dfs.append(h.read_games())
            except Exception as e:
                print(f"  Skipping MatchHistory for season {s}: {e}")
        if history_dfs:
            match_history = pd.concat(history_dfs)
            match_history.to_csv(match_history_file)
    except Exception as e:
        print(f"  MatchHistory fetch skipped: {e}")

    # Fetch real upcoming 2026/27 fixtures
    upcoming_sched = fetch_upcoming_fixtures()

    # Combine historical schedule with upcoming 2026/27 fixtures
    if not upcoming_sched.empty:
        if not schedule.empty:
            schedule_combined = pd.concat([schedule, upcoming_sched], ignore_index=True)
        else:
            schedule_combined = upcoming_sched
    else:
        schedule_combined = schedule

    schedule_combined.to_csv(schedule_file, index=False)

    # Fast Injuries & Missing Players
    fetch_missing_players()

    print("\nData ingestion complete! Saved all datasets to data/ directory.")


if __name__ == "__main__":
    ingest_data()
