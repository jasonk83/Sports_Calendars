# 🏆 Sports Calendar Automations

This repository uses Python and GitHub Actions to automatically generate and maintain `.ics` calendar files for various sports leagues and teams[cite: 1]. These calendar feeds can be imported directly into Google Calendar, Apple Calendar, or Outlook to provide live, dynamically updating schedules.

## ⚙️ How It Works

The Python scripts query reliable data sources (such as the ESPN API and the Jolpica F1 API) to retrieve the latest match fixtures and start times[cite: 1]. They process this data, perform timezone conversions to US Eastern Time, and build standards-compliant iCalendar (`.ics`) files. 

GitHub Actions workflows are scheduled using cron jobs to run these scripts automatically at regular intervals, ensuring the calendars are always up-to-date with flexed times, added cup fixtures, and advancing tournament stages[cite: 1].

## 📅 Included Calendars

The following scripts and their corresponding output calendars are managed in this repository[cite: 1]:

*   **⚽ Soccer:**
    *   `generate_epl.py`: Generates `spurs_schedule.ics` (Tottenham Hotspur) and `burnley_schedule.ics` (Burnley FC) across all active competitions[cite: 1].
    *   `generate_dc_united.py`: Generates `dc_united_schedule.ics` (D.C. United) for MLS and tournament play[cite: 1].
    *   `generate_calendar.py`: Generates `world_cup_2026.ics` (FIFA World Cup 2026)[cite: 1].
*   **🏈 Football (NFL):**
    *   `generate_nfl.py`: Generates `bears_schedule.ics` (Chicago Bears) and `patriots_schedule.ics` (New England Patriots)[cite: 1].
*   **🏀 Basketball (NBA):**
    *   `generate_nba.py`: Generates `celtics_schedule.ics` (Boston Celtics)[cite: 1].
*   **🏎️ Racing:**
    *   `generate_f1_calendar.py`: Generates `f1_2026.ics` (Formula 1 Practice, Qualifying, Sprints, and Main Races)[cite: 1].

## 🤖 Automation Workflows

The automation schedules are controlled by YAML files located in the `.github/workflows/` directory[cite: 1]:

*   **`update_schedule.yml`:** Runs daily to track rapidly advancing tournament brackets[cite: 1].
*   **`72_hour_teams.yml`:** Runs every 3 days to fetch the latest club fixtures across the NBA, NFL, MLS, and English football leagues[cite: 1].
*   **`f1_schedule.yml`:** Runs weekly to fetch the upcoming race weekend timetable[cite: 1].

## 🔗 Subscribing to a Calendar

To add one of these auto-updating schedules to your personal calendar:
1. Click on the desired `.ics` file in this repository (e.g., `celtics_schedule.ics`)[cite: 1].
2. Click the **Raw** button in the top right corner.
3. Copy the URL from your browser's address bar.
4. In Google Calendar, go to **Settings > Add calendar > From URL** and paste the link.
