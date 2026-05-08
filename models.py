from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="USER")
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String(255), unique=True, nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PackingVideo(Base):
    __tablename__ = "packing_videos"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(255), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp_start = Column(DateTime, nullable=True)
    timestamp_end = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True) # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
