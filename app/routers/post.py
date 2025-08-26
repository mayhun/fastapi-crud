from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schema
from ..database import get_db

router = APIRouter(prefix="/post", tags=["post"])

@router.get("", response_model=list[schema.Post], summary="모든 게시글 목록 조회")
async def get_posts(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await crud.get_posts(db, skip=skip, limit=limit)


@router.post("/{user_id}", response_model=schema.Post, summary="특정 사용자의 게시글 생성")
async def post_post_for_user(user_id: int, post: schema.PostCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user_post(db=db, user_id=user_id, post=post)

@router.put("/{post_id}", response_model=schema.Post, summary="기존 게시글 수정")
async def update_post(post_id: int, updated_post: schema.PostCreate, db: AsyncSession = Depends(get_db)):
    db_post = await crud.get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return await crud.update_post(db, db_post, updated_post)

@router.delete("/{post_id}", summary="게시글 삭제")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    db_post = await crud.get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await crud.delete_post(db, db_post)
    return {"message": "Post deleted successfully"}