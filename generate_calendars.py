import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ==========================================
# 1. CONFIGURATION TABLE
# Add or modify teams here without touching the core logic.
# ==========================================
TEAM_CONFIGS = [
    {
        "name": "Boston Celtics",
        "sport": "basketball",
        "league": "nba",
        "team_id": "bos",
        "emoji": "🏀",
        "duration_hours": 2.5,
        "output_file": "celtics_schedule.ics",
        "is_soccer": False
    },
    {
        "name": "Chicago Bears",
        "sport": "football",
        "league": "nfl",
        "team_id": "chi",
        "emoji": "🏈",
        "duration_hours": 3.25,
        "output_file": "bears_schedule.ics",
        "is_soccer": False
    },
    {
        "name": "New England Patriots",
        "sport": "football",
        "league": "nfl",
        "team_id": "ne",
        "emoji": "🏈",
        "duration_hours": 3.25,
        "output_file": "patriots_schedule.ics",
        "is_soccer": False
    },
    {
        "name": "Tottenham Hotspur",
        "sport": "soccer",
        "league": "all",
        "team_id": "367",
        "emoji": "⚽",
        "duration_hours": 2.0,
        "output_file": "spurs_schedule.ics",
        "is_soccer": True
    },
    {
        "name": "Burnley FC",
        "sport": "soccer",
        "league": "all",
        "team_id": "379",
        "emoji": "⚽",
        "duration_hours": 2.0,
        "output_file": "burnley_schedule.ics",
        "is_soccer": True
    },
    {
        "name": "D.C. United",
        "sport": "soccer",
        "league": "all",
        "team_id": "193",
        "emoji": "⚽",
        "duration_hours": 2.0,
        "output_file": "dc_united_schedule.ics",
        "is_soccer": True
    }
]

# ==========================================
# 2. FORMATTING ENGINE
# Customize the look & feel of calendar entries in one place.
# ==========================================
def format_event_title(item, target_team_id, default_emoji):
    """
    Builds the event title string with optional Win/Loss badges and final scores.
    """
    raw_name = item.get("name", "Unknown Matchup")
    competitions = item.get("competitions", [{}])[0]
    competitors = competitions.get("competitors", [])
    status = item.get("status", {}).get("type", {})
    is_completed = status.get("completed", False)

    prefix = f"{default_emoji} "
    suffix = ""

    # Calculate score & win/loss outcome if the game is finished
    if is_completed and competitors:
        target_comp = None
        opp_comp = None

        for comp in competitors:
            c_id = str(comp.get("id", ""))
            t_id = str(comp.get("team", {}).get("id", ""))
            if c_id == str(target_team_id) or t_id == str(target_team_id):
                target_comp = comp
            else:
                opp_comp = comp

        if target_comp and opp_comp:
            target_score = target_comp.get("score", {}).get("displayValue", "0")
            opp_score = opp_comp.get("score", {}).get("displayValue", "0")

            target_won = target_comp.get("winner", False)
            opp_won = opp_comp.get("winner", False)

            if target_won:
                prefix = "✅ " + prefix
            elif opp_won:
                prefix = "❌ " + prefix
            else:
                prefix = "🤝 " + prefix  # Draw / Tie

            suffix = f" ({target_score}-{opp_score})"

    return f"{prefix}{raw_name}{suffix}"

# ==========================================
# 3. DATA FETCHING LAYER
# ==========================================
def fetch_team_schedule(config):
    sport = config["sport"]
    league = config["league"]
    team_id = config["team_id"]
    base_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/schedule?limit=200"

    urls = [base_url]
    # Soccer requires querying both completed and upcoming fixture endpoints
    if config.get("is_soccer"):
        urls.append(f"{base_url}&fixture=true")

    raw_events = []
    seen_ids = set()

    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for event in data.get("events", []):
                    event_id = event.get("id")
                    if event_id not in seen_ids:
                        seen_ids.add(event_id)
                        raw_events.append(event)
        except Exception as e:
            print(f"Error requesting {url}: {e}")

    return raw_events

# ==========================================
# 4. CALENDAR GENERATOR
# ==========================================
def generate_ics_calendar(config):
    events_data = fetch_team_schedule(config)
    cal = Calendar()

    for item in events_data:
        time_str = item.get("date")
        if not time_str:
            continue

        try:
            clean_time = time_str.replace('Z', '')
            utc_time = datetime.fromisoformat(clean_time).replace(tzinfo=ZoneInfo("UTC"))
            eastern_time = utc_time.astimezone(ZoneInfo("America/New_York"))

            event = Event()
            event.name = format_event_title(item, config["team_id"], config["emoji"])
            event.begin = eastern_time
            event.end = eastern_time + timedelta(hours=config["duration_hours"])

            competitions = item.get("competitions", [{}])
            
            # Extract Location
            if competitions and "venue" in competitions[0]:
                event.location = competitions[0]["venue"].get("fullName", "TBD Arena")

            # Extract Broadcast Info
            tv_networks = []
            if competitions:
                broadcasts = competitions[0].get("broadcasts", [])
                for broadcast in broadcasts:
                    # Target the schedule endpoint format
                    media = broadcast.get("media", {})
                    if "shortName" in media:
                        tv_networks.append(media["shortName"])
                    
                    # Fallback for the scoreboard endpoint format
                    names = broadcast.get("names", [])
                    if isinstance(names, list):
                        tv_networks.extend(names)
            
            # Deduplicate networks and format the string
            tv_networks = list(set(tv_networks))
            if tv_networks:
                desc_text = f"TV/Streaming: {', '.join(tv_networks)}"
            else:
                desc_text = "TV/Streaming: TBD"

            # Add F1 Podium for Completed Races
            status = item.get("status", {}).get("type", {})
            is_completed = status.get("completed", False)

            if config.get("sport") == "racing" and is_completed and competitions:
                competitors = competitions[0].get("competitors", [])
                
                # Filter for top 3 and sort by order
                podium = [c for c in competitors if c.get("order", 999) <= 3]
                podium.sort(key=lambda x: x.get("order", 999))
                
                if podium:
                    desc_text += "\n\nPodium:"
                    for comp in podium:
                        place = comp.get("order")
                        driver = comp.get("athlete", {}).get("displayName", "Unknown")
                        desc_text += f"\n{place}. {driver}"

            event.description = desc_text
            cal.events.add(event)
        except Exception as e:
            print(f"Skipping event due to parsing error: {e}")

    with open(config["output_file"], 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print(f"Updated: {config['output_file']} ({len(cal.events)} events)")

if __name__ == "__main__":
    for config in TEAM_CONFIGS:
        generate_ics_calendar(config)
