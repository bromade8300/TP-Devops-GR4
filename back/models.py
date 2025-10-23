from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DetectionResult(Base):
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    detections = Column(JSON, nullable=False)  # Store detection results as JSON
    total_objects = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "detections": self.detections,
            "total_objects": self.total_objects,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
