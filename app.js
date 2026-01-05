// const video = document.getElementById("video");
// const startBtn = document.getElementById("startCam");
// const captureBtn = document.getElementById("capture");
// const statusDiv = document.getElementById("status");
// const progress = document.getElementById("progress");
// const overlay = document.getElementById("videoOverlay");
// const results = document.getElementById("results");
// const themeBtn = document.getElementById("themeToggle");

// /* CAMERA */
// startBtn.onclick = async () => {
//   try {
//     const stream = await navigator.mediaDevices.getUserMedia({ video: true });
//     video.srcObject = stream;
//     overlay.style.display = "none";
//     captureBtn.disabled = false;
//     statusDiv.textContent = "✅ Camera started";
//   } catch {
//     statusDiv.textContent = "❌ Camera access denied";
//   }
// };

// /* MOCK INFERENCE */
// captureBtn.onclick = async () => {
//   statusDiv.textContent = "🧠 Inferencing…";
//   progress.value = 0;
//   results.innerHTML = "";

//   for (let i = 0; i <= 100; i += 10) {
//     await new Promise(r => setTimeout(r, 120));
//     progress.value = i;
//   }

//   results.innerHTML = `
//     <strong>Detected Mudra:</strong>
//     <span style="color:#22c55e">Pataka</span><br>
//     <strong>Confidence:</strong> 94%
//   `;
//   statusDiv.textContent = "✅ Done";
// };

// /* THEME */
// function setTheme(mode) {
//   document.body.classList.toggle("dark", mode === "dark");
//   themeBtn.textContent = mode === "dark" ? "☀️ Light" : "🌙 Dark";
//   localStorage.setItem("theme", mode);
// }

// setTheme(localStorage.getItem("theme") || "dark");

// themeBtn.onclick = () =>
//   setTheme(document.body.classList.contains("dark") ? "light" : "dark");


// const video = document.getElementById("video");
// const startBtn = document.getElementById("startCam");
// const captureBtn = document.getElementById("capture");
// const statusDiv = document.getElementById("status");
// const progress = document.getElementById("progress");
// const overlay = document.getElementById("videoOverlay");
// const results = document.getElementById("results");
// const themeBtn = document.getElementById("themeToggle");

// /* =========================
//    CAMERA START
// ========================= */
// startBtn.onclick = async () => {
//   try {
//     const stream = await navigator.mediaDevices.getUserMedia({ video: true });
//     video.srcObject = stream;
//     overlay.style.display = "none";
//     captureBtn.disabled = false;
//     statusDiv.textContent = "✅ Camera started";
//   } catch (err) {
//     console.error(err);
//     statusDiv.textContent = "❌ Camera access denied";
//   }
// };

// /* =========================
//    REAL YOLO INFERENCE
// ========================= */
// captureBtn.onclick = async () => {
//   try {
//     statusDiv.textContent = "🧠 Inferencing…";
//     progress.value = 10;
//     results.innerHTML = "";

//     // --- Capture frame from video ---
//     const canvas = document.createElement("canvas");
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;

//     const ctx = canvas.getContext("2d");
//     ctx.drawImage(video, 0, 0);

//     const imageBlob = await new Promise(resolve =>
//       canvas.toBlob(resolve, "image/jpeg", 0.95)
//     );

//     progress.value = 30;

//     // --- Send to FastAPI ---
//     const formData = new FormData();
//     formData.append("file", imageBlob, "frame.jpg");

//     const response = await fetch("http://0.0.0.0:8000/infer", {
//       method: "POST",
//       body: formData
//     });

//     if (!response.ok) {
//       throw new Error("Inference request failed");
//     }

//     progress.value = 70;

//     // --- Receive annotated image ---
//     const resultBlob = await response.blob();
//     const resultURL = URL.createObjectURL(resultBlob);

//     // --- Show result ---
//     results.innerHTML = `
//       <strong>Inference Result:</strong><br>
//       <img src="${resultURL}"
//            style="
//              margin-top:10px;
//              max-width:100%;
//              border-radius:12px;
//              border:2px solid #22c55e;
//            ">
//     `;

//     progress.value = 100;
//     statusDiv.textContent = "✅ Done";

//   } catch (err) {
//     console.error(err);
//     statusDiv.textContent = "❌ Inference failed";
//   }
// };

// /* =========================
//    THEME TOGGLE
// ========================= */
// function setTheme(mode) {
//   document.body.classList.toggle("dark", mode === "dark");
//   themeBtn.textContent = mode === "dark" ? "☀️ Light" : "🌙 Dark";
//   localStorage.setItem("theme", mode);
// }

// // Load saved theme
// setTheme(localStorage.getItem("theme") || "dark");

// themeBtn.onclick = () =>
//   setTheme(document.body.classList.contains("dark") ? "light" : "dark");


const video = document.getElementById("video");
const startBtn = document.getElementById("startCam");
const captureBtn = document.getElementById("capture");
const statusDiv = document.getElementById("status");
const progress = document.getElementById("progress");
const overlay = document.getElementById("videoOverlay");
const results = document.getElementById("results");
const themeBtn = document.getElementById("themeToggle");

let cameraStream = null;

/* =========================
   CAMERA START / STOP
========================= */
startBtn.onclick = async () => {
  try {
    // ---------- STOP CAMERA ----------
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
      video.srcObject = null;

      overlay.style.display = "flex";
      captureBtn.disabled = true;
      startBtn.textContent = "▶ Start Camera";
      statusDiv.textContent = "⏹ Camera stopped";
      return;
    }

    // ---------- START CAMERA ----------
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = cameraStream;

    overlay.style.display = "none";
    captureBtn.disabled = false;
    startBtn.textContent = "⏹ Stop Camera";
    statusDiv.textContent = "✅ Camera started";

  } catch (err) {
    console.error(err);
    statusDiv.textContent = "❌ Camera access denied";
  }
};

/* =========================
   REAL YOLO INFERENCE
========================= */
captureBtn.onclick = async () => {
  try {
    if (!cameraStream) {
      statusDiv.textContent = "⚠️ Start camera first";
      return;
    }

    statusDiv.textContent = "🧠 Inferencing…";
    progress.value = 10;
    results.innerHTML = "";

    // --- Capture frame ---
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const imageBlob = await new Promise(resolve =>
      canvas.toBlob(resolve, "image/jpeg", 0.95)
    );

    progress.value = 30;

    // --- Send to FastAPI ---
    const formData = new FormData();
    formData.append("file", imageBlob, "frame.jpg");

    const response = await fetch("http://127.0.0.1:8000/infer", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Inference request failed");
    }

    progress.value = 70;

    // --- Receive annotated image ---
    const resultBlob = await response.blob();
    const resultURL = URL.createObjectURL(resultBlob);

    results.innerHTML = `
      <strong>Inference Result:</strong><br>
      <img src="${resultURL}"
           style="
             margin-top:10px;
             max-width:100%;
             border-radius:12px;
             border:2px solid #22c55e;
           ">
    `;

    progress.value = 100;
    statusDiv.textContent = "✅ Done";

  } catch (err) {
    console.error(err);
    statusDiv.textContent = "❌ Inference failed";
  }
};

/* =========================
   THEME TOGGLE
========================= */
function setTheme(mode) {
  document.body.classList.toggle("dark", mode === "dark");
  themeBtn.textContent = mode === "dark" ? "☀️ Light" : "🌙 Dark";
  localStorage.setItem("theme", mode);
}

setTheme(localStorage.getItem("theme") || "dark");

themeBtn.onclick = () =>
  setTheme(document.body.classList.contains("dark") ? "light" : "dark");
