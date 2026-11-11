"""On the AWS copy: keeps every webcam photo in the S3 bucket, in one folder per day with success/, failure/
and unknown/ inside, for example 20261110/success/2026-11-10_10-15-03_V_93.jpg

It sorts photos the same way as captures.py does on the laptop. The uploads happen in the background,
one at a time and in order, so the web page never waits for them.
"""

import io
import os
import queue
import threading

import boto3

from backend.captures import day_folder, photo_name

# The bucket's name. deploy/setup.sh saves it on the server; CloudFormation creates the bucket.
BUCKET = os.environ.get("CAPTURES_BUCKET", "")

# Talks to Amazon S3. The server's IAM role gives it permission to use this one bucket.
s3 = boto3.client("s3")

# The to-do list for the background helper: each job is (function, its inputs).
jobs = queue.Queue()

# The last photo where the AI gave a sign, waiting in unknown/ for the visitor's Yes or No: (day, name), or None.
waiting_photo = None


# Upload one photo into a day's folder, for example 20261110/unknown/.
def upload(photo_bytes, day, folder, name):
    s3.put_object(Bucket=BUCKET, Key=f"{day}/{folder}/{name}", Body=photo_bytes, ContentType="image/jpeg")


# Move a photo from the day's unknown/ to its success/ or failure/. S3 has no "move", so copy it, then delete the old one.
def move(day, name, folder):
    old_key = f"{day}/unknown/{name}"
    s3.copy_object(Bucket=BUCKET, Key=f"{day}/{folder}/{name}", CopySource={"Bucket": BUCKET, "Key": old_key})
    s3.delete_object(Bucket=BUCKET, Key=old_key)


# The background helper: does the jobs one at a time, in order. A failed job is printed, never stops the app.
def work_through_jobs():
    while True:
        job, inputs = jobs.get()
        try:
            job(*inputs)
        except Exception as error:
            print("Could not save a photo to S3:", error)


# Start the background helper once, when the app starts.
threading.Thread(target=work_through_jobs, daemon=True).start()


# Turn the photo into JPEG bytes and add "upload it to today's unknown/" to the to-do list.
def save_capture(photo, answer):
    global waiting_photo
    day = day_folder()
    name = photo_name(answer)
    photo_file = io.BytesIO()
    photo.save(photo_file, format="JPEG", quality=90)
    jobs.put((upload, (photo_file.getvalue(), day, "unknown", name)))
    if answer.get("sign"):
        waiting_photo = (day, name)
    else:
        waiting_photo = None


# The visitor pressed Yes or No: add "move it to success/ or failure/" to the to-do list.
def sort_capture(answer):
    global waiting_photo
    if waiting_photo is None:
        return
    day, name = waiting_photo
    jobs.put((move, (day, name, "success" if answer == "yes" else "failure")))
    waiting_photo = None
