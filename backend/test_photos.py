"""Run a folder of saved photos through the AI and print the results.

Name each photo after the sign it shows, then an underscore, for example:
    A.jpg   A_1.jpg   B_nikita.jpg   V_2.png   ILY_1.jpg or ILoveU.jpg   (= I LOVE YOU)

Run from the project root:
    python -m backend.test_photos test_photos
"""

import sys
import time
from pathlib import Path

from PIL import Image

from backend.signs import predict_photo

PHOTO_TYPES = {".jpg", ".jpeg", ".png"}


# Work out the expected sign from the file name, e.g. "B_1.jpg" -> "B", "ILY_1.jpg" or "ILoveU.jpg" -> "I LOVE YOU".
def expected_sign(photo_path):
    first_part = photo_path.stem.split("_")[0].upper()
    if first_part in ("ILY", "ILOVEU"):
        return "I LOVE YOU"
    return first_part


# Turn the AI's answer into one short line of text.
def describe(answer):
    if answer["status"] == "no_hand":
        return "no hand found"
    if answer["confidence"] is None:
        return f'{answer["sign"]} ({answer["status"]}, by hand rule)'
    return f'{answer["sign"]} ({answer["status"]}, {answer["confidence"]:.0%})'


# Run every photo in the folder through the AI and print a table plus a score.
def main(folder):
    photos = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in PHOTO_TYPES)
    if not photos:
        print(f"No photos found in {folder}")
        return

    correct = 0
    print(f'{"Photo":28} {"Expected":12} {"AI answer":36} {"Time":>7}')
    for photo_path in photos:
        photo = Image.open(photo_path).convert("RGB")
        start = time.perf_counter()
        answer, _ = predict_photo(photo)
        seconds = time.perf_counter() - start

        expected = expected_sign(photo_path)
        is_right = answer["status"] == "ok" and answer["sign"] == expected
        correct += is_right
        mark = "OK " if is_right else "-- "
        print(f'{mark}{photo_path.name:25} {expected:12} {describe(answer):36} {seconds * 1000:5.0f} ms')

    print(f"\nCorrect: {correct} out of {len(photos)} ({correct / len(photos):.0%})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "test_photos")
