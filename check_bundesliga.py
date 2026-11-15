import soccerdata as sd

try:
    understat = sd.Understat(leagues="GER-Bundesliga", seasons="2627", no_cache=True)
    sched = understat.read_schedule()
    upcoming = sched[sched['is_result'] == False]
    print(f"Total Bundesliga 26/27 games: {len(sched)}")
    print(f"Upcoming Bundesliga 26/27 games: {len(upcoming)}")
except Exception as e:
    print(f"Error fetching Bundesliga: {e}")
