"use strict";

let selectedScanType = "T1";

const API_URL = "http://localhost:5000/api/analyze";

/* ──────────────────────────────────────────
   SCAN TYPE SELECTOR
────────────────────────────────────────── */
function setScanType(btn, type) {
  document
    .querySelectorAll(".seg-btn")
    .forEach((b) => b.classList.remove("active"));

  btn.classList.add("active");
  selectedScanType = type;

  const scanTypeTag = document.getElementById("scanTypeTag");
  if (scanTypeTag) {
    scanTypeTag.textContent = type + "-weighted";
  }
}

/* ──────────────────────────────────────────
   MRI FILE HANDLING
────────────────────────────────────────── */
function handleFile(input) {
  const file = input.files[0];
  if (!file) return;

  if (!file.type.startsWith("image/")) {
    alert("Please upload a valid image file.");
    input.value = "";
    return;
  }

  const reader = new FileReader();

  reader.onload = (e) => {
    document.getElementById("mriImg").src = e.target.result;
    document.getElementById("mriPlaceholder").style.display = "none";

    const preview = document.getElementById("mriPreview");
    preview.style.display = "flex";
    preview.style.flexDirection = "column";

    document.getElementById("mriFileName").textContent = file.name;

    const kb = file.size / 1024;
    document.getElementById("mriFileSize").textContent =
      kb > 1024 ? (kb / 1024).toFixed(1) + " MB" : kb.toFixed(1) + " KB";

    markStage(2);
  };

  reader.readAsDataURL(file);
}

function removeImage(e) {
  e.stopPropagation();

  document.getElementById("mriFile").value = "";
  document.getElementById("mriImg").src = "";
  document.getElementById("mriPlaceholder").style.display = "flex";
  document.getElementById("mriPreview").style.display = "none";
}

/* ──────────────────────────────────────────
   STAGE INDICATOR
────────────────────────────────────────── */
function markStage(n) {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById("s" + i);
    if (!el) continue;

    if (i < n) {
      el.classList.remove("active");
      el.classList.add("done");
      el.querySelector(".stage-num").textContent = "✓";
    } else if (i === n) {
      el.classList.add("active");
    }
  }
}

/* ──────────────────────────────────────────
   LIVE AGE RISK BAR
────────────────────────────────────────── */
const ageInput = document.getElementById("age");

if (ageInput) {
  ageInput.addEventListener("input", () => {
    const v = parseInt(ageInput.value) || 0;
    const pct = Math.min(100, Math.max(0, ((v - 50) / 40) * 100));

    document.getElementById("ageBar").style.width = pct + "%";
    document.getElementById("ageBarPct").textContent = v
      ? pct.toFixed(0) + "%"
      : "—";

    if (v) markStage(1);
  });
}

/* Auto-fill age from DOB */
const dobInput = document.getElementById("dob");

if (dobInput) {
  dobInput.addEventListener("change", function () {
    if (this.value) {
      const birthDate = new Date(this.value);
      const today = new Date();

      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();

      if (
        monthDiff < 0 ||
        (monthDiff === 0 && today.getDate() < birthDate.getDate())
      ) {
        age--;
      }

      document.getElementById("age").value = age;
      document.getElementById("age").dispatchEvent(new Event("input"));
    }
  });
}

/* ──────────────────────────────────────────
   DRAG & DROP
────────────────────────────────────────── */
const zone = document.getElementById("mriZone");

if (zone) {
  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("drag-over");
  });

  zone.addEventListener("dragleave", () => {
    zone.classList.remove("drag-over");
  });

  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("drag-over");

    const file = e.dataTransfer.files[0];

    if (file && file.type.startsWith("image/")) {
      const dt = new DataTransfer();
      dt.items.add(file);

      const inp = document.getElementById("mriFile");
      inp.files = dt.files;

      handleFile(inp);
    } else {
      alert("Please upload a valid image file.");
    }
  });
}

