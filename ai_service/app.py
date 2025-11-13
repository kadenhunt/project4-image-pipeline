from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import io, torch
import torchvision.transforms as T
from torchvision.models import resnet18, ResNet18_Weights

app = FastAPI(title="AI Classification Service")

# Load model + weights
weights = ResNet18_Weights.DEFAULT
model = resnet18(weights=weights)
model.eval()
labels = weights.meta["categories"]

# Preprocessing
preprocess = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=weights.meta["mean"], std=weights.meta["std"])
])

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    # Validate file
    try:
        content = await image.read()
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or corrupted image."}
        )

    # Preprocess
    x = preprocess(img).unsqueeze(0)

    # Inference
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]
        conf, idx = torch.max(probs, 0)

    return {
        "class": labels[idx.item()],
        "confidence": round(conf.item(), 4)
    }
