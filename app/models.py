from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    email = mapped_column(String(255), unique=True, nullable=False)
    posts = relationship("Post",back_populates="owner", cascade='delete')
    hashed_pw = mapped_column(String(255), nullable=False)
    is_active = mapped_column(Boolean,default=False)

class Post(Base):
    __tablename__ = "posts"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    title = mapped_column(String(255), nullable=False)
    description = mapped_column(String(255))
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    owner = relationship("User",back_populates="posts")