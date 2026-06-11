"use strict"; /*for no mistake ( rules follow garauna ) */
let selectedScanType = "T1";

const API_URL = "http://localhost:5000/api/analyze";

/* ──────────────────────────────────────────
   SCAN TYPE SELECTOR (show which scan selscted t!, T2 or k xa tai)
────────────────────────────────────────── */
function setScanType(btn, type) {
  document
    .querySelectorAll(".seg-btn")
    .forEach((b) => b.classList.remove("active"));

  btn.classList.add("active");
  selectedScanType = type;
  document.getElementById("scanTypeTag").textContent = type + "-weighted";
}

/* ──────────────────────────────────────────
   MRI FILE HANDLING ( preview img, read, display file name aani stage progress move on  )
────────────────────────────────────────── */
function handleFile(input) {
  const file = input.files[0];
  if (!file) return;

  const reader = new FileReader();

  reader.onload = (e) => {
    document.getElementById("mriImg").src = e.target.result;
    document.getElementById("mriPlaceholder").style.display = "none";

    const preview = document.getElementById("mriPreview");
    preview.style.display = "flex";
    preview.style.flexDirection = "column";

    document.getElementById("mriFileName").textContent = file.name;

    const kb = (file.size / 1024).toFixed(1);
    document.getElementById("mriFileSize").textContent =
      kb > 1024 ? (kb / 1024).toFixed(1) + " MB" : kb + " KB";

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
   STAGE INDICATOR( completed vanerwa tick sign on progress)
────────────────────────────────────────── */
function markStage(n) {
  for (let i = 1; i <= n; i++) {
    const el = document.getElementById("s" + i);
    if (!el) continue;

    if (i < n) {
      el.classList.remove("active");
      el.classList.add("done");
      el.querySelector(".stage-num").textContent = "✓";
    } else {
      el.classList.add("active");
    }
  }
}

/* ──────────────────────────────────────────
   LIVE AGE RISK BAR
───────────────────────────── ( age anusar risk dekhauni )───────────── */
const ageInput = document.getElementById("age");

ageInput.addEventListener("input", () => {
  const v = parseInt(ageInput.value) || 0;
  const pct = Math.min(100, Math.max(0, ((v - 50) / 40) * 100));

  document.getElementById("ageBar").style.width = pct + "%";
  document.getElementById("ageBarPct").textContent = v
    ? pct.toFixed(0) + "%"
    : "—";

  if (v) markStage(1);
});

/* Auto-fill age from DOB */
document.getElementById("dob").addEventListener("change", function () {
  if (this.value) {
    const age = new Date().getFullYear() - new Date(this.value).getFullYear();
    document.getElementById("age").value = age;
    document.getElementById("age").dispatchEvent(new Event("input"));
  }
});

/* ──────────────────────────────────────────
   DRAG & DROP
────────────────────────────────────────── */
const zone = document.getElementById("mriZone");

zone.addEventListener("dragover", (e) => {
  e.preventDefault();
  zone.classList.add("drag-over");
});

zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));

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
  }
});

/* ──────────────────────────────────────────
   RUN ANALYSIS ( check form fillup , display result, error )
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

    renderResults(results);

    saveToDatabase(results);

    markStage(4);

    const s4 = document.getElementById("s4");
    s4.classList.add("done");
    s4.querySelector(".stage-num").textContent = "✓";
  } catch (err) {
    document.getElementById("loadingOverlay").classList.remove("show");

    console.error("[NeuroScan] Analysis error:", err);

    alert("Analysis failed: " + err.message);
  }
}

/* ──────────────────────────────────────────
   data collect
────────────────────────────────────────── */
async function generateResultsWithAI(age) {
  /* Collect form data */
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
    backendResponse: data,
  };
}

/* ── Fallback helpers (used if AI amits a field) ── */
function deriveRiskLabel(risk) {
  return risk >= 60
    ? "High risk — refer urgently"
    : risk >= 35
      ? "Moderate risk — monitor closely"
      : "Low risk — routine follow-up";
}

function deriveStage(risk) {
  return risk >= 75
    ? "Moderate–Severe"
    : risk >= 45
      ? "Mild–Moderate"
      : risk >= 25
        ? "Mild (MCI)"
        : "No Impairment";
}

