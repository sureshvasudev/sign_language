"""Finding the hand in a photo, using MediaPipe from Google.

MediaPipe finds 21 points on the hand (the "landmarks": wrist, knuckles and
finger tips). We draw a box around those points, add a margin, and cut out
(crop) that part of the photo. The crop removes most of the background, which
makes it easier for the sign model to see the hand.

The same 21 points are used to spot I LOVE YOU, which the sign model does not know.

Point numbers (from the MediaPipe documentation):
    0 = wrist
    1-4   = thumb   (4 is the tip)
    5-8   = index   (5 is the knuckle, 6 the middle joint, 8 the tip)
    9-12  = middle  (10 middle joint, 12 tip)
    13-16 = ring    (14 middle joint, 16 tip)
    17-20 = pinky   (18 middle joint, 20 tip)
"""

import math
from pathlib import Path

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from PIL import Image

# The MediaPipe hand model file, downloaded once into backend/models/.
HAND_MODEL_FILE = Path(__file__).parent / "models" / "hand_landmarker.task"

# Extra space around the hand, as a fraction of the hand's size (0.25 = 25%).
CROP_MARGIN = 0.25

# For I LOVE YOU, the thumb tip must be at least this far from the index knuckle,
# measured as a fraction of the palm length (wrist to middle knuckle).
THUMB_OUT_DISTANCE = 0.5


# Load the MediaPipe hand finder once, when the server starts.
def load_hand_finder():
    options = vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(HAND_MODEL_FILE)),
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(options)


hand_finder = load_hand_finder()


# Find the hand in a photo. Returns its 21 points as (x, y) pixels, or None if there is no hand.
def find_hand_points(photo):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(photo))
    result = hand_finder.detect(mp_image)
    if not result.hand_landmarks:
        return None
    # MediaPipe gives positions from 0 to 1, so multiply by the photo size to get pixels.
    return [(point.x * photo.width, point.y * photo.height) for point in result.hand_landmarks[0]]


# Work out a square box around the hand (left, top, right, bottom) in pixels.
def hand_box(points, photo_width, photo_height):
    xs = [x for x, y in points]
    ys = [y for x, y in points]

    # Make the box square (the sign model expects a square picture) and add the margin.
    centre_x = (min(xs) + max(xs)) / 2
    centre_y = (min(ys) + max(ys)) / 2
    hand_size = max(max(xs) - min(xs), max(ys) - min(ys))
    half = hand_size * (1 + 2 * CROP_MARGIN) / 2

    # Keep the box inside the photo.
    left = max(0, int(centre_x - half))
    top = max(0, int(centre_y - half))
    right = min(photo_width, int(centre_x + half))
    bottom = min(photo_height, int(centre_y + half))
    return left, top, right, bottom


# Find the hand and cut it out of the photo. Returns (crop, points), or (None, None) if no hand.
def crop_to_hand(photo: Image.Image):
    points = find_hand_points(photo)
    if points is None:
        return None, None
    box = hand_box(points, photo.width, photo.height)
    return photo.crop(box), points


# Distance in pixels between two points.
def distance(point_a, point_b):
    return math.dist(point_a, point_b)


# A finger is "up" (straight) if its tip is further from the wrist than its middle joint.
def finger_is_up(points, tip, middle_joint):
    wrist = points[0]
    return distance(points[tip], wrist) > distance(points[middle_joint], wrist)


# The thumb is "out" if its tip is far from the index knuckle.
def thumb_is_out(points):
    palm_length = distance(points[0], points[9])
    return distance(points[4], points[5]) > THUMB_OUT_DISTANCE * palm_length


# I LOVE YOU: thumb, index and pinky up; middle and ring down.
def is_i_love_you(points):
    return (
        thumb_is_out(points)
        and finger_is_up(points, tip=8, middle_joint=6)        # index up
        and not finger_is_up(points, tip=12, middle_joint=10)  # middle down
        and not finger_is_up(points, tip=16, middle_joint=14)  # ring down
        and finger_is_up(points, tip=20, middle_joint=18)      # pinky up
    )
