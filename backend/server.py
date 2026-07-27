import os
import uuid
import numpy as np
from PIL import Image

import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from gradcam import generate_gradcam
from llm_report import generate_llm_report


# =====================================================
# 1. BASIC CONFIGURATION
# =====================================================

MODEL_PATH = "models/best_model.keras"
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

IMG_SIZE = (224, 224)

CLASS_NAMES = [
    "MildDemented",
    "ModerateDemented",
    "NonDemented",
    "VeryMildDemented"
]

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "tiff"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================================
# 2. FLASK APP SETUP
# =====================================================

app = Flask(__name__)
CORS(app)


# =====================================================
# 3. LOAD TRAINED MODEL
# =====================================================

print("[Backend] Loading fine-tuned ResNet50 model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("[Backend] Model loaded successfully.")


# =====================================================
# 4. HELPER FUNCTIONS
# =====================================================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def preprocess_mri(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMG_SIZE)

    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array = preprocess_input(image_array)

    return image_array


def get_risk_label(prediction):
    risk_map = {
        "NonDemented": "Low risk / No dementia indication",
        "VeryMildDemented": "Very mild dementia indication",
        "MildDemented": "Mild dementia indication",
        "ModerateDemented": "Moderate dementia indication"
    }

    return risk_map.get(prediction, "Unknown risk level")


def get_prevention_advice(prediction, symptoms):
    advice = [
        "Consult a neurologist or radiologist for clinical confirmation.",
        "Maintain regular cognitive screening and medical follow-up.",
        "Encourage physical activity, a balanced diet, proper sleep, and mental stimulation.",
        "Monitor changes in memory, language, mood, orientation, and daily functioning."
    ]

    symptom_advice = {
        "Memory loss": "For memory loss: use reminders, calendars, notes, labels, and fixed daily routines.",
        "Disorientation": "For disorientation: keep the environment familiar and use visible clocks, calendars, and signs.",
        "Confusion (time/place)": "For confusion: improve home safety and avoid leaving the patient unattended in unfamiliar areas.",
        "Language difficulty": "For language difficulty: use simple sentences, speech exercises, and caregiver communication support.",
        "Mood changes": "For mood changes: monitor anxiety, depression, agitation, and seek psychological support if needed.",
        "Problem solving decline": "For problem-solving decline: assist with financial tasks, medication schedules, and complex decisions.",
        "Personality change": "For personality changes: maintain calm communication and discuss behavioral changes with a specialist.",
        "Withdrawal / apathy": "For withdrawal or apathy: encourage supervised social interaction, hobbies, and daily activities."
    }

    for symptom in symptoms:
        if symptom in symptom_advice:
            advice.append(symptom_advice[symptom])

    if prediction in ["MildDemented", "ModerateDemented"]:
        advice.append(
            "Since dementia indication is present, early care planning and regular specialist consultation are recommended."
        )

    return advice


# =====================================================
# 5. ROUTES
# =====================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Alzheimer MRI Detection Backend",
        "status": "running",
        "model": "Fine-tuned ResNet50",
        "llm": "llama3.2:3b via Ollama"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "model": "Fine-tuned ResNet50",
        "model_file": "best_model.keras",
        "input_size": "224x224x3",
        "gradcam": "enabled",
        "llm": "llama3.2:3b via Ollama"
    })


@app.route("/outputs/<filename>", methods=["GET"])
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
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
        # Save uploaded MRI
        # -----------------------------
        filename = f"{uuid.uuid4()}_{file.filename}"
        image_path = os.path.join(UPLOAD_DIR, filename)
        file.save(image_path)

        # -----------------------------
        # Model Prediction
        # -----------------------------
        image_array = preprocess_mri(image_path)
        prediction_probs = model.predict(image_array)

        class_index = int(np.argmax(prediction_probs))
        confidence = round(float(np.max(prediction_probs)) * 100, 2)
        prediction = CLASS_NAMES[class_index]

        probabilities = {
            CLASS_NAMES[i]: round(float(prediction_probs[0][i]) * 100, 2)
            for i in range(len(CLASS_NAMES))
        }

        risk_label = get_risk_label(prediction)
        prevention_advice = get_prevention_advice(prediction, symptoms)

        # -----------------------------
        # Grad-CAM
        # -----------------------------
        gradcam_filename = f"gradcam_{filename}.jpg"
        gradcam_path = os.path.join(OUTPUT_DIR, gradcam_filename)

        generate_gradcam(
            model=model,
            image_array=image_array,
            original_image_path=image_path,
            class_index=class_index,
            output_path=gradcam_path
        )

        gradcam_url = f"http://localhost:5000/outputs/{gradcam_filename}"

        # -----------------------------
        # LLM Report using Ollama
        # -----------------------------
        llm_report = generate_llm_report(
            prediction=prediction,
            confidence=confidence,
            probabilities=probabilities,
            symptoms=symptoms,
            age=age,
            sex=sex
        )

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
            "llm_report": llm_report,

            "gradcam": {
                "enabled": True,
                "image_url": gradcam_url
            },

            "model_info": {
                "model_name": "Fine-tuned ResNet50",
                "model_file": "best_model.keras",
                "input_shape": "224x224x3",
                "preprocessing": "tensorflow.keras.applications.resnet50.preprocess_input",
                "explainability": "Grad-CAM",
                "llm_model": "llama3.2:3b via Ollama"
            },

            "disclaimer": (
                "This result is for research and clinical decision support only. "
                "It is not a medical diagnosis. Please consult a qualified medical professional."
            )
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error during analysis.",
            "error": str(e)
        }), 500


# =====================================================
# 6. RUN SERVER
# =====================================================

if __name__ == "__main__":
    print("[Backend] Server running at http://localhost:5000")
    app.run(debug=True, port=5000)