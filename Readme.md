# Yukesh AI — Alzheimer's Detection System

AI-powered Alzheimer's Disease Detection System using Brain MRI images and a fine-tuned ResNet50 model.

---

## Project Structure

```text
alzheimer backend/
│
├── frontend/
│   ├── index.html
│   ├── result.html
│   ├── style.css
│   └── app.js
│
├── backend/
│   ├── server.py
│   ├── models/
│   │   └── best_model.keras
│   └── uploads/
│
├── README.md
└── requirements.txt
```

---

## Features

* Patient Information Collection
* MRI Image Upload
* Alzheimer's Disease Classification
* Fine-tuned ResNet50 Model
* Confidence Score Prediction
* Risk Assessment
* Symptoms Recording
* Prevention Recommendations
* Professional Result Report Page
* Flask REST API Backend

---

## Model Information

### Selected Model

Fine-tuned ResNet50

### Validation Performance

| Metric    | Value  |
| --------- | ------ |
| Accuracy  | 96.62% |
| Precision | 96.65% |
| Recall    | 96.62% |
| F1 Score  | 96.62% |

The model was selected after comparing multiple deep learning architectures.

---

## Requirements

Install required packages:

```bash
pip install -r requirements.txt
```

or

```bash
pip install flask flask-cors tensorflow pillow numpy opencv-python
```

---

# How To Run

## Step 1: Start Backend Server

Open terminal inside backend directory:

```bash
cd backend
python server.py
```

Expected output:

```text
Model loaded successfully.
Server running at:
http://localhost:5000
```

You can verify backend health:

```text
http://localhost:5000/api/health
```

---

## Step 2: Start Frontend

Open a second terminal:

```bash
cd frontend
python -m http.server 8080
```

Open browser:

```text
http://localhost:8080
```

Alternatively, if using VS Code Live Server:

```text
http://127.0.0.1:5500/index.html
```

---

## Step 3: Run Analysis

1. Enter patient information
2. Upload MRI image
3. Select symptoms
4. Click "Run AI Analysis"

Workflow:

```text
Patient Form
      ↓
Upload MRI
      ↓
Backend Prediction
      ↓
ResNet50 Classification
      ↓
Result Page
```

---

## Output

The system generates:

* Predicted Alzheimer's Stage
* Confidence Score
* Risk Label
* Symptoms Summary
* Prevention Recommendations
* Model Information

Results are displayed on a dedicated report page.

---

## API Endpoint

### Analyze MRI

```http
POST /api/analyze
```

Form Data:

```text
mri
patient_name
age
sex
education
family_history
scan_type
symptoms
clinical_notes
```

Returns:

```json
{
  "success": true,
  "model_result": {
    "prediction": "ModerateDemented",
    "confidence": 96.62
  }
}
```

---

## Disclaimer

This system is intended for educational, research, and clinical decision-support purposes only.

It is not a medical diagnosis tool and should not replace consultation with qualified healthcare professionals.
