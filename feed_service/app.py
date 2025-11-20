import os, random, json
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
import requests

AI_URL = "http://ai_service:8000/predict"
IMAGES_DIR = "/images"
SHARED_DIR = "/shared"

app = FastAPI()

@app.post("/trigger")
def trigger():
    try:
        # Pick a random image
        files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(("jpg","jpeg","png"))]
        if not files:
            return {"error": "No images found."}

        chosen = random.choice(files)
        with open(f"{IMAGES_DIR}/{chosen}", "rb") as f:
            resp = requests.post(AI_URL, files={"image": (chosen, f)})

        if resp.status_code != 200:
            return resp.json()

        result = resp.json()

        # Save latest artifacts
        image = Image.open(f"{IMAGES_DIR}/{chosen}")
        # Convert to RGB if image has transparency (RGBA, LA) or is palette mode
        # JPEG format doesn't support transparency
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(f"{SHARED_DIR}/latest.jpg")

        with open(f"{SHARED_DIR}/latest.json", "w") as jf:
            json.dump(result, jf)

        return {"status": "ok", "result": result}

    except Exception as e:
        return {"error": str(e)}

@app.get("/latest")
def latest():
    try:
        with open(f"{SHARED_DIR}/latest.json") as f:
            return json.load(f)
    except:
        return {"error": "No results available."}

@app.get("/image/latest")
def latest_image():
    path = f"{SHARED_DIR}/latest.jpg"
    if not os.path.exists(path):
        return {"error": "No image available."}
    return FileResponse(path, media_type="image/jpeg")
