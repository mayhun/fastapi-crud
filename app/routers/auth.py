from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.utils.security import verify_password, create_code
from app.utils.jwt import create_access_token, decode_token
from app.schema import LoginRequest, TokenResponse, EmailRequest, CodeVerifyRequest, PasswordResetRequest
from app.utils.redis_client import r
from app.utils.email import send_email_code
import json
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------
# 로그인 관련
# ---------------------------
@router.post("/login", response_model=TokenResponse, summary="로그인 및 JWT 토큰 발급")
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    token = create_access_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 30,
        path="/"
    )

    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout", summary="로그아웃")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    return {"message": "로그아웃 완료"}

# ---------------------------
# 패스워드 수정
# ---------------------------
@router.post('/passowrd/reset-code', summary='패스워드 변경 인증번호 요청')
def send_reset_code(request: EmailRequest, response: Response):
    
    key = f"reset_code:{request.email}"

    # 기존 인증번호 존재시 삭제
    if r.exists(key):
        r.delete(key)

    code = create_code()    # 인증번호 생성

    data = {
        "code": code,
        "verified": False
    }
    r.setex(key, 300, json.dumps(data)) # redis에 등록 300초(5분) 동안 유지함
    send_email_code(request.email, code)    # 인증번호 메일 전송

    # reset_token 발급
    reset_token = create_access_token(
        data={"sub": request.email, "purpose": "verify_code"},
        expires_delta=timedelta(minutes=5)
    )

    response.set_cookie(
        key="reset_token",
        value=reset_token,
        httponly=True,
        secure=False,
        max_age=300,
        path="/",
        samesite="strict"
    )

    return {"message": "인증번호가 이메일로 전송되었습니다."}

@router.post("/password/verify-code", summary='인증번호 검증')
def verify_code(request: CodeVerifyRequest, response:Response, reset_token: str = Cookie(...)):

    # reset_token 디코딩 → 이메일 추출
    payload = decode_token(reset_token)
    if payload.get("purpose") != "verify_code":
        raise HTTPException(status_code=403, detail="인증번호 검증용 토큰이 아닙니다.")
    
    email = payload.get("sub")
    key = f"reset_code:{email}"
    value = r.get(key)

    if not value:
        raise HTTPException(status_code=400, detail="인증번호가 만료되었거나 존재하지 않습니다.")

    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="저장된 인증 데이터 오류")

    if data.get("code") != request.code:
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않습니다.")

    # 인증 완료 → Redis 상태 갱신
    r.setex(key, 300, json.dumps({"code": request.code, "verified": True}))

    # change_token 발급 (비밀번호 재설정 전용)
    change_token = create_access_token(
        data={"sub": email, "purpose": "reset_password"},
        expires_delta=timedelta(minutes=5)
    )

    # 쿠키 설정 (기존 reset_token 삭제 → change_token 설정)
    response.delete_cookie("reset_token")
    response.set_cookie(
        key="change_token",
        value=change_token,
        httponly=True,
        secure=False,
        max_age=300,
        path="/",
        samesite="strict"
    )

    return {"message": "인증번호 확인 완료. 비밀번호 변경 가능"}


@router.post("/password/reset", summary="비밀번호 변경")
def reset_password(request: PasswordResetRequest, response: Response, change_token: str = Cookie(...), db: Session = Depends(get_db)):

    payload = decode_token(change_token)

    if payload.get("purpose") != "reset_password":
        raise HTTPException(status_code=403, detail="비밀번호 변경 토큰이 아닙니다.")
    
    email = payload.get('sub')

    key = f"reset_code:{email}"
    value = r.get(key)

    if not value:
        raise HTTPException(status_code=400, detail="인증이 완료되지 않았습니다.")

    data = json.loads(value)

    if not data.get("verified"):
        raise HTTPException(status_code=403, detail="이메일 인증을 완료해주세요.")

    # 사용자 조회
    user = crud.get_user_by_email(db, email)
    
    # 비밀번호 변경
    crud.reset_password(db=db, user=user, new_password=request.new_password)
    
    # 인증번호 및 토큰 제거
    r.delete(key)
    response.delete_cookie("change_token")

    return {"message": "비밀번호가 변경되었습니다."}
