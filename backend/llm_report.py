import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"


def fallback_report(prediction, confidence, error=None):
    return {
        "doctor_summary": (
            f"The ResNet50 model predicted {prediction} with {confidence}% confidence. "
            "This should be clinically confirmed by a neurologist or radiologist."
        ),
        "patient_explanation": (
            "The AI system analyzed the MRI scan and produced a support result. "
            "This is not a final medical diagnosis."
        ),
        "recommendations": [
            "Consult a neurologist or radiologist for confirmation.",
            "Compare the result with clinical history and cognitive tests.",
            "Continue monitoring memory, mood, language, and daily functioning."
        ],
        "disclaimer": "This AI-generated explanation is for clinical decision support only.",
        "llm_status": "fallback",
        "error": error
    }


def generate_llm_report(prediction, confidence, probabilities, symptoms, age, sex):
    symptoms_text = ", ".join(symptoms) if symptoms else "No symptoms reported"

    prompt = f"""
You are an AI assistant for an Alzheimer's MRI detection research system.

Return ONLY valid JSON. Do not use markdown.

Patient details:
Age: {age}
Sex: {sex}
Reported symptoms: {symptoms_text}

AI model result:
Model: Fine-tuned ResNet50
Prediction: {prediction}
Confidence: {confidence}%
Class probabilities: {probabilities}

Rules:
- Do not give a final medical diagnosis.
- Explain the AI result in simple language.
- Mention that a neurologist or radiologist must confirm the result.
- Keep the response professional and concise.

Return this exact JSON structure:
{{
  "doctor_summary": "...",
  "patient_explanation": "...",
  "recommendations": ["...", "...", "..."],
  "disclaimer": "..."
}}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            },
            timeout=90
        )

        response.raise_for_status()

        content = response.json()["message"]["content"].strip()

        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            return fallback_report(prediction, confidence, "LLM did not return valid JSON.")

        report = json.loads(content[start:end])
        report["llm_status"] = "generated"
        report["llm_model"] = OLLAMA_MODEL

        return report

    except Exception as e:
        return fallback_report(prediction, confidence, str(e))