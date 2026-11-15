import soccerdata as sd
for c in ['ClubElo', 'ESPN', 'FBref', 'MatchHistory', 'Sofascore', 'SoFIFA', 'Understat', 'WhoScored']:
    print(c)
    methods = [m for m in dir(getattr(sd, c)) if not m.startswith("_")]
    for m in methods:
        print("  -", m)
