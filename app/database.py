from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_USER")    
passwd = os.getenv("DB_PASSWD")
host = os.getenv("DB_HOST")    
port = os.getenv("DB_PORT")    
db = os.getenv("DB_NAME")      

# asyncmy, aiomysql 둘 중 asyncmy가 빠르다고 하여 선택
DB_URL = f'mysql+asyncmy://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

# Async Engine 생성
engine = create_async_engine(DB_URL, echo=True, future=True)

# Async 세센팩토리
SessionLocal = async_sessionmaker(
    bind=engine,              # DB 연결 엔진
    class_=AsyncSession,      # 비동기 세션 클래스 사용
    autoflush=False,          # 자동 flush 비활성화 (직접 commit/flush)
    autocommit=False,         # 자동 commit 비활성화 (명시적 commit 필요)
    expire_on_commit=False    # commit 후에도 ORM 객체를 만료시키지 않음 (재사용 가능)
)

# Base 모델
Base = declarative_base()

# Dependency Injection 
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session