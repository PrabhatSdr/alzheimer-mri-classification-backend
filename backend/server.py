# =====================================================
# ALZHEIMER MRI DETECTION BACKEND
# Midterm Version
#
# Features:
# 1. Accept MRI image from frontend
# 2. Validate uploaded file
# 3. Load best ResNet50 model
# 4. Predict Alzheimer class
# 5. Return confidence + probabilities
# 6. Return symptom-based prevention advice
#
# No database
# No LLM integration
# =====================================================

import os
import uuid
import numpy as np
from PIL import Image

import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input

from flask import Flask, request, jsonify
from flask_cors import CORS


# =====================================================
# 1. BASIC CONFIGURATION
# =====================================================

MODEL_PATH = "models/best_model.keras"
UPLOAD_DIR = "uploads"

IMG_SIZE = (224, 224)

CLASS_NAMES = [
    "MildDemented",
    "ModerateDemented",
    "NonDemented",
    "VeryMildDemented"
]

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "bmp",
    "tiff"
}

os.makedirs(UPLOAD_DIR, exist_ok=True)


# =====================================================
# 2. FLASK APP SETUP
# =====================================================

app = Flask(__name__)
CORS(app)


# =====================================================
# 3. LOAD TRAINED MODEL
# =====================================================

print("[Backend] Loading best ResNet50 model...")

model = tf.keras.models.load_model(MODEL_PATH)

print("[Backend] Model loaded successfully.")


# =====================================================
# 4. FILE VALIDATION FUNCTION
# =====================================================

def allowed_file(filename):
    """
    Checks whether uploaded file has allowed image extension.
    """

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# =====================================================
# 5. MRI IMAGE PREPROCESSING
# =====================================================

def preprocess_mri(image_path):
    """
    Prepares uploaded MRI image for ResNet50 model.

    Required format:
    - RGB image
    - 224 x 224
    - ResNet50 preprocess_input
    """

    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMG_SIZE)

    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)

    image_array = preprocess_input(image_array)

    return image_array


# =====================================================
# 6. RISK LABEL MAPPING
# =====================================================

def get_risk_label(prediction):
    """
    Converts predicted class into user-friendly risk label.
    """

    if prediction == "NonDemented":
        return "Low risk / No dementia indication"

    if prediction == "VeryMildDemented":
        return "Very mild dementia indication"

    if prediction == "MildDemented":
        return "Mild dementia indication"

    if prediction == "ModerateDemented":
        return "Moderate dementia indication"

    return "Unknown risk level"


# =====================================================
# 7. SYMPTOM-BASED PREVENTION ADVICE
# =====================================================

def get_prevention_advice(prediction, symptoms):
    """
    Generates basic prevention/care suggestions based on:
    - selected symptoms
    - predicted dementia class

    This is rule-based, not LLM-based.
    """

    advice = [
        "Consult a neurologist or radiologist for clinical confirmation.",
        "Maintain regular cognitive screening and medical follow-up.",
        "Encourage physical activity, a balanced diet, proper sleep, and mental stimulation.",
        "Monitor changes in memory, language, mood, orientation, and daily functioning."
    ]

    if "Memory loss" in symptoms:
        advice.append(
            "For memory loss: use reminders, calendars, notes, labels, and fixed daily routines."
        )

    if "Disorientation" in symptoms:
        advice.append(
            "For disorientation: keep the environment familiar and use visible clocks, calendars, and signs."
        )

    if "Confusion (time/place)" in symptoms:
        advice.append(
            "For confusion: improve home safety and avoid leaving the patient unattended in unfamiliar areas."
        )

    if "Language difficulty" in symptoms:
        advice.append(
            "For language difficulty: use simple sentences, speech exercises, and caregiver communication support."
        )

    if "Mood changes" in symptoms:
        advice.append(
            "For mood changes: monitor anxiety, depression, agitation, and seek psychological support if needed."
        )

    if "Problem solving decline" in symptoms:
        advice.append(
            "For problem-solving decline: assist with financial tasks, medication schedules, and complex decisions."
        )

    if "Personality change" in symptoms:
        advice.append(
            "For personality changes: maintain calm communication and discuss behavioral changes with a specialist."
        )

    if "Withdrawal / apathy" in symptoms:
        advice.append(
            "For withdrawal or apathy: encourage supervised social interaction, hobbies, and daily activities."
        )

    if prediction in ["MildDemented", "ModerateDemented"]:
        advice.append(
            "Since dementia indication is present, early care planning and regular specialist consultation are recommended."
        )

    return advice


