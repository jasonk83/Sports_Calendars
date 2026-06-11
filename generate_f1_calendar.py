import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def fetch_and_build_f1_calendar():
    # Using the Jolpica API (the 2025/2026 community replacement for Ergast)
    API_URL = "https://api.jolpi.ca/ergast/f1/current.json"
    
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("Error: Failed to fetch F1 data.")
        return

    data = response.json()
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    cal = Calendar()

    for race in races:
        country = race.get("Circuit", {}).get("Location", {}).get("country", "Unknown")
        location = race.get("Circuit", {}).get("circuitName", "TBD Circuit")

        # Map of all possible sub-sessions an F1 weekend could have. 
        # The key is the API's JSON label, the value is what you will see on your calendar.
        session_keys = {
            "FirstPractice": "Practice 1",
            "SecondPractice": "Practice 2",
            "ThirdPractice": "Practice 3",
            "Qualifying": "Qualifying",
            "SprintShootout": "Sprint Qualifying", # Ergast/Jolpica's historical key
            "SprintQualifying": "Sprint Qualifying", # Fallback key
            "Sprint": "Sprint Race"
        }

        # 1. Loop through and add Practice, Quali, and Sprints (if they exist for this race)
        for json_key, session_title in session_keys.items():
            if json_key in race:
                session_data = race[json_key]
                add_event(
                    cal, 
                    name=f"🏎️ F1 {country}: {session_title}",
                    date_str=session_data.get("date"),
                    time_str=session_data.get("time"),
                    location=location,
                    duration_hours=1 # Practice and Quali usually get a 1-hour block
                )

        # 2. Add the Main Sunday Race (which sits at the root level of the race object)
        add_event(
            cal,
            name=f"🏁 F1 {country}: MAIN RACE",
            date_str=race.get("date"),
            time_str=race.get("time"),
            location=location,
            duration_hours=2 # Main races usually get a 2-hour block
        )

    # Export the calendar file
    with open('f1_2026.ics', 'w', encoding='utf-8') as my_file:
        my_file.writelines(cal.serialize_iter())
    print("Successfully updated f1_2026.ics")

def add_event(cal, name, date_str, time_str, location, duration_hours):
    if not date_str or not time_str:
        return
        
    event = Event()
    event.name = name
    event.location = location

    try:
        # F1 API times always come in UTC format like '15:00:00Z'
        clean_time = time_str.replace('Z', '')
        
        # 1. Parse the time
        naive_time = datetime.strptime(f"{date_str} {clean_time}", "%Y-%m-%d %H:%M:%S")
        
        # 2. Assign UTC timezone explicitly
        utc_time = naive_time.replace(tzinfo=ZoneInfo("UTC"))
        
        # 3. Convert directly to Eastern Time
        eastern_time = utc_time.astimezone(ZoneInfo("America/New_York"))
        
        event.begin = eastern_time
        event.end = eastern_time + timedelta(hours=duration_hours)
        cal.events.add(event)
    except Exception as e:
        print(f"Skipping {name} due to time parsing error: {e}")

if __name__ == "__main__":
    fetch_and_build_f1_calendar()
