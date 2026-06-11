import requests
from ics import Calendar, Event
from datetime import datetime, timedelta

def fetch_and_build_calendar():
    # Placeholder for your chosen API endpoint
    # Example: A free community-maintained JSON or a paid sports API
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
        
        event.name = f"World Cup 2026: {team1} vs {team2}"
        
        # You will need to adjust the time parsing based on your API's specific format
        date_str = match.get("date") # e.g., "2026-06-11"
        time_str = match.get("time") # e.g., "15:00"
        
        try:
            # Assuming the API provides UTC time
            start_time = datetime.strptime(f"{date_str} {time_str[:5]}", "%Y-%m-%d %H:%M")
            event.begin = start_time
            # Standard match length + buffer
            event.end = start_time + timedelta(hours=2) 
        except Exception as e:
            print(f"Skipping match due to time parsing error: {e}")
            continue

        event.location = match.get("ground", "TBD Stadium")
        event.description = f"Group: {match.get('group', 'TBD')} | Round: {match.get('round', 'TBD')}"
        cal.events.add(event)

    # Export the calendar file
    with open('world_cup_2026.ics', 'w') as my_file:
        my_file.writelines(cal.serialize_iter())
    print("Successfully updated world_cup_2026.ics")

if __name__ == "__main__":
    fetch_and_build_calendar()
