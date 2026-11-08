With Option A, everything runs on your own PC, and neither the photos nor the model calls need to leave it after the one-time setup.

Browser page (webcam)
      │  1. You show a sign and click Capture
      ▼
Local API (Python, FastAPI)  POST /predict
      │  2. Receives the image
      ▼
MediaPipe
      │  3. Finds the hand and crops to it
      ▼
SigLIP2 ASL model
      │  4. Scores each possible sign
      ▼
Local API
      │  5. Returns JSON: {"letter": "B", "confidence": 0.97}
      ▼
Browser page
         6. Shows the letter and confidence

One-time setup

Install Python and the required libraries: FastAPI, PyTorch, Transformers and MediaPipe.
Download the model from Hugging Face. It’s cached locally, so the app can then run offline.
Start the API on your PC, for example at http://localhost:8000.

Each time you capture a sign

Capture: the page takes a photo from the webcam and sends it to /predict.
Find the hand: MediaPipe crops the image to your hand, which removes most of the background. If it finds no hand, the API returns “no hand detected” and the page asks you to try again.
Classify: the model scores the cropped image against each sign it knows and picks the highest.
Check confidence: if the score is below a set level, such as 70%, the page shows “not sure, try again” rather than a likely wrong letter. We’d tune that level through testing.
Display: the page shows the result. It could also add each letter to a line of text, so you can spell out words.

Speed: I’d expect about a second or less per photo on a typical CPU, but I haven’t measured this, and it will depend on your PC.

Optional upgrade: instead of clicking Capture, the page could send a frame automatically about once a second for near-live recognition. I’d start with the button because it’s simpler to test.

If this flow works for you, tell me to go ahead and I’ll build it.