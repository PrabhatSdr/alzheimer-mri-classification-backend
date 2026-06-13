#  MRI Alzheimer Detection + LLM Explanation System

This project is an AI-based medical assistant that analyzes MRI images and generates structured explanations using a Large Language Model (LLM).

---

#  Project Overview

The system works in 3 main steps:

1. MRI image is uploaded via FastAPI backend  
2. CNN model predicts condition (Alzheimer / MCI / Normal)  
3. LLM (Ollama - LLaMA 3) generates a human-readable medical explanation  

---

#  System Architecture

MRI Image  
↓  
CNN Model (Prediction)  
↓  
FastAPI Backend  
↓  
LLM (Ollama - LLaMA 3)  
↓  
Final Medical Report  

---

#  Project Structure

mri-ai/
│
├── app.py              # FastAPI backend
├── model.py            # CNN model (dummy or trained)
├── llm.py              # LLM explanation logic
├── pipeline.py        # Full integration pipeline
├── create_image.py    # Sample image generator
├── test_model.py      # Model testing
├── test_llm.py        # LLM testing
├── README.md

---

#  Installation

## 1. Install dependencies

```bash
pip install fastapi uvicorn python-multipart torch torchvision pillow ollama transformers