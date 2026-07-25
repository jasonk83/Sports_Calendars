import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def fetch_espn_schedule(sport, league, team_id, emoji, output_file):
    base_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/schedule"
    
    # ESPN separates past games and future games. We need to scrape both!
    urls = [
        base_url,                  # Gets all completed games
        f"{base_url}?fixture=true" # Gets all future upcoming games
    ]
    
    cal = Calendar()
    
    # Loop through both URLs and combine the results
    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Warning: Failed to fetch data from {url}")
            continue

        data = response.json()
        
        for item in data.get("events", []):
            event = Event()
            name = item.get("name", "Unknown Matchup")
            event.name = f"{emoji} {name}"
            
            time_str = item.get("date") 
            if not time_str:
                continue
                
            try:
                clean_time = time_str.replace('Z', '')
                utc_time = datetime.fromisoformat(clean_time).replace(tzinfo=ZoneInfo("UTC"))
                eastern_time = utc_time.astimezone(ZoneInfo("America/New_York"))
                
                event.begin = eastern_time
                event.end = eastern_time + timedelta(hours=2)
                
                competitions = item.get("competitions", [])
                if competitions and "venue" in competitions[0]:
                    event.location = competitions[0]["venue"].get("fullName", "TBD Pitch")
                    
                cal.events.add(event)
            except Exception as e:
                print(f"Skipping match due to error: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print(f"Successfully updated {output_file}")

if __name__ == "__main__":
    fetch_espn_schedule("soccer", "all", "193", "🛡️", "dc_united_schedule.ics")
