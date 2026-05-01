from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database import get_db
from models import User
from schemas import UserResponse, UserCreate, UserUpdate
from security import get_password_hash
from dependencies import require_super_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")
        
    db_user = User(
        name=user.name,
        username=user.username,
        password_hash=get_password_hash(user.password),
        role=user.role,
        device_id=user.device_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.username is not None:
        if user_update.username != db_user.username:
            check_u = await db.execute(select(User).where(User.username == user_update.username))
            if check_u.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already taken")
        db_user.username = user_update.username
        
    if user_update.password is not None and user_update.password != "":
        db_user.password_hash = get_password_hash(user_update.password)
        
    if user_update.role is not None:
        db_user.role = user_update.role
    if user_update.device_id is not None:
        db_user.device_id = user_update.device_id if user_update.device_id != 0 else None
        
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_super_admin)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own active account")
        
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.delete(db_user)
    await db.commit()
    return {"detail": "User deleted successfully"}
