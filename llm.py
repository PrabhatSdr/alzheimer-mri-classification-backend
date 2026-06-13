import ollama

def explain_result(prediction, confidence):

    prompt = f"""
You are a medical AI assistant.

MRI Result:
- Condition: {prediction}
- Confidence: {confidence}

Give:
1. Simple summary
2. Meaning
3. Next steps
4. Short reassurance
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]