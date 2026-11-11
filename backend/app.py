"""AI Sign Language Translator: the local web server.

Run from the project root:
    uvicorn backend.app:app --reload --port 8000
Then open http://localhost:8000
"""

import io
import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from backend.signs import predict_photo
from backend.stats import count_answer, count_capture, read_all_days, read_stats, reset_stats

# The frontend folder sits next to the backend folder.
FRONTEND_FOLDER = Path(__file__).parent.parent / "frontend"

# Sample photos of each sign (A.jpg, B.jpg ... ILoveU.jpg). The page shows them when you hover over a sign.
PHOTOS_FOLDER = Path(__file__).parent.parent / "test_photos"

# The last hand crop is saved here, so we can check what the AI is looking at.
DEBUG_FOLDER = Path(__file__).parent / "debug"

# Settings for the AWS copy of the app. On the laptop none of them are set, so it works as before.
# RESET_PIN: if set, the statistics can only be reset with this PIN.
RESET_PIN = os.environ.get("RESET_PIN", "")
# SAVE_DEBUG_CROPS=no: do not keep visitors' hand pictures (used on AWS).
SAVE_DEBUG_CROPS = os.environ.get("SAVE_DEBUG_CROPS", "yes") != "no"
# SAVE_CAPTURES: where to keep the webcam photos. "folder" = captures/ on the laptop (the default),
# "s3" = the S3 bucket (used on AWS), "no" = do not keep them.
SAVE_CAPTURES = os.environ.get("SAVE_CAPTURES", "folder")
# APP_PLACE=aws: the page then says it runs on a cloud server, not on the laptop.
APP_PLACE = os.environ.get("APP_PLACE", "laptop")

# Load the photo-keeping code for the chosen place. Only AWS loads the S3 one, so the laptop does not need boto3.
if SAVE_CAPTURES == "s3":
    from backend import captures_s3 as captures
elif SAVE_CAPTURES == "no":
    captures = None
else:
    from backend import captures

app = FastAPI(title="AI Sign Language Translator")


# Tell the browser to always check for a newer copy of the page, so code changes show up straight away.
@app.middleware("http")
async def always_fresh(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache"
    return response


# Tells us the server is running.
@app.get("/health")
def health():
    return {"ok": True}


# Tells the page where this copy of the app runs: "laptop" or "aws".
@app.get("/where")
def where():
    return {"place": APP_PLACE}


# Turn the uploaded file into a picture. Stops with an error if it is not a picture.
def read_photo(photo_bytes):
    try:
        return Image.open(io.BytesIO(photo_bytes)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="The file is not a picture.")


# Save the hand crop to backend/debug/last_crop.jpg (for checking only).
def save_debug_crop(crop):
    DEBUG_FOLDER.mkdir(exist_ok=True)
    crop.save(DEBUG_FOLDER / "last_crop.jpg")


# Receive a photo from the web page and send back which sign it shows.
@app.post("/predict")
def predict(photo: UploadFile = File(...)):
    picture = read_photo(photo.file.read())
    answer, hand_picture = predict_photo(picture)
    if hand_picture is not None and SAVE_DEBUG_CROPS:
        save_debug_crop(hand_picture)
    if captures:
        captures.save_capture(picture, answer)
    count_capture(answer["status"])
    return answer


# Send the saved statistics to the web page.
@app.get("/stats")
def get_stats():
    return read_stats()


# What the page sends when the visitor presses Yes or No. Anything else is refused.
class Feedback(BaseModel):
    answer: Literal["yes", "no"]


# Save the visitor's Yes or No and send back the new statistics.
@app.post("/stats/answer")
def save_answer(feedback: Feedback):
    if captures:
        captures.sort_capture(feedback.answer)
    return count_answer(feedback.answer)


# Send every saved day's numbers, for the students' report.
@app.get("/stats/all")
def get_all_stats():
    return read_all_days()


# What the page sends to reset the statistics. The PIN is only needed when RESET_PIN is set.
class ResetRequest(BaseModel):
    pin: str = ""


# Set the statistics back to zero (the reset link in the info popup, or Ctrl+Alt+R).
@app.post("/stats/reset")
def reset(request: ResetRequest | None = None):
    given_pin = request.pin if request else ""
    if RESET_PIN and given_pin != RESET_PIN:
        raise HTTPException(status_code=403, detail="Wrong or missing reset PIN.")
    return reset_stats()


# Serve the sample sign photos at http://localhost:8000/test_photos/
PHOTOS_FOLDER.mkdir(exist_ok=True)
app.mount("/test_photos", StaticFiles(directory=PHOTOS_FOLDER), name="test_photos")

# Serve the web page (index.html, style.css, app.js) at http://localhost:8000/
# This must come last, so it does not hide the routes above.
app.mount("/", StaticFiles(directory=FRONTEND_FOLDER, html=True), name="frontend")
