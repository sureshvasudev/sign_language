"""AI Sign Language Translator: the local web server.

Run from the project root:
    uvicorn backend.app:app --reload --port 8000
Then open http://localhost:8000
"""

import io
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from backend.signs import predict_photo
from backend.stats import count_answer, count_capture, read_stats, reset_stats

# The frontend folder sits next to the backend folder.
FRONTEND_FOLDER = Path(__file__).parent.parent / "frontend"

# Sample photos of each sign (A.jpg, B.jpg ... ILoveU.jpg). The page shows them when you hover over a sign.
PHOTOS_FOLDER = Path(__file__).parent.parent / "test_photos"

# The last hand crop is saved here, so we can check what the AI is looking at.
DEBUG_FOLDER = Path(__file__).parent / "debug"

app = FastAPI(title="AI Sign Language Translator")


# Tells us the server is running.
@app.get("/health")
def health():
    return {"ok": True}


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
    if hand_picture is not None:
        save_debug_crop(hand_picture)
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
    return count_answer(feedback.answer)


# Set the statistics back to zero (the hidden Ctrl+Alt+R shortcut on the page).
@app.post("/stats/reset")
def reset():
    return reset_stats()


# Serve the sample sign photos at http://localhost:8000/test_photos/
PHOTOS_FOLDER.mkdir(exist_ok=True)
app.mount("/test_photos", StaticFiles(directory=PHOTOS_FOLDER), name="test_photos")

# Serve the web page (index.html, style.css, app.js) at http://localhost:8000/
# This must come last, so it does not hide the routes above.
app.mount("/", StaticFiles(directory=FRONTEND_FOLDER, html=True), name="frontend")
