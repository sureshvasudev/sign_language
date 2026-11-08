// AI Sign Language Translator: what happens when buttons are clicked.
//
// Capture takes a photo, sends it to the AI on this laptop (POST /predict),
// lights up the workflow steps while the AI works, then shows the result.

// Short helper: find a page element by its id.
function byId(id) {
  return document.getElementById(id);
}

// The 5 steps of the workflow animation, in order.
const workflowSteps = document.querySelectorAll(".steps li");
const STEP_CAPTURE = 0;
const STEP_SEND = 1;
const STEP_FIND_HAND = 2;
const STEP_SCORE = 3;
const STEP_CHECK = 4;

// How long each step stays lit, in milliseconds, so visitors can follow it.
const STEP_TIME = 500;

// True once the webcam is on.
let cameraIsOn = false;

// Wait for a number of milliseconds (used with "await").
function wait(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

// Show one of the three right-hand cards ("guide", "pipe" or "result") and hide the others.
function showCard(cardId) {
  for (const id of ["guide", "pipe", "result"]) {
    byId(id).hidden = (id !== cardId);
  }
}

// Show or hide the "AI is analysing your sign..." message in the camera box.
function showAnalysing(isAnalysing) {
  byId("camBusy").hidden = !isAnalysing;
}

// ---------- Camera ----------

// Ask the browser for the webcam and show its live picture in the camera box.
async function startCamera() {
  byId("camError").hidden = true;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720 },
      audio: false
    });
    byId("camVideo").srcObject = stream;
    byId("camVideo").hidden = false;
    byId("camIdle").hidden = true;
    byId("captureBtn").disabled = false;
    cameraIsOn = true;
  } catch (error) {
    // For example: the visitor clicked "Block", or no webcam is plugged in.
    byId("camError").textContent = "Could not turn on the camera. Check that a webcam is connected and that the browser is allowed to use it.";
    byId("camError").hidden = false;
    console.log("Camera error:", error);
  }
}

// Turn the webcam off (its light goes off) and show CLICK TO START again.
function stopCamera() {
  const video = byId("camVideo");
  if (video.srcObject) {
    video.srcObject.getTracks().forEach(track => track.stop());
    video.srcObject = null;
  }
  video.hidden = true;
  byId("camIdle").hidden = false;
  byId("captureBtn").disabled = true;
  cameraIsOn = false;
}

// Take a photo from the live video and return it as a JPEG file.
function takePhoto() {
  const video = byId("camVideo");
  const canvas = byId("snapCanvas");

  // Make the canvas the same size as the video, then copy the current frame onto it.
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  // Turn the canvas into a JPEG (quality 0.9 out of 1).
  return new Promise(resolve => canvas.toBlob(resolve, "image/jpeg", 0.9));
}

// ---------- Talking to the AI ----------

// Send the photo to the AI on this laptop and return its answer.
async function askTheAI(photo) {
  const form = new FormData();
  form.append("photo", photo, "capture.jpg");
  try {
    const response = await fetch("/predict", { method: "POST", body: form });
    if (!response.ok) {
      return { status: "error" };
    }
    return await response.json();
  } catch (error) {
    // For example: the Python server is not running.
    console.log("Could not reach the AI:", error);
    return { status: "error" };
  }
}

// ---------- Workflow animation ----------

// Light up one step: the steps before it are "done", this one is "on", the rest are dim.
function lightStep(stepNumber) {
  workflowSteps.forEach((step, index) => {
    if (index < stepNumber) {
      step.className = "done";
    } else if (index === stepNumber) {
      step.className = "on";
    } else {
      step.className = "";
    }
  });
}

// Mark every step up to and including this one as "done".
function finishStepsUpTo(stepNumber) {
  workflowSteps.forEach((step, index) => {
    if (index <= stepNumber) {
      step.className = "done";
    }
  });
}

// ---------- Capture ----------

// Runs when Capture is pressed: photo, send to the AI, animate the steps, show the result.
async function capture() {
  if (!cameraIsOn) {
    return;
  }
  byId("captureBtn").disabled = true;
  showAnalysing(true);
  showCard("pipe");

  lightStep(STEP_CAPTURE);
  const photo = await takePhoto();

  // We have the photo, so turn the webcam off. Hide CLICK TO START until Try Again or Finish.
  stopCamera();
  byId("camIdle").hidden = true;
  await wait(STEP_TIME);

  // Start sending now. The answer arrives in the background while the steps light up.
  lightStep(STEP_SEND);
  const answerArriving = askTheAI(photo);
  await wait(STEP_TIME);

  // The server finds the hand and scores the signs. We wait here until it answers.
  lightStep(STEP_FIND_HAND);
  await wait(STEP_TIME);
  const answer = await answerArriving;

  // If there was a hand, show the last two steps (the server has already done them).
  if (answer.status !== "no_hand" && answer.status !== "error") {
    lightStep(STEP_SCORE);
    await wait(STEP_TIME);
    lightStep(STEP_CHECK);
    await wait(STEP_TIME);
    finishStepsUpTo(STEP_CHECK);
  } else {
    finishStepsUpTo(STEP_FIND_HAND);
  }
  await wait(STEP_TIME);

  showResult(answer);
  showAnalysing(false);
  loadStats();
}

