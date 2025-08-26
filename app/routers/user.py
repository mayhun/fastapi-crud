from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schema
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[schema.User],summary="모든 사용자 정보 조회")
async def get_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schema.User, summary="특정 사용자 정보 조회")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user =  await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("", response_model=schema.User, summary="회원가입")
async def post_user(user: schema.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user =  await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db, user=user)

@router.put("/{user_id}", response_model=schema.User, summary="기존 사용자 정보 수정")
async def update_user(user_id: int, updated_user: schema.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user =  await crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.update_user(db, db_user, updated_user)

@router.delete("/{user_id}", summary="사용자 삭제")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user =  await crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await crud.delete_user(db, db_user)
    return {"message": "User deleted successfully"}