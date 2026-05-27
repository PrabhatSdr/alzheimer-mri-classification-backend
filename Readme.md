# Yukesh AI — Alzheimer's Detection System

A clinical decision-support UI for Alzheimer's detection via MRI scan,
split into clean HTML / CSS / JS layers with a Python + SQLite backend.

---

## Project Structure

```
alzheimer_app/
├── index.html     ← markup & layout
├── style.css      ← all styling & CSS variables
├── app.js         ← UI logic, analysis engine, DB API calls
├── server.py      ← Flask REST API + SQLite database (not ready)
└── README.md
```

---

## Quick Start

### 1. Install Python dependencies

```bash
pip install flask flask-cors
```

### 2. Start the backend server

```bash
python server.py
```

You should see:

```
[Yukesh] Database ready → ./Yukesh.db
[Yukesh] Server starting on http://localhost:5000
```

### 3. Open the frontend

Either open `index.html` directly in a browser, **or** serve it with a
local static server to avoid any CORS issues:

```bash
# Option A — Python built-in server (from the project folder)
python -m http.server 8080
# Then visit http://localhost:8080

# Option B — Node live-server
npx live-server
```

---

## How It Works

1. Fill in patient details and upload an MRI scan.
2. Select observed symptoms.
3. Click **Run AI Analysis** — the heuristic engine scores risk,
   predicts stage, and estimates hippocampal volume change.
4. Results are automatically `POST`ed to `http://localhost:5000/api/save`.
5. The response shows a green banner with the saved record ID.

---

## API Endpoints

| Method | Endpoint            | Description                         |
| ------ | ------------------- | ----------------------------------- |
| POST   | `/api/save`         | Save a full patient analysis record |
| GET    | `/api/records`      | List all records                    |
| GET    | `/api/records/<id>` | Single record detail                |
| GET    | `/api/stats`        | Aggregate statistics                |
| GET    | `/api/health`       | Server health check                 |

---

## Database Schema (SQLite — Yukesh.db)

### `patients`

| Column           | Type    | Notes          |
| ---------------- | ------- | -------------- |
| id               | INTEGER | Primary key    |
| patient_name     | TEXT    | Required       |
| dob              | TEXT    | Date of birth  |
| age              | INTEGER |                |
| sex              | TEXT    |                |
| education        | TEXT    |                |
| family_history   | TEXT    |                |
| referring_doctor | TEXT    |                |
| scan_date        | TEXT    |                |
| clinical_notes   | TEXT    |                |
| created_at       | TEXT    | Auto timestamp |

### `analyses`

| Column             | Type    | Notes                      |
| ------------------ | ------- | -------------------------- |
| id                 | INTEGER | Primary key                |
| patient_id         | INTEGER | FK → patients.id           |
| scan_type          | TEXT    | T1 / T2 / FLAIR / DWI      |
| mri_filename       | TEXT    |                            |
| symptoms           | TEXT    | Comma-separated            |
| risk_percent       | INTEGER | 0–100                      |
| risk_label         | TEXT    | Risk category description  |
| predicted_stage    | TEXT    | CDR stage label            |
| hippocampal_volume | TEXT    | e.g. -18%                  |
| confidence         | TEXT    | e.g. 87%                   |
| findings           | TEXT    | Pipe-separated findings    |
| generated_at       | TEXT    | ISO timestamp from browser |
| saved_at           | TEXT    | Auto timestamp (server)    |

---

## Notes

- The analysis engine is a **heuristic prototype** — not a trained ML model.
  Replace `generateResults()` in `app.js` with a real model API call for
  clinical use.
- All data is stored **locally** in `Yukesh.db` — no cloud services used.
- This tool is for **research and clinical support only** — not a medical
  diagnosis system.
