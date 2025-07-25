from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from typing import Optional
import re

# ---------------------------
# 게시글 관련 스키마
# ---------------------------

class PostBase(BaseModel):
    title: str
    description: Optional[str] = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# 사용자 관련 스키마
# ---------------------------

class UserBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "홍길동"})
    email: EmailStr = Field(
        ..., 
        title="이메일", 
        description="유효한 이메일 형식", 
        json_schema_extra={"example": "hong@naver.com"}
    )

class UserCreate(UserBase):
    password: str = Field(
        ..., 
        title="비밀번호", 
        description="8~128자, 공백 없음", 
        min_length=8, 
        max_length=128, 
        json_schema_extra={"example": "securePass123!"}
    )

class User(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# 인증 관련 스키마
# ---------------------------

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "hong@naver.com"})
    password: str = Field(..., min_length=8, json_schema_extra={"example": "securePass123!"})

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmailRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "hong@naver.com"})

class CodeVerifyRequest(BaseModel):
    code: str

class PasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=100, json_schema_extra={"example":"securePass123!"})

    @validator("new_password")
    def password_comlexity(cls, v):
        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=-]).{8,}$", v):
            raise ValueError("비밀번호는 영문, 숫자, 특수문자를 포함해야합니다.")
        return v