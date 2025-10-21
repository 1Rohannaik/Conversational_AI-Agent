from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base
from datetime import datetime

class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    cloud_url = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)  # optional, if linked to a user
