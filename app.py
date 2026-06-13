from fastapi import FastAPI, UploadFile, File
import shutil
from pipeline import run_pipeline

app = FastAPI()

@app.get("/")
def home():
    return {"status": "AI backend running"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    path = "temp.jpg"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_pipeline(path)

    return result