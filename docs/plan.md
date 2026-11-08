# Build plan

Work through these in order. Finish and test each one before starting the next.

## Milestone 1: Backend skeleton
- `backend/app.py` with FastAPI.
- `GET /health` returns `{"ok": true}`.
- Serves `frontend/` as static files at `/`.
- **Test:** run uvicorn, open http://localhost:8000/health.

## Milestone 2: Static front end
- Turn `docs/ui-mockup.html` into `frontend/index.html`, `style.css` and `app.js`.
- Download the font into `frontend/fonts/` so it works offline (or use a system font).
- Keep the mockup's look. Use placeholder numbers for now.
- **Test:** page looks like `docs/ui-mockup-start.png`, and the (i) popup opens and closes.

## Milestone 3: Webcam and capture
- CLICK TO START turns on the webcam (`navigator.mediaDevices.getUserMedia`) inside the camera box.
- Capture takes a JPEG from a hidden canvas.
- **Test:** the captured photo shows up briefly as a thumbnail (debug only).

## Milestone 4: Hand detection
- `POST /predict` accepts the image.
- MediaPipe Hands finds the hand and crops to it with a margin.
- If no hand is found, return `{"status": "no_hand"}`.
- **Test:** send a photo with and without a hand.

## Milestone 5: Model
- Confirm the model id with the user (see CLAUDE.md open questions).
- Load the model once at startup, not on every request.
- Return `{"status": "ok", "sign": "B", "confidence": 0.97}`, or `"not_sure"` below the threshold, or `"not_included"` if the best label is outside the 9.
- Handle I LOVE YOU (model label, or the landmark rule).
- **Test:** a small script that runs a few saved photos through `/predict` and prints results.

## Milestone 6: Connect front end to backend
- Capture → POST to `/predict` → workflow animation → result card.
- Show each result state from `spec.md`.
- **Test:** try all 9 signs and one sign that is not included.

## Milestone 7: Statistics
- Backend stores stats per day in `backend/stats.json`. The stats row shows yesterday and today.
- `GET /stats` and `POST /stats/answer` (Yes / No). `/predict` counts Attempts and Unknown itself.
- Stats row reads from the backend.
- **Test:** close and reopen the browser; numbers stay.

## Milestone 8: Polish for the fair
- Pictures for the 9 sign chips.
- Fill in the two flow diagrams in the info popup.
- Measure speed and accuracy with real people, and write the numbers down for the report.
- A "reset stats" option hidden from visitors (for example a keyboard shortcut).