// ---------- Result card ----------

// Turn a score like 0.873 into "87%".
function asPercent(score) {
  return Math.round(score * 100) + "%";
}

// Fill in the result card for the AI's answer, then show it.
function showResult(answer) {
  let title = "";
  let icon = "";
  let details = "";
  let askIfRight = false;

  if (answer.status === "ok") {
    title = "THE AI HAS SUCCESSFULLY RECOGNISED THE SIGN!";
    icon = (answer.sign === "I LOVE YOU") ? "🤟" : answer.sign;
    let confidence = "Confidence <b>" + asPercent(answer.confidence) + "</b>";
    if (answer.confidence === null) {
      confidence = "<small>Found by the hand-points rule</small>";
    }
    details = "<b>" + answer.sign + "</b> · Meaning: " + answer.meaning + " · " + confidence;
    askIfRight = true;
  } else if (answer.status === "not_sure") {
    title = "THE AI FAILED TO RECOGNISE THE SIGN.";
    icon = "🤔";
    details = "The AI was not sure (best guess " + answer.sign + ", only " + asPercent(answer.confidence) + "). Please try again.";
  } else if (answer.status === "no_hand") {
    title = "THE AI COULD NOT FIND A HAND.";
    icon = "✋";
    details = "Please try again.<br><small>Tip: stand in good light, about an arm's length from the camera, with your whole hand in the picture.</small>";
  } else if (answer.status === "not_included") {
    title = "SIGN NOT INCLUDED IN THIS PROJECT.";
    icon = "🚫";
    details = "The AI thinks this is " + answer.sign + " (" + asPercent(answer.confidence) + "), which is not one of our 9 signs. Please try one of the signs below.";
  } else {
    title = "SOMETHING WENT WRONG.";
    icon = "⚠️";
    details = "The page could not reach the AI. Please check that the Python server is running, then try again.";
  }

  byId("resultTitle").textContent = title;
  byId("resultIcon").textContent = icon;
  byId("resultDetails").innerHTML = details;
  byId("feedback").hidden = !askIfRight;
  byId("thanks").hidden = true;
  showCard("result");
}

// ---------- Statistics ----------

// Put yesterday's and today's numbers into the statistics row.
function showStats(stats) {
  for (const name of ["attempts", "correct", "incorrect", "unknown"]) {
    byId("yesterday-" + name).textContent = stats.yesterday[name];
    byId("today-" + name).textContent = stats.today[name];
  }
}

// Ask the server for the saved numbers and show them.
async function loadStats() {
  try {
    const response = await fetch("/stats");
    if (response.ok) {
      showStats(await response.json());
    }
  } catch (error) {
    // For example: the Python server is not running.
    console.log("Could not load the statistics:", error);
  }
}

// Yes / No: thank the visitor, save the answer on the server, and show the new numbers.
async function answerFeedback(answer) {
  byId("feedback").hidden = true;
  byId("thanks").hidden = false;
  try {
    const response = await fetch("/stats/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer: answer })
    });
    if (response.ok) {
      showStats(await response.json());
    }
  } catch (error) {
    console.log("Could not save the answer:", error);
  }
}

// Ask "are you sure?", then set the statistics back to zero on the server.
async function resetStats() {
  if (!confirm("Reset all statistics to 0? The old numbers are kept in the backend/stats-backups folder.")) {
    return;
  }
  try {
    const response = await fetch("/stats/reset", { method: "POST" });
    if (response.ok) {
      showStats(await response.json());
    }
  } catch (error) {
    console.log("Could not reset the statistics:", error);
  }
}

// Hidden shortcut for the team: Ctrl+Alt+R resets the statistics. There is no button, so visitors won't find it.
function onKeyDown(event) {
  if (event.ctrlKey && event.altKey && event.key.toLowerCase() === "r") {
    event.preventDefault();
    resetStats();
  }
}

// ---------- Try Again / Finish ----------

// Go back to the "How to play" card, ready for the next try.
function startOver() {
  showAnalysing(false);
  showCard("guide");
  byId("camIdle").hidden = cameraIsOn;
  byId("captureBtn").disabled = !cameraIsOn;
}

// Try Again: go back to the start and turn the camera on again by itself.
function tryAgain() {
  startOver();
  startCamera();
}

// Finish: the camera stays off. Go back to the start, ready for the next visitor.
function finish() {
  startOver();
}

// ---------- Info popup ----------

// Open the full-page info popup.
function openAbout() {
  byId("about").showModal();
}

// Close the info popup.
function closeAbout() {
  byId("about").close();
}

// Connect the buttons to the functions above.
byId("startBtn").addEventListener("click", startCamera);
byId("captureBtn").addEventListener("click", capture);
byId("yesBtn").addEventListener("click", () => answerFeedback("yes"));
byId("noBtn").addEventListener("click", () => answerFeedback("no"));
byId("againBtn").addEventListener("click", tryAgain);
byId("finishBtn").addEventListener("click", finish);
byId("openAbout").addEventListener("click", openAbout);
byId("closeAbout").addEventListener("click", closeAbout);
document.addEventListener("keydown", onKeyDown);

// Show the saved statistics as soon as the page opens.
loadStats();
