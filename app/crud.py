from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schema
from .utils.security import hash_password

############################ USER ############################
async def get_users(db: AsyncSession, skip:int=0, limit:int=50):
    '''
    모든 사용자 정보 조회(페이징 처리)
    '''
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def get_user(db: AsyncSession, user_id: int):
    '''
    특정 사용자 조회
    '''
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    '''
    회원가입시 동일 이메일 존재 여부를 위한 조회
    '''
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user:schema.UserCreate):
    '''
    신규 사용자 추가
    '''
    hashed_pw = hash_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_pw=hashed_pw,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user: models.User, updated_user: schema.UserCreate):
    '''
    사용자 정보 수정
    '''
    for key, value in updated_user.model_dump().items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user: models.User):
    '''
    사용자 제거
    '''
    db.delete(user)
    await db.commit()

############################ POST ############################
async def get_posts(db: AsyncSession, skip:int=0, limit: int=50):
    '''
    모든 게시물 조회(페이징 처리)
    '''
    result = await db.execute(select(models.Post).offset(skip).limit(limit))
    return result.scalars().all()

async def get_post(db: AsyncSession, post_id: int):
    '''
    특정 게시물 조회
    '''
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    return result.scalars().first()


async def create_user_post(db:AsyncSession, post:schema.PostCreate, user_id : int):
    '''
    특정 사용자의 게시물 생성
    '''
    db_post = models.Post(**post.model_dump(), owner_id=user_id )
    db.add(db_post)

    await db.commit()
    await db.refresh(db_post)
    return db_post

async def update_post(db: AsyncSession, post: models.Post, updated_post: schema.PostCreate):
    '''
    게시물 수정
    '''
    for key, value in updated_post.model_dump().items():
        setattr(post, key, value)
    
    await db.commit()
    await db.refresh(post)
    return post

async def delete_post(db: AsyncSession, post: models.Post):
    '''
    게시물 삭제
    '''
    db.delete(post)
    await db.commit()

############################ AUTH ############################

async def reset_password(db: AsyncSession, user: models.User, new_password: str):
    '''
    비밀번호 변경
    '''
    hashed_pw = hash_password(new_password)
    user.hashed_pw = hashed_pw
    await db.commit()