/* ──────────────────────────────────────────
   RUN ANALYSIS
────────────────────────────────────────── */
async function runAnalysis() {
  const name = document.getElementById("patientName").value.trim();
  const age = parseInt(document.getElementById("age").value) || 0;
  const fileInput = document.getElementById("mriFile");

  if (!name) {
    alert("Please enter the patient name.");
    return;
  }

  if (!age) {
    alert("Please enter patient age.");
    return;
  }

  if (!fileInput.files[0]) {
    alert("Please upload an MRI scan.");
    return;
  }

  document.getElementById("loadingOverlay").classList.add("show");

  try {
    const results = await generateResultsWithAI(age);

    document.getElementById("loadingOverlay").classList.remove("show");

    markStage(4);

    const s4 = document.getElementById("s4");
    if (s4) {
      s4.classList.add("done");
      s4.querySelector(".stage-num").textContent = "✓";
    }

    renderResults(results);
  } catch (err) {
    document.getElementById("loadingOverlay").classList.remove("show");

    console.error("[NeuroScan] Analysis error:", err);

    alert("Analysis failed: " + err.message);
  }
}

/* ──────────────────────────────────────────
   COLLECT DATA + SEND TO BACKEND
────────────────────────────────────────── */
async function generateResultsWithAI(age) {
  const familyHist = document.getElementById("family").value;

  const checkedBoxes = document.querySelectorAll(
    '#symptoms input[type="checkbox"]:checked'
  );

  const symptoms = Array.from(checkedBoxes).map((cb) =>
    cb.nextElementSibling.textContent.trim()
  );

  const patientData = {
    name: document.getElementById("patientName").value.trim(),
    dob: document.getElementById("dob").value,
    age,
    sex: document.getElementById("sex").value,
    education: document.getElementById("edu").value,
    familyHistory: familyHist,
    referringDoctor: document.getElementById("doctor").value.trim(),
    scanDate: document.getElementById("scanDate").value,
    clinicalNotes: document.getElementById("notes").value.trim(),
    scanType: selectedScanType,
    symptoms,
  };

  const formData = new FormData();

  formData.append("mri", document.getElementById("mriFile").files[0]);
  formData.append("patient_name", patientData.name);
  formData.append("dob", patientData.dob);
  formData.append("age", patientData.age);
  formData.append("sex", patientData.sex);
  formData.append("education", patientData.education);
  formData.append("family_history", patientData.familyHistory);
  formData.append("referring_doctor", patientData.referringDoctor);
  formData.append("scan_date", patientData.scanDate);
  formData.append("clinical_notes", patientData.clinicalNotes);
  formData.append("scan_type", patientData.scanType);
  formData.append("symptoms", symptoms.join(","));

  const response = await fetch(API_URL, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  console.log("Backend Response:", data);
  console.log("LLM Report:", data.llm_report);

  if (!response.ok || !data.success) {
    throw new Error(data.message || "Backend analysis failed.");
  }

  return {
    patientName: patientData.name,
    dob: patientData.dob,
    age: patientData.age,
    sex: patientData.sex,
    education: patientData.education,
    familyHistory: patientData.familyHistory,
    referringDoctor: patientData.referringDoctor,
    scanDate: patientData.scanDate,
    clinicalNotes: patientData.clinicalNotes,
    scanType: patientData.scanType,
    mriFileName: document.getElementById("mriFileName").textContent,
    symptoms,

    riskPercent: Math.round(data.model_result.confidence),
    riskLabel: data.model_result.risk_label,
    stage: data.model_result.prediction,
    hippocampalVolume: "N/A",
    confidence: data.model_result.confidence + "%",
    findings: data.prevention_advice || [],
    generatedAt: new Date().toISOString(),

    probabilities: data.model_result.probabilities,
    gradcamUrl: data.gradcam ? data.gradcam.image_url : "",

    llm_report: data.llm_report || null,
    backendResponse: data,
  };
}

/* ──────────────────────────────────────────
   RENDER RESULTS TO RESULT PAGE
────────────────────────────────────────── */
function renderResults(r) {
  sessionStorage.setItem("analysisResult", JSON.stringify(r));
  window.location.href = "result.html";
}

/* ──────────────────────────────────────────
   RESET FORM
────────────────────────────────────────── */
function resetForm() {
  document
    .querySelectorAll('input:not([type="file"]), select, textarea')
    .forEach((el) => (el.value = ""));

  document
    .querySelectorAll('#symptoms input[type="checkbox"]')
    .forEach((cb) => (cb.checked = false));

  removeImage({ stopPropagation: () => {} });

  document.getElementById("ageBar").style.width = "0%";
  document.getElementById("ageBarPct").textContent = "—";

  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById("s" + i);
    if (!el) continue;

    el.classList.remove("done", "active");
    el.querySelector(".stage-num").textContent = i;
  }

  const s1 = document.getElementById("s1");
  if (s1) s1.classList.add("active");
}