"""Keeps the visitor statistics for each day in a small file, so they are still there after the laptop is closed."""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

# The numbers are saved here, next to this file, with one entry per day.
STATS_FILE = Path(__file__).parent / "stats.json"

# Each reset moves the old numbers into this folder, in a file named with the date and time.
BACKUP_FOLDER = Path(__file__).parent / "stats-backups"

# The visitor is not asked Yes or No after these results, so they count as Unknown.
UNKNOWN_RESULTS = ("not_sure", "no_hand", "not_included")


# The numbers for a day with no captures yet.
def empty_day():
    return {"attempts": 0, "correct": 0, "incorrect": 0, "unknown": 0}


# Read every saved day. The very first time there is no file yet, so there are no days.
def read_all_days():
    if not STATS_FILE.exists():
        return {}
    return json.loads(STATS_FILE.read_text())


# Save every day. Writing a new file and then swapping it in keeps the old numbers safe if the laptop stops halfway.
def save_all_days(days):
    new_file = STATS_FILE.with_suffix(".tmp")
    new_file.write_text(json.dumps(days, indent=2))
    new_file.replace(STATS_FILE)


# Find today's numbers, adding a new empty day if this is the first capture today.
def todays_numbers(days):
    return days.setdefault(date.today().isoformat(), empty_day())


# Return today's and yesterday's numbers for the web page.
def read_stats():
    days = read_all_days()
    today = date.today()
    yesterday = today - timedelta(days=1)
    return {
        "today": days.get(today.isoformat(), empty_day()),
        "yesterday": days.get(yesterday.isoformat(), empty_day()),
    }


# Count one capture today: Attempts goes up, and Unknown too if the AI gave no sign to check.
def count_capture(status):
    days = read_all_days()
    today = todays_numbers(days)
    today["attempts"] += 1
    if status in UNKNOWN_RESULTS:
        today["unknown"] += 1
    save_all_days(days)


# Count the visitor's answer to "Did the AI get it right?" and return the new numbers.
def count_answer(answer):
    days = read_all_days()
    today = todays_numbers(days)
    if answer == "yes":
        today["correct"] += 1
    else:
        today["incorrect"] += 1
    save_all_days(days)
    return read_stats()


# Start again from zero, keeping the old numbers in a dated backup file, for example stats-2026-11-08_14-30-05.json.
def reset_stats():
    if STATS_FILE.exists():
        BACKUP_FOLDER.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        STATS_FILE.replace(BACKUP_FOLDER / f"stats-{stamp}.json")
    return read_stats()
