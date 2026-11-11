# Spec: AI Sign Language Translator

This is the agreed version, after the UI review. It replaces `requirements-original.md` where they differ.

## Purpose

An educational science fair project showing how AI can recognise American Sign Language (ASL) hand signs from a webcam photo. It runs on one laptop, offline.

## Supported signs (exactly 9)

| Sign | Meaning |
|---|---|
| A | Letter A |
| B | Letter B |
| C | Letter C |
| F | Letter F |
| O | Letter O |
| L | Letter L |
| V | Letter V (also "victory" / "peace") |
| Y | Letter Y |
| I LOVE YOU | "I love you" |

## Page layout (one page, see `ui-mockup.html`)

1. **Title** at the top: AI SIGN LANGUAGE TRANSLATOR, with a small yellow **(i)** info icon at the end.
2. **Statistics row** under the title, compact, dashboard style, all in one row. Each box shows two numbers, Yesterday | Today, with today larger:
   - Attempts
   - Correct (green)
   - Incorrect (red)
   - Unknown (amber)
   (There is no "Total users" and no participation number. They were removed in review.)
3. **Main row**:
   - **Left:** camera window with a CLICK TO START button inside it, and a **Capture** button below.
   - **Right:** one card that changes with the state (see "States" below).
4. **Learn the 9 signs**: a row of round chips, one per sign. In the real app each chip should show a picture of the hand sign.

## States of the right-hand card

1. **Before a try: "How to play"**
   1. Pick one of the 9 signs below.
   2. Click CLICK TO START to turn on the camera.
   3. Show the sign clearly to the camera.
   4. When you are ready, press Capture.
   5. Wait a moment for the AI's result.
2. **While analysing: workflow animation.** These steps light up one by one, following the real request:
   Capture → Send to the AI → Find the hand (MediaPipe) → Score each sign → Check confidence (above 70%).
   In the real app, a step should light up as the backend actually finishes it, or at least finish only when the response arrives.
3. **Result**, one of:
   - **Recognised:** "THE AI HAS SUCCESSFULLY RECOGNISED THE SIGN!", the sign, its meaning, and the confidence %.
   - **Not sure:** confidence below the threshold (start at 70%): "THE AI FAILED TO RECOGNISE THE SIGN." and ask to try again.
   - **No hand found:** MediaPipe found no hand: ask to try again, with a tip about light and distance.
   - **Not included:** the best match is a sign outside the 9: "SIGN NOT INCLUDED IN THIS PROJECT." and ask to try again.
   - Then, whenever the AI gave a sign (Recognised, Not sure or Not included): "Did the AI get it right?" **Yes / No**. **Try Again / Finish** stay hidden until Yes or No is pressed.
   - For No hand found: no Yes/No question; **Try Again / Finish** show straight away.

## Statistics rules

- **Attempts** goes up by 1 for every capture.
- **Correct** goes up when the visitor presses Yes.
- **Incorrect** goes up when the visitor presses No.
- **Unknown** goes up when the result is No hand found. (The visitor is not asked Yes/No in that case.) Not sure and Not included are asked Yes/No, so they count as Correct or Incorrect. (Changed on 8 Nov 2026 at the user's request; before that, Not sure and Not included counted as Unknown.)
- Statistics are saved per day, using the laptop's date. The page shows only yesterday and today; every day stays in `backend/stats.json`.
- Statistics must still be there after the page or the laptop is closed and opened again.

## Info popup (opened by the (i) icon)

A full-page popup with:

- **Two columns:** "Project Idea" (a 7-step timeline filling the whole column: how the project was made, from finding the idea to fine-tuning) and "How it is done" (the technical flow from `design.md`, as a flow diagram at the top, then short bullet points).
- **Footer:** "Who we are: Nikita · Class 9 - Sapphire, Sivani · Class 9 - Sapphire".
- A ✕ button to close it.

## Ideas for later (not required)

- Extra stats: accuracy %, average confidence, easiest and hardest sign, time per prediction, "no hand found" count.
- Speak the result aloud with the browser's speech feature.
- Automatic capture about once a second instead of the button.
