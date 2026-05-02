import os
import aiofiles
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List
from config import settings
from database import get_db
from models import PackingVideo, User
from schemas import VideoResponse
from dependencies import require_super_admin, require_packing_staff, get_current_user

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    invoice_number: str = Form(...),
    device_id: int = Form(0),
    timestamp_start: str = Form(None),
    duration: int = Form(0),
    video: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_packing_staff)
):
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    storage_dir = os.path.join(settings.VIDEO_STORAGE_PATH, date_str)
    
    os.makedirs(storage_dir, exist_ok=True)
    
    filename = f"{invoice_number}.mp4"
    filepath = os.path.join(storage_dir, filename)
    
    # Handle filename collision
    counter = 1
    base_name = invoice_number
    while os.path.exists(filepath):
        filename = f"{base_name}_{counter}.mp4"
        filepath = os.path.join(storage_dir, filename)
        counter += 1

    async with aiofiles.open(filepath, 'wb') as out_file:
        content = await video.read()
        await out_file.write(content)
        
    start_time = None
    if timestamp_start:
        try:
            start_time = datetime.fromisoformat(timestamp_start.replace('Z', '+00:00'))
        except ValueError:
            start_time = datetime.utcnow()
    else:
        start_time = datetime.utcnow()
        
    dev_id = device_id if device_id != 0 else current_user.device_id
    
    new_video = PackingVideo(
        invoice_number=invoice_number,
        filename=filename,
        filepath=filepath,
        device_id=dev_id,
        operator_id=current_user.id,
        timestamp_start=start_time,
        timestamp_end=datetime.utcnow(),
        duration=duration
    )
    
    db.add(new_video)
    await db.commit()
    await db.refresh(new_video)
    
    return new_video

@router.get("/stats")
async def get_video_stats(db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()
    # Handle simple truncation to start of day
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    r_today = await db.execute(select(func.count(PackingVideo.id)).where(PackingVideo.created_at >= today_start))
    r_week = await db.execute(select(func.count(PackingVideo.id)).where(PackingVideo.created_at >= week_start))
    r_month = await db.execute(select(func.count(PackingVideo.id)).where(PackingVideo.created_at >= month_start))
    r_total = await db.execute(select(func.count(PackingVideo.id)))
    
    return {
        "today": r_today.scalar() or 0,
        "week": r_week.scalar() or 0,
        "month": r_month.scalar() or 0,
        "total": r_total.scalar() or 0
    }

@router.get("/")
async def list_videos(
    invoice_number: str = None,
    operator_id: int = None,
    date_from: str = None,
    date_to: str = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * limit
    
    stmt = select(PackingVideo, User.name.label('operator_name')).outerjoin(User, PackingVideo.operator_id == User.id)
    count_stmt = select(func.count(PackingVideo.id))
    
    if current_user.role == "PACKING_STAFF":
        stmt = stmt.where(PackingVideo.operator_id == current_user.id)
        count_stmt = count_stmt.where(PackingVideo.operator_id == current_user.id)
    else:
        if operator_id:
            stmt = stmt.where(PackingVideo.operator_id == operator_id)
            count_stmt = count_stmt.where(PackingVideo.operator_id == operator_id)
            
    if invoice_number:
        stmt = stmt.where(PackingVideo.invoice_number.ilike(f"%{invoice_number}%"))
        count_stmt = count_stmt.where(PackingVideo.invoice_number.ilike(f"%{invoice_number}%"))

    if date_from:
        from datetime import datetime
        dt_from = datetime.strptime(date_from, "%Y-%m-%d")
        stmt = stmt.where(PackingVideo.created_at >= dt_from)
        count_stmt = count_stmt.where(PackingVideo.created_at >= dt_from)

    if date_to:
        from datetime import datetime, timedelta
        dt_to = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
        stmt = stmt.where(PackingVideo.created_at < dt_to)
        count_stmt = count_stmt.where(PackingVideo.created_at < dt_to)
        
    stmt = stmt.order_by(PackingVideo.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    response_data = []
    for video, op_name in rows:
        v_dict = {
            "id": video.id,
            "invoice_number": video.invoice_number,
            "filename": video.filename,
            "filepath": video.filepath,
            "device_id": video.device_id,
            "operator_id": video.operator_id,
            "operator_name": op_name or "Unknown",
            "timestamp_start": video.timestamp_start,
            "timestamp_end": video.timestamp_end,
            "duration": video.duration,
            "created_at": video.created_at
        }
        response_data.append(v_dict)
        
    return {
        "data": response_data,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/play/{video_id}")
async def play_video(video_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(PackingVideo).where(PackingVideo.id == video_id)
    if current_user.role == "PACKING_STAFF":
        stmt = stmt.where(PackingVideo.operator_id == current_user.id)
        
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if not os.path.exists(video.filepath):
        raise HTTPException(status_code=404, detail="Video file is missing on disk")
        
    return FileResponse(path=video.filepath, media_type="video/mp4", filename=video.filename)

@router.delete("/{video_id}")
async def delete_video(video_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    stmt = select(PackingVideo).where(PackingVideo.id == video_id)
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    # Delete real file
    if os.path.exists(video.filepath):
        try:
            os.remove(video.filepath)
        except OSError:
            pass 
            
    await db.delete(video)
    await db.commit()
    return {"detail": "Video deleted successfully"}
