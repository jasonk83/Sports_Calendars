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

    # Dictionary to dynamically map host cities to their exact timezones
    timezone_map = {
        "vancouver": "America/Vancouver",
        "seattle": "America/Los_Angeles",
        "san francisco": "America/Los_Angeles",
        "santa clara": "America/Los_Angeles",
        "los angeles": "America/Los_Angeles",
        "inglewood": "America/Los_Angeles",
        "guadalajara": "America/Mexico_City",
        "mexico city": "America/Mexico_City",
        "monterrey": "America/Monterrey",
        "dallas": "America/Chicago",
        "arlington": "America/Chicago",
        "houston": "America/Chicago",
        "kansas city": "America/Chicago",
        "atlanta": "America/New_York",
        "miami": "America/New_York",
        "boston": "America/New_York",
        "foxborough": "America/New_York",
        "new york": "America/New_York",
        "new jersey": "America/New_York",
        "east rutherford": "America/New_York",
        "philadelphia": "America/New_York",
        "toronto": "America/Toronto"
    }

    for match in matches:
        event = Event()
        team1 = match.get("team1", "TBD")
        team2 = match.get("team2", "TBD")
        
        event.name = f"⚽ {team1} vs {team2}"
        
        date_str = match.get("date")
        time_str = match.get("time") 
        stadium = match.get("ground", "").lower()
        
        # Default to Eastern Time if a stadium isn't found
        match_tz = "America/New_York" 
        for key, tz in timezone_map.items():
            if key in stadium:
                match_tz = tz
                break
        
        try:
            # 1. Parse the local stadium time
            naive_time = datetime.strptime(f"{date_str} {time_str[:5]}", "%Y-%m-%d %H:%M")
            
            # 2. Assign the specific timezone based on where the stadium is located
            stadium_time = naive_time.replace(tzinfo=ZoneInfo(match_tz))
            
            # 3. Convert universally to UTC so Google Calendar translates it flawlessly
            utc_time = stadium_time.astimezone(ZoneInfo("UTC"))
            
            event.begin = utc_time
            event.end = utc_time + timedelta(hours=2) 
        except Exception as e:
            print(f"Skipping match due to time parsing error: {e}")
            continue

        # Using title() to capitalize the stadium name cleanly
        event.location = match.get("ground", "TBD Stadium").title()
        event.description = f"Group: {match.get('group', 'TBD')} | Round: {match.get('round', 'TBD')}"
        cal.events.add(event)

    with open('world_cup_2026.ics', 'w', encoding='utf-8') as my_file:
        my_file.writelines(cal.serialize_iter())
    print("Successfully updated world_cup_2026.ics")

if __name__ == "__main__":
    fetch_and_build_calendar()
