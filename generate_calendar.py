import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def fetch_and_build_calendar():
    # Placeholder for your chosen API endpoint
    API_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
    
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("Error: Failed to fetch match data.")
        return

    data = response.json()
    matches = data.get("matches", [])
    cal = Calendar()

    for match in matches:
        event = Event()
        team1 = match.get("team1", "TBD")
        team2 = match.get("team2", "TBD")
        
        # --- UPDATED LINE ---
        event.name = f"⚽ {team1} vs {team2}"
        
        date_str = match.get("date")
        time_str = match.get("time") 
        
        try:
            naive_time = datetime.strptime(f"{date_str} {time_str[:5]}", "%Y-%m-%d %H:%M")
            utc_time = naive_time.replace(tzinfo=ZoneInfo("UTC"))
            eastern_time = utc_time.astimezone(ZoneInfo("America/New_York"))
            
            event.begin = eastern_time
            # Standard match length + buffer
            event.end = eastern_time + timedelta(hours=2) 
        except Exception as e:
            print(f"Skipping match due to time parsing error: {e}")
            continue

        event.location = match.get("ground", "TBD Stadium")
        event.description = f"Group: {match.get('group', 'TBD')} | Round: {match.get('round', 'TBD')}"
        cal.events.add(event)

        # --- UPDATED LINE (added encoding='utf-8' to handle the emoji safely) ---
    with open('world_cup_2026.ics', 'w', encoding='utf-8') as my_file:
        my_file.writelines(cal.serialize_iter())
    print("Successfully updated world_cup_2026.ics")

if __name__ == "__main__":
    fetch_and_build_calendar()
