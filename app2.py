# from fastapi import FastAPI, UploadFile, File
# from typing import List
# import cv2
# import numpy as np
# import base64
# import torch
# from ultralytics import YOLO

# app = FastAPI()

# # Load Model once on startup
# MODEL_PATH = "best.pt" 
# device = "cuda" if torch.cuda.is_available() else "cpu"
# model = YOLO(MODEL_PATH).to(device)

# @app.post("/infer_batch")
# async def infer_batch(files: List[UploadFile] = File(...)):
#     frames = []
    
#     # 1. Decode all incoming images
#     for file in files:
#         data = await file.read()
#         img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
#         if img is not None:
#             frames.append(img)

#     if not frames:
#         return {"frames": [], "msg": "No frames received"}

#     # 2. Batch Inference (passing the whole list is faster)
#     results = model.predict(source=frames, conf=0.4, device=device, verbose=False)

#     # 3. Annotate and Encode
#     processed_b64 = []
#     for r in results:
#         annotated_img = r.plot() 
#         _, buffer = cv2.imencode(".jpg", annotated_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
#         img_str = base64.b64encode(buffer).decode("utf-8")
#         processed_b64.append(img_str)

#     return {"frames": processed_b64}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, UploadFile, File
from typing import List
import cv2
import numpy as np
import base64
import torch
from ultralytics import YOLO

app = FastAPI()

# Load Model once on startup
MODEL_PATH = "best.pt" 
device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO(MODEL_PATH).to(device)

@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "MudraAI Backend is running"}

@app.post("/infer_batch")
async def infer_batch(files: List[UploadFile] = File(...)):
    frames = []
    
    # 1. Decode all incoming images
    for file in files:
        data = await file.read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            frames.append(img)

    if not frames:
        return {"frames": [], "msg": "No frames received"}

    # 2. Batch Inference (passing the whole list is faster)
    results = model.predict(source=frames, conf=0.4, device=device, verbose=False)

    # 3. Annotate and Encode
    processed_b64 = []
    for r in results:
        annotated_img = r.plot() 
        _, buffer = cv2.imencode(".jpg", annotated_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        img_str = base64.b64encode(buffer).decode("utf-8")
        processed_b64.append(img_str)

    return {"frames": processed_b64}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)