/* ──────────────────────────────────────────
   RENDER RESULTS TO DOM
────────────────────────────────────────── */
/* ──────────────────────────────────────────
   RENDER RESULTS TO NEXT PAGE
────────────────────────────────────────── */
function renderResults(r) {

  sessionStorage.setItem(
    "analysisResult",
    JSON.stringify(r)
  );

  window.location.href = "result.html";
}

/* ──────────────────────────────────────────
   SAVE TO DATABASE (via Flask API)
────────────────────────────────────────── */
async function saveToDatabase(results) {
  console.log("Database disabled for midterm.");
  console.log("Result not saved:", results);
}


  /* IMPORTANT : YO part outcome ko lagi ho no need paxi ma herxu 
  const userPrompt = `Analyse MRI scan and patient data:

Patient: ${patientData.name}, Age ${patientData.age}, ${patientData.sex || "sex not specified"}
Education: ${patientData.education || "not specified"}
Family history: ${patientData.familyHistory || "not specified"}
Scan type: ${patientData.scanType}
Scan date: ${patientData.scanDate || "not specified"}
Symptoms reported: ${symptoms.length ? symptoms.join(", ") : "none selected"}
Clinical notes: ${patientData.clinicalNotes || "none"}

Examine the attached MRI image carefully for: hippocampal atrophy, cortical thinning, ventricular enlargement, white matter changes, and other Alzheimer's-related biomarkers. Return only the JSON object.`;

  /* Strip the data-URL prefix to get raw base64 
  const base64Image = mriSrc.split(",")[1];
  const mimeMatch = mriSrc.match(/data:(image\/[a-z+]+);base64/);
  const mimeType = mimeMatch ? mimeMatch[1] : "image/jpeg";

  /* Call  API 
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: systemPrompt,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "image",
              source: {
                type: "base64",
                media_type: mimeType,
                data: base64Image,
              },
            },
            { type: "text", text: userPrompt },
          ],
        },
      ],
    }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(
      errData.error?.message || `API returned ${response.status}`,
    );
  }

  const data = await response.json();
  const rawText = data.content
    .map((b) => b.text || "")
    .join("")
    .trim();

  /* Parse — strip any accidental markdown fences 
  let parsed;
  try {
    const clean = rawText.replace(/```json|```/g, "").trim();
    parsed = JSON.parse(clean);
  } catch (e) {
    throw new Error(
      "AI returned malformed JSON. Raw: " + rawText.slice(0, 200),
    );
  }

  /* Validate & fall back gracefully 
  const risk = Math.min(100, Math.max(0, parseInt(parsed.riskPercent) || 0));

  return {
    /* Patient passthrough 
    patientName: patientData.name,
    dob: patientData.dob,
    age,
    sex: patientData.sex,
    education: patientData.education,
    familyHistory: patientData.familyHistory,
    referringDoctor: patientData.referringDoctor,
    scanDate: patientData.scanDate,
    clinicalNotes: patientData.clinicalNotes,
    scanType: patientData.scanType,
    mriFileName: document.getElementById("mriFileName").textContent,
    symptoms,
    /* AI results 
    riskPercent: risk,
    riskLabel: parsed.riskLabel || deriveRiskLabel(risk),
    stage: parsed.stage || deriveStage(risk),
    hippocampalVolume: parsed.hippocampalVolume || "—",
    confidence: parsed.confidence || "—",
    findings: Array.isArray(parsed.findings)
      ? parsed.findings
      : [parsed.findings || "Analysis complete."],
    generatedAt: new Date().toISOString(),
  };
}

/* ── Fallback helpers (used if AI amits a field) ── 
function deriveRiskLabel(risk) {
  return risk >= 60
    ? "High risk — refer urgently"
    : risk >= 35
      ? "Moderate risk — monitor closely"
      : "Low risk — routine follow-up";
}
function deriveStage(risk) {
  return risk >= 75
    ? "Moderate–Severe"
    : risk >= 45
      ? "Mild–Moderate"
      : risk >= 25
        ? "Mild (MCI)"
        : "No Impairment";
}

/* ──────────────────────────────────────────
   RENDER RESULTS TO DOM
────────────────────────────────────────── 
function renderResults(r) {
  /* Risk 
  const riskEl = document.getElementById("riskPct");
  riskEl.textContent = r.riskPercent + "%";
  riskEl.className =
    "rc-val " +
    (r.riskPercent >= 60
      ? "val-danger"
      : r.riskPercent >= 35
        ? "val-warn"
        : "val-safe");
  document.getElementById("riskLabel").textContent = r.riskLabel;

  /* Stage 
  const stageEl = document.getElementById("stageVal");
  stageEl.textContent = r.stage;
  stageEl.className =
    "rc-val " +
    (r.riskPercent >= 60
      ? "val-danger"
      : r.riskPercent >= 35
        ? "val-warn"
        : "val-safe");

  /* Hippocampal volume 
  const hippoEl = document.getElementById("hippoVal");
  hippoEl.textContent = r.hippocampalVolume;
  hippoEl.className =
    "rc-val " +
    (r.riskPercent >= 60
      ? "val-danger"
      : r.riskPercent >= 35
        ? "val-warn"
        : "val-safe");

  /* Confidence 
  document.getElementById("confVal").textContent = r.confidence;

  /* Findings 
  const ul = document.getElementById("findingsList");
  ul.innerHTML = "";
  r.findings.forEach((f) => {
    const li = document.createElement("li");
    li.textContent = f;
    ul.appendChild(li);
  });

  /* Finding box accent color 
  const fb = document.getElementById("findingBox");
  const accent =
    r.riskPercent >= 60
      ? "var(--danger)"
      : r.riskPercent >= 35
        ? "var(--warn)"
        : "var(--success)";
  const bg =
    r.riskPercent >= 60
      ? "rgba(248,113,113,0.06)"
      : r.riskPercent >= 35
        ? "rgba(245,158,11,0.06)"
        : "rgba(52,211,153,0.06)";
  fb.style.borderLeftColor = accent;
  fb.style.background = bg;
  fb.querySelector("h3").style.color = accent;

  /* Timestamp 
  document.getElementById("reportTimestamp").textContent =
    "Generated: " + new Date(r.generatedAt).toLocaleString();

  /* Show panel 
  const rp = document.getElementById("resultPanel");
  rp.classList.add("visible");
  rp.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ──────────────────────────────────────────
   SAVE TO DATABASE (via Flask API)
────────────────────────────────────────── 
async function saveToDatabase(results) {
  const statusEl = document.getElementById("dbStatus");
  statusEl.style.display = "flex";
  statusEl.className = "db-status saving";
  statusEl.textContent = "💾  Saving record to database…";

  try {
    const payload = {
      patient_name: results.patientName,
      dob: results.dob,
      age: results.age,
      sex: results.sex,
      education: results.education,
      family_history: results.familyHistory,
      referring_doctor: results.referringDoctor,
      scan_date: results.scanDate,
      clinical_notes: results.clinicalNotes,
      scan_type: results.scanType,
      mri_filename: results.mriFileName,
      symptoms: results.symptoms.join(", "),
      risk_percent: results.riskPercent,
      risk_label: results.riskLabel,
      predicted_stage: results.stage,
      hippocampal_volume: results.hippocampalVolume,
      confidence: results.confidence,
      findings: results.findings.join(" | "),
      generated_at: results.generatedAt,
    };

    const response = await fetch("http://localhost:5000/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (response.ok && data.success) {
      statusEl.className = "db-status saved";
      statusEl.innerHTML = `✅  Record saved to database &nbsp;<span style="opacity:.6;font-weight:400;">— ID #${data.record_id}</span>`;
    } else {
      throw new Error(data.message || "Unknown error");
    }
  } catch (err) {
    statusEl.className = "db-status error";
    statusEl.innerHTML = `⚠️  Database save failed: ${err.message}
      &nbsp;—&nbsp; <span style="opacity:.7;">Is the server running? See server.py</span>`;
    console.error("[NeuroScan] DB save error:", err);
  }
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

  const resultPanel = document.getElementById("resultPanel");
  if (resultPanel) {
    resultPanel.classList.remove("visible");
  }

  const dbStatus = document.getElementById("dbStatus");
  if (dbStatus) {
    dbStatus.style.display = "none";
  }

  document.getElementById("ageBar").style.width = "0%";
  document.getElementById("ageBarPct").textContent = "—";

  /* Reset stage indicators */
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById("s" + i);
    el.classList.remove("done", "active");
    el.querySelector(".stage-num").textContent = i;
  }

  document.getElementById("s1").classList.add("active");
}