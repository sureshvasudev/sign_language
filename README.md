# AI Sign Language Translator

Science fair project by Nikita and Sivani (Class 9 - Sapphire). A web page that recognises 9 ASL hand signs from a webcam photo, running offline on one laptop.

## Start in VS Code

1. Copy this folder somewhere on your laptop and open it in VS Code (File → Open Folder).
2. Install Python 3.10 or newer, and the Claude Code extension for VS Code.
3. Open Claude Code in VS Code. It reads `CLAUDE.md` automatically, so it already knows the project.
4. Give it a first message, for example:

   > Read CLAUDE.md and docs/. Then start Milestone 1 from docs/plan.md.

5. After each milestone, test it the way Claude describes, then say "next milestone".

## What's in here

| Path | What it is |
|---|---|
| `CLAUDE.md` | Instructions for Claude Code: the project, the rules and the open questions |
| `docs/spec.md` | The agreed requirements (the source of truth) |
| `docs/design.md` | The technical flow: browser → FastAPI → MediaPipe → SigLIP2 model |
| `docs/plan.md` | Build order, in 8 milestones |
| `docs/ui-mockup.html` | The agreed page design; open it in a browser |
| `docs/ui-mockup-*.png` | Screenshots of each state |
| `docs/requirements-original.md` | The first requirements, kept for history |
| `backend/requirements.txt` | Python libraries |
| `backend/`, `frontend/` | Empty for now. Claude Code fills these in |

## Run it the easy way (Windows)

Double-click `start.bat` in the project folder, or open a command prompt and run:

```bat
cd path\to\sign_language
start.bat
```

The script:

1. The first time only, creates the Python environment (`.venv`) and installs the libraries. This needs internet and can take several minutes.
2. Starts the server.
3. Waits until the server is ready, then opens http://localhost:8000 in the default browser.

Keep the black window open while using the app. Close it, or press Ctrl+C, to stop.

## Reset the statistics to 0

Double-click `reset.bat`. It shows the current numbers, then asks you to type `Y` to confirm. The old numbers are not deleted: each reset saves them in its own dated file in `backend\stats-backups\`, for example `stats-2026-11-08_14-30-05.json`. Open that file in Notepad to see what was there before. If the app is open, refresh the page to see the zeros. (In the app itself, Ctrl+Alt+R does the same.)

## Run it by hand

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload --port 8000
```

Then open http://localhost:8000 in Chrome or Edge.
