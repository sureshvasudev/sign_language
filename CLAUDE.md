# AI Sign Language Translator: instructions for Claude

You are helping two Class 9 students (Nikita and Sivani, Class 9 - Sapphire) build a science fair project, together with a parent who is guiding them. Keep the code simple enough for a 9th grader to read and explain to a judge.

## What we are building

A single web page where a visitor shows one of 9 static ASL hand signs to the laptop webcam, clicks Capture, and the AI says which sign it is, what it means, and how confident it is. Everything runs offline on one laptop.

Read these before writing code:

- `docs/spec.md`: the agreed requirements. This is the source of truth.
- `docs/design.md`: the agreed technical flow (browser → local FastAPI → MediaPipe → SigLIP2 model → JSON → browser).
- `docs/ui-mockup.html` and the `docs/ui-mockup-*.png` screenshots: the agreed look. Match it.
- `docs/plan.md`: the build order. Work one milestone at a time.
- `docs/requirements-original.md`: the first requirements, kept for history. Where it differs from `spec.md`, `spec.md` wins.

## Project layout

```
backend/    Python FastAPI app (app.py), model loading, /predict endpoint
frontend/   index.html, style.css, app.js (plain HTML/CSS/JS, no framework, no build step)
docs/       spec, design, plan, mockup
```

The backend serves the frontend as static files, so the app opens at http://localhost:8000.

## Rules

- **Keep it simple.** Plain HTML, CSS and JavaScript on the front end. No React, no bundler, no npm. One small Python backend.
- **Offline after setup.** No CDNs at runtime. Download any fonts or libraries into `frontend/` once. The model is cached locally by Hugging Face after the first download.
- **Only 9 signs.** A, B, C, F, O, L, V, Y and I LOVE YOU. Any other prediction counts as "sign not included".
- **Explainable code.** Short functions, clear names, and a one-line comment above each function saying what it does in plain English. No clever tricks.
- **Colours.** Pink, yellow and white, as in the mockup. Reuse the CSS variables from `docs/ui-mockup.html`.
- **One milestone at a time.** After each milestone, tell the user how to run and test it, and wait for them to confirm before moving on.
- **Do not invent results.** If something is unmeasured (speed, accuracy), say so. The students will measure it for their report.
- **Ask before** adding a new dependency, changing the agreed UI layout, or changing the confidence threshold.

## Commands

```bash
# one-time setup (from the project root)
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt

# run
uvicorn backend.app:app --reload --port 8000
# then open http://localhost:8000
```

## Known open questions (check with the user)

1. **Which Hugging Face model.** design.md says a SigLIP2 ASL model. Confirm the exact model id before coding, and check its labels list.
2. **I LOVE YOU.** Most ASL alphabet models only know the letters A to Z, so they cannot output "I LOVE YOU". Check the chosen model's labels. If it is missing, suggest the simplest fix: a rule on MediaPipe hand landmarks (thumb, index and pinky up; middle and ring down), checked before the model runs.
3. **Where statistics are stored.** spec.md says they must survive closing the page. Default plan: a small JSON or SQLite file written by the backend.
