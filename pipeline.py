from model import predict_mri
from llm import explain_result

def run_pipeline(image_path):

    # 1. CNN prediction
    result = predict_mri(image_path)

    prediction = result["prediction"]
    confidence = result["confidence"]

    # 2. LLM explanation
    explanation = explain_result(prediction, confidence)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "explanation": explanation
    }


# TEST FULL SYSTEM
if __name__ == "__main__":
    output = run_pipeline("test.jpg")
    print(output)