# =====================================================
# 8. HOME ROUTE
# =====================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Alzheimer MRI Detection Backend",
        "status": "running",
        "version": "midterm"
    })


# =====================================================
# 9. HEALTH CHECK ROUTE
# =====================================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "model": "Fine-tuned ResNet50",
        "model_file": "best_model.keras",
        "input_size": "224x224x3",
        "database": "not included in midterm",
        "llm": "handled by another team member"
    })


# =====================================================
# 10. MAIN ANALYSIS ROUTE
# =====================================================

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Main API endpoint used by frontend.

    Expected form-data:
    - mri: image file
    - patient_name
    - dob
    - age
    - sex
    - education
    - family_history
    - referring_doctor
    - scan_date
    - clinical_notes
    - scan_type
    - symptoms
    """

    # -----------------------------
    # 10.1 Validate MRI file
    # -----------------------------

    if "mri" not in request.files:
        return jsonify({
            "success": False,
            "message": "MRI image is required."
        }), 400

    file = request.files["mri"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No MRI file selected."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Invalid file type. Allowed types: jpg, jpeg, png, bmp, tiff."
        }), 400

    # -----------------------------
    # 10.2 Collect frontend form data
    # -----------------------------

    patient_name = request.form.get("patient_name", "").strip()
    dob = request.form.get("dob", "").strip()
    age = request.form.get("age", "").strip()
    sex = request.form.get("sex", "").strip()
    education = request.form.get("education", "").strip()
    family_history = request.form.get("family_history", "").strip()
    referring_doctor = request.form.get("referring_doctor", "").strip()
    scan_date = request.form.get("scan_date", "").strip()
    clinical_notes = request.form.get("clinical_notes", "").strip()
    scan_type = request.form.get("scan_type", "T1").strip()

    symptoms_raw = request.form.get("symptoms", "")
    symptoms = [
        symptom.strip()
        for symptom in symptoms_raw.split(",")
        if symptom.strip()
    ]

    # -----------------------------
    # 10.3 Basic validation
    # -----------------------------

    if not patient_name:
        return jsonify({
            "success": False,
            "message": "Patient name is required."
        }), 400

    if not age or not age.isdigit():
        return jsonify({
            "success": False,
            "message": "Valid patient age is required."
        }), 400

    # -----------------------------
    # 10.4 Save uploaded MRI image
    # -----------------------------

    filename = f"{uuid.uuid4()}_{file.filename}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    file.save(image_path)

    # -----------------------------
    # 10.5 Preprocess image
    # -----------------------------

    image_array = preprocess_mri(image_path)

    # -----------------------------
    # 10.6 Model prediction
    # -----------------------------

    prediction_probs = model.predict(image_array)

    class_index = int(np.argmax(prediction_probs))
    confidence = round(float(np.max(prediction_probs)) * 100, 2)

    prediction = CLASS_NAMES[class_index]

    probabilities = {
        CLASS_NAMES[i]: round(float(prediction_probs[0][i]) * 100, 2)
        for i in range(len(CLASS_NAMES))
    }

    # -----------------------------
    # 10.7 Generate rule-based output
    # -----------------------------

    risk_label = get_risk_label(prediction)
    prevention_advice = get_prevention_advice(prediction, symptoms)

    # -----------------------------
    # 10.8 Final JSON response
    # -----------------------------

    return jsonify({
        "success": True,

        "patient": {
            "name": patient_name,
            "dob": dob,
            "age": age,
            "sex": sex,
            "education": education,
            "family_history": family_history,
            "referring_doctor": referring_doctor,
            "scan_date": scan_date,
            "clinical_notes": clinical_notes,
            "scan_type": scan_type
        },

        "model_result": {
            "prediction": prediction,
            "risk_label": risk_label,
            "confidence": confidence,
            "class_index": class_index,
            "probabilities": probabilities
        },

        "symptoms": symptoms,

        "prevention_advice": prevention_advice,

        "model_info": {
            "model_name": "Fine-tuned ResNet50",
            "model_file": "best_model.keras",
            "input_shape": "224x224x3",
            "preprocessing": "tensorflow.keras.applications.resnet50.preprocess_input"
        },

        "disclaimer": (
            "This result is for research and clinical decision support only. "
            "It is not a medical diagnosis. Please consult a qualified medical professional."
        )
    })


# =====================================================
# 11. RUN SERVER
# =====================================================

if __name__ == "__main__":
    print("[Backend] Server running at http://localhost:5000")
    app.run(debug=True, port=5000)