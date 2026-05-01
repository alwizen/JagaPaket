from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database import get_db
from models import Device, User
from schemas import DeviceResponse, DeviceCreate, DeviceUpdate
from dependencies import require_super_admin

router = APIRouter(prefix="/devices", tags=["devices"])

@router.get("/", response_model=List[DeviceResponse])
async def read_devices(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    stmt = select(Device).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=DeviceResponse)
async def create_device(device: DeviceCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    db_device = Device(
        device_name=device.device_name,
        location=device.location
    )
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return db_device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: int, device_update: DeviceUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    stmt = select(Device).where(Device.id == device_id)
    result = await db.execute(stmt)
    db_device = result.scalar_one_or_none()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    if device_update.device_name is not None:
        db_device.device_name = device_update.device_name
    if device_update.location is not None:
        db_device.location = device_update.location
        
    await db.commit()
    await db.refresh(db_device)
    return db_device

@router.delete("/{device_id}")
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    stmt = select(Device).where(Device.id == device_id)
    result = await db.execute(stmt)
    db_device = result.scalar_one_or_none()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    await db.delete(db_device)
    await db.commit()
    return {"detail": "Device deleted successfully"}
