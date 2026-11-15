import pandas as pd
import soccerdata as sd

def test():
    try:
        ws = sd.WhoScored(leagues=["ENG-Premier League"], seasons="2020-21")
        hist = ws.read_missing_players(match_id=[1485184])
        print("Success! Data shape:", hist.shape)
        print(hist.head())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
