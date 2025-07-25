from sqlalchemy.orm import Session
from . import models, schema
from .utils.security import hash_password

############################ USER ############################
def get_users(db: Session, skip:int=0, limit:int=50):
    '''
    모든 사용자 정보 조회(페이징 처리)
    '''
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    '''
    특정 사용자 조회
    '''
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    '''
    회원가입시 동일 이메일 존재 여부를 위한 조회
    '''
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user:schema.UserCreate):
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
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: models.User, updated_user: schema.UserCreate):
    '''
    사용자 정보 수정
    '''
    for key, value in updated_user.model_dump().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: models.User):
    '''
    사용자 제거
    '''
    db.delete(user)
    db.commit()

############################ POST ############################
def get_posts(db: Session, skip:int=0, limit: int=50):
    '''
    모든 게시물 조회(페이징 처리)
    '''
    return db.query(models.Post).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    '''
    특정 게시물 조회
    '''
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def create_user_post(db:Session, post:schema.PostCreate, user_id : int):
    '''
    특정 사용자의 게시물 생성
    '''
    db_post = models.Post(**post.model_dump(), owner_id=user_id )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_post(db: Session, post: models.Post, updated_post: schema.PostCreate):
    '''
    게시물 수정
    '''
    for key, value in updated_post.model_dump().items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post: models.Post):
    '''
    게시물 삭제
    '''
    db.delete(post)
    db.commit()

############################ AUTH ############################

def reset_password(db: Session, user: models.User, new_password: str):
    '''
    비밀번호 변경
    '''
    hashed_pw = hash_password(new_password)
    user.hashed_pw = hashed_pw
    db.commit()