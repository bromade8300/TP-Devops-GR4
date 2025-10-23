from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
import io
import base64
from ultralytics import YOLO
import os
from datetime import datetime
from database import get_db, save_detection_result
from models import DetectionResult
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Detection API", version="1.0.0")

# CORS middleware - Allow all origins for development and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load YOLO model
model = None

def load_model():
    global model
    try:
        # Try to load YOLOv8 nano model
        model = YOLO('yolov8n.pt')
        logger.info("YOLO model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load YOLOv8n model: {e}")
        try:
            # Fallback to YOLOv8s if nano fails
            logger.info("Trying YOLOv8s model as fallback...")
            model = YOLO('yolov8s.pt')
            logger.info("YOLOv8s model loaded successfully")
        except Exception as e2:
            logger.error(f"Failed to load any YOLO model: {e2}")
            # Don't raise exception, let the app start without model
            model = None

@app.on_event("startup")
async def startup_event():
    load_model()
    # Initialize database tables
    try:
        from database import create_tables
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # Don't fail startup if database is not ready yet

@app.get("/")
async def root():
    return {"message": "Image Detection API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    try:
        # Check if model is loaded
        if model is None:
            raise HTTPException(status_code=503, detail="YOLO model is not loaded. Please check server logs.")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Run detection
        results = model(opencv_image)
        
        # Process results
        detections = []
        annotated_image = opencv_image.copy()
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = model.names[class_id]
                    
                    # Only include detections with confidence > 0.5
                    if confidence > 0.5:
                        detections.append({
                            "class": class_name,
                            "confidence": float(confidence),
                            "bbox": [float(x1), float(y1), float(x2), float(y2)]
                        })
                        
                        # Draw bounding box on image
                        cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(annotated_image, f"{class_name}: {confidence:.2f}", 
                                   (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Convert annotated image back to base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Save to database
        detection_result = DetectionResult(
            filename=file.filename,
            detections=detections,
            total_objects=len(detections),
            timestamp=datetime.now()
        )
        
        try:
            save_detection_result(detection_result)
            logger.info(f"Saved detection result for {file.filename}")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            # Continue without failing the request
        
        return {
            "filename": file.filename,
            "detections": detections,
            "total_objects": len(detections),
            "annotated_image": annotated_image_b64,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.get("/detections")
async def get_detections():
    try:
        db = next(get_db())
        results = db.query(DetectionResult).order_by(DetectionResult.timestamp.desc()).limit(50).all()
        return {"detections": [result.to_dict() for result in results]}
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve detections")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

