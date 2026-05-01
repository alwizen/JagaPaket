from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    username: str
    role: str = "PACKING_STAFF"
    device_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    device_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    device_name: str
    location: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    location: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    invoice_number: str
    filename: str
    filepath: str
    device_id: Optional[int] = None
    operator_id: Optional[int] = None
    timestamp_start: Optional[datetime] = None
    timestamp_end: Optional[datetime] = None
    duration: Optional[int] = None

class VideoResponse(VideoBase):
    id: int
    created_at: datetime
    operator_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
