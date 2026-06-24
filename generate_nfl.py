import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def fetch_espn_schedule(sport, league, team_abbr, emoji, output_file):
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{team_abbr}/schedule"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Failed to fetch {team_abbr} data.")
        return

    data = response.json()
    cal = Calendar()
    
    for item in data.get("events", []):
        event = Event()
        name = item.get("name", "Unknown Matchup")
        event.name = f"{emoji} {name}"
        
        time_str = item.get("date") 
        if not time_str:
            continue
            
        try:
            clean_time = time_str.replace('Z', '')
            utc_time = datetime.strptime(clean_time, "%Y-%m-%dT%H:%M").replace(tzinfo=ZoneInfo("UTC"))
            eastern_time = utc_time.astimezone(ZoneInfo("America/New_York"))
            
            event.begin = eastern_time
            event.end = eastern_time + timedelta(hours=3, minutes=15) # NFL games run slightly longer
            
            competitions = item.get("competitions", [])
            if competitions and "venue" in competitions[0]:
                event.location = competitions[0]["venue"].get("fullName", "TBD Stadium")
                
            cal.events.add(event)
        except Exception as e:
            print(f"Skipping match due to error: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print(f"Successfully updated {output_file}")

if __name__ == "__main__":
    # Fetch Chicago Bears
    fetch_espn_schedule("football", "nfl", "chi", "🏈", "bears_schedule.ics")
    # Fetch New England Patriots
    fetch_espn_schedule("football", "nfl", "ne", "🏈", "patriots_schedule.ics")
