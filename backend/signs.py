"""Naming the sign in a photo.

Steps, in order:
  1. MediaPipe finds the hand and crops the photo to it (see hands.py).
  2. If the hand points match I LOVE YOU, we stop there (the model does not know it).
  3. Otherwise the SigLIP2 model scores the crop against all 26 letters and picks the best.
  4. Below 70% confidence we say "not sure". A letter outside our 9 is "not included".
"""

import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

from backend.hands import crop_to_hand, is_i_love_you

# The Hugging Face model: SigLIP2, fine-tuned on the sign language alphabet A to Z.
MODEL_ID = "prithivMLmods/Alphabet-Sign-Language-Detection"

# Below this confidence the AI says it is not sure (0.70 = 70%).
CONFIDENCE_THRESHOLD = 0.70

# The 9 signs in this project, and what each one means.
SIGNS = {
    "A": "Letter A",
    "B": "Letter B",
    "C": "Letter C",
    "F": "Letter F",
    "O": "Letter O",
    "L": "Letter L",
    "V": 'Letter V (also "victory" / "peace")',
    "Y": "Letter Y",
    "I LOVE YOU": '"I love you"',
}


# Load the model from the laptop's Hugging Face cache, or download it the first time.
def load_model():
    try:
        processor = AutoImageProcessor.from_pretrained(MODEL_ID, local_files_only=True)
        model = AutoModelForImageClassification.from_pretrained(MODEL_ID, local_files_only=True)
    except OSError:
        print("Model not on this laptop yet. Downloading it once (about 372 MB)...")
        processor = AutoImageProcessor.from_pretrained(MODEL_ID)
        model = AutoModelForImageClassification.from_pretrained(MODEL_ID)
    model.eval()
    return processor, model


# Loaded once when the server starts, not on every photo.
processor, model = load_model()


# Score the hand picture against every letter. Returns a list of (letter, score), best first.
def score_signs(hand_picture):
    inputs = processor(images=hand_picture, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    # Softmax turns the raw numbers into scores between 0 and 1 that add up to 1.
    scores = torch.softmax(logits, dim=1)[0].tolist()
    labels = [model.config.id2label[i] for i in range(len(scores))]
    return sorted(zip(labels, scores), key=lambda pair: pair[1], reverse=True)


# The whole job: photo in, answer out (as a dictionary the web page can read).
def predict_photo(photo):
    hand_picture, points = crop_to_hand(photo)
    if hand_picture is None:
        return {"status": "no_hand"}, None

    # I LOVE YOU is checked with the hand points, before the model runs.
    if is_i_love_you(points):
        answer = {
            "status": "ok",
            "sign": "I LOVE YOU",
            "meaning": SIGNS["I LOVE YOU"],
            "confidence": None,
            "method": "hand_rule",
        }
        return answer, hand_picture

    ranking = score_signs(hand_picture)
    best_letter, best_score = ranking[0]
    top3 = [{"sign": letter, "score": round(score, 3)} for letter, score in ranking[:3]]

    if best_score < CONFIDENCE_THRESHOLD:
        status = "not_sure"
    elif best_letter not in SIGNS:
        status = "not_included"
    else:
        status = "ok"

    answer = {
        "status": status,
        "sign": best_letter,
        "meaning": SIGNS.get(best_letter, ""),
        "confidence": round(best_score, 3),
        "method": "model",
        "top3": top3,
    }
    return answer, hand_picture
