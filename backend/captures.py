"""Keeps every webcam photo on the laptop, in one folder per day, each with success, failure and unknown inside.

For example: captures/20261110/success/2026-11-10_10-15-03_V_93.jpg

success = the AI named a sign and the visitor pressed Yes
failure = the AI named a sign and the visitor pressed No
unknown = the AI found no hand, or the visitor never pressed Yes or No
Any result with a sign (even "not sure" or "not included") waits for Yes or No.
"""

from datetime import datetime
from pathlib import Path

# The captures folder sits in the project folder, next to backend and frontend.
CAPTURES_FOLDER = Path(__file__).parent.parent / "captures"

# The last photo with a named sign, waiting in "unknown" for the visitor's Yes or No. None if there is none.
waiting_photo = None


# Today's folder name, for example 20261110 (year, month, day).
def day_folder():
    return datetime.now().strftime("%Y%m%d")


# Make a file name from the time and the AI's answer, for example 2026-11-10_10-15-03_V_93.jpg
# or 2026-11-10_10-16-40_not-sure_A_55.jpg.
def photo_name(answer):
    parts = [datetime.now().strftime("%Y-%m-%d_%H-%M-%S")]
    if answer["status"] != "ok":
        parts.append(answer["status"].replace("_", "-"))
    if answer.get("sign"):
        parts.append(answer["sign"].replace(" ", "-"))
    if answer.get("confidence") is not None:
        parts.append(str(round(answer["confidence"] * 100)))
    return "_".join(parts) + ".jpg"


# Save the photo in today's "unknown" folder. If the AI gave a sign, remember it so Yes or No can move it later.
def save_capture(photo, answer):
    global waiting_photo
    folder = CAPTURES_FOLDER / day_folder() / "unknown"
    folder.mkdir(parents=True, exist_ok=True)
    photo_path = folder / photo_name(answer)
    photo.save(photo_path, quality=90)
    if answer.get("sign"):
        waiting_photo = photo_path
    else:
        waiting_photo = None


# The visitor pressed Yes or No: move the waiting photo into "success" or "failure" of the same day.
def sort_capture(answer):
    global waiting_photo
    if waiting_photo is None or not waiting_photo.exists():
        return
    day = waiting_photo.parent.parent
    folder = day / ("success" if answer == "yes" else "failure")
    folder.mkdir(parents=True, exist_ok=True)
    waiting_photo.replace(folder / waiting_photo.name)
    waiting_photo = None
