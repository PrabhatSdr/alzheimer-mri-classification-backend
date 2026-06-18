# Alzheimer's Disease Detection System

## Overview

This project is an AI-powered Alzheimer's Disease Detection System that analyzes brain MRI images and classifies them into different stages of dementia using Deep Learning.

The system uses a fine-tuned ResNet50 model trained on MRI scans and provides:

* Alzheimer's stage prediction
* Confidence score
* Class probabilities
* Grad-CAM explainability heatmap
* Symptom-based recommendations
* Professional result visualization through a web interface

The project follows a client-server architecture where the frontend collects patient information and MRI images, while the Flask backend performs model inference and generates predictions.

---

# Project Directory Structure

```text
ALZHEIMER/
│
├── backend/
│   │
│   ├── evaluation_results/
│   │   ├── model_comparison.csv
│   │   ├── confusion_matrices
│   │   └── classification_reports
│   │
│   ├── models/
│   │   └── best_model.keras
│   │
│   ├── outputs/
│   │   └── generated_gradcam_images
│   │
│   ├── uploads/
│   │   └── uploaded_mri_images
│   │
│   ├── .gitignore
│   ├── gradcam.py
│   ├── requirements.txt
│   └── server.py
│
├── app.js
├── index.html
├── result.html
├── style.css
└── README.md
```

---

# Features

## MRI Classification

The system accepts MRI brain images and predicts one of the following Alzheimer's stages:

```text
NonDemented
VeryMildDemented
MildDemented
ModerateDemented
```

---

## Confidence Score

The model provides prediction confidence using the Softmax output layer.

Example:

```text
Prediction: ModerateDemented

Confidence: 96.62%
```

---

## Class Probabilities

The backend returns probabilities for all four classes:

```text
NonDemented         : 1.24%
VeryMildDemented    : 2.11%
MildDemented        : 0.03%
ModerateDemented    : 96.62%
```

---

## Grad-CAM Explainability

Grad-CAM highlights the regions of the MRI image that influenced the model prediction.

Benefits:

* Model transparency
* Better visualization
* Explainable AI
* Clinical decision support

Generated heatmaps are displayed on the result page.

---

## Symptom-Based Recommendations

Based on selected symptoms and model prediction, the system provides:

* Prevention suggestions
* Follow-up recommendations
* Monitoring advice
* Clinical consultation guidance

---

# Deep Learning Models Evaluated

Several models were trained and evaluated before selecting the final model.

Models compared:

```text
CNN
MobileNetV2
DenseNet121
ResNet50
```

---

# Final Selected Model

```text
Fine-tuned ResNet50
```

Reason for selection:

* Highest validation accuracy
* Best Precision
* Best Recall
* Best F1-score
* Stable convergence during training

---

# Model Performance

| Metric    | Score  |
| --------- | ------ |
| Accuracy  | 96.62% |
| Precision | 96.65% |
| Recall    | 96.62% |
| F1-score  | 96.62% |

---

# Technologies Used

## Backend

```text
Python
Flask
TensorFlow
Keras
NumPy
OpenCV
Pillow
Flask-CORS
```

---

## Frontend

```text
HTML5
CSS3
JavaScript
```

---

## Explainability

```text
Grad-CAM
```

---

# Input Requirements

Accepted image formats:

```text
jpg
jpeg
png
bmp
tiff
```

Input image size:

```text
224 × 224 × 3
```

Preprocessing:

```python
tensorflow.keras.applications.resnet50.preprocess_input
```

---

# Required Model File

The trained model is not included in GitHub because of its size.

Place the model manually:

```text
backend/models/best_model.keras
```

---

# Installation

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd ALZHEIMER
```

---

## Step 2: Install Dependencies

Navigate to backend:

```bash
cd backend
```

Install requirements:

```bash
pip install -r requirements.txt
```

or

```bash
pip install flask flask-cors tensorflow numpy pillow opencv-python
```

---

# Running the Backend

Inside backend folder:

```bash
python server.py
```

Expected output:

```text
[Backend] Loading best ResNet50 model...
[Backend] Model loaded successfully.
[Backend] Server running at http://localhost:5000
```

---

# Verify Backend

Open:

```text
http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "running"
}
```

---

# Running the Frontend

## Option 1: VS Code Live Server

Open:

```text
index.html
```

using Live Server.

Example:

```text
http://127.0.0.1:5500/index.html
```

---

## Option 2: Python HTTP Server

From project root:

```bash
python -m http.server 8080
```

Open:

```text
http://localhost:8080/index.html
```

---

# System Workflow

```text
Patient Information
        ↓
MRI Upload
        ↓
Frontend
        ↓
Flask API
        ↓
MRI Preprocessing
        ↓
Fine-tuned ResNet50
        ↓
Prediction
        ↓
Confidence Score
        ↓
Grad-CAM Generation
        ↓
Result Page
```

---

# API Endpoint

## Analyze MRI

### Request

```http
POST /api/analyze
```

### Form Data

```text
mri
patient_name
dob
age
sex
education
family_history
referring_doctor
scan_date
clinical_notes
scan_type
symptoms
```

---

### Example Response

```json
{
  "success": true,
  "model_result": {
    "prediction": "ModerateDemented",
    "confidence": 96.62,
    "class_index": 1,
    "probabilities": {
      "MildDemented": 0.01,
      "ModerateDemented": 96.62,
      "NonDemented": 1.15,
      "VeryMildDemented": 2.22
    }
  },
  "gradcam": {
    "enabled": true,
    "image_url": "http://localhost:5000/outputs/gradcam_image.jpg"
  }
}
```

---

# Grad-CAM Integration

Grad-CAM is generated immediately after prediction.

Process:

```text
MRI Image
      ↓
ResNet50 Prediction
      ↓
Last Convolution Layer
      ↓
Gradient Calculation
      ↓
Heatmap Generation
      ↓
Overlay on MRI
      ↓
Display in result.html
```

---

# Evaluation Results

All evaluation reports are available inside:

```text
backend/evaluation_results/
```

Contents:

```text
Classification Reports
Confusion Matrices
Model Comparison CSV
Accuracy Scores
Precision Scores
Recall Scores
F1 Scores
```

---

# Git Ignore Configuration

Recommended `.gitignore`:

```gitignore
*.keras
*.h5

backend/models/
backend/uploads/
backend/outputs/

__pycache__/
*.pyc

.env
venv/
```

---

# Future Improvements

The following features are planned for final submission:

```text
Admin Dashboard
Database Integration
Patient History Tracking
LLM-Based Report Generation
Advanced Analytics Dashboard
Multi-user Support
Authentication System
Exportable PDF Reports
```

---

# Disclaimer

This project is intended for educational, research, and clinical decision-support purposes only.

The system is not a substitute for professional medical diagnosis. Final diagnosis and treatment decisions must always be made by qualified healthcare professionals.
