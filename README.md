# 🚀 FastAPI User & Post Management API

FastAPI 기반의 사용자(User) 및 게시글(Post) CRUD API 프로젝트입니다.  
JWT 인증을 통한 로그인/로그아웃 기능과 비동기 SQLAlchemy 기반 데이터베이스 연동이 포함되어 있습니다.

---

## 📦 프로젝트 구조

```text
.
├── app/
│   ├── routers/               # 라우터 정의 디렉토리
│   │   ├── auth.py            # 로그인, 로그아웃 등 인증 관련 API 라우터
│   │   ├── user.py            # 사용자 CRUD 관련 API 라우터
│   │   └── post.py            # 게시글 CRUD 관련 API 라우터
│   ├── templates/                          # 템플릿
│   │   └── email_verification.html         # 인증번호 메일 템플릿
│   ├── utils/                              # 유틸리티 모듈 디렉토리
│   │   ├── email.py                        # 이메일 발송을 위한 SMTP 설정
│   │   ├── jwt.py                          # JWT 토큰 생성 및 검증 함수
│   │   ├── redis_client.py                 # Redis 설정
│   │   └── security.py                     # 비밀번호 해싱/검증 등의 보안 유틸리티
│   ├── crud.py                             # 데이터베이스 CRUD 로직 정의
│   ├── database.py                         # DB 연결 및 세션 설정
│   ├── main.py                
│   ├── models.py              # SQLAlchemy ORM 모델 정의
│   └── schema.py              # Pydantic을 이용한 데이터 검증 스키마 정의
├── Dockerfile                 # 애플리케이션 Docker 컨테이너화 설정 파일
├── docker-compose.yml         # 데이터베이스 등 의존 서비스 포함 Docker Compose 설정
├── .env                       # 환경 변수 설정 파일 (DB 정보, 시크릿 키 등)
├── requirements.txt           # Python 패키지 의존성 목록
└── README.md                  # 프로젝트 설명 문서
```

## 🔐 env 파일 작성 예시

```text
DB_USER='DB_USER'
DB_PASSWD='DB_PASSWD'
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fastapi_crud

SECRET_KEY=SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

EMAIL_USER=test@gmail.com
EMAIL_PASS='16자리 pass 번호'

REDIS_HOST=redis
REDIS_PORT=6379
```
## 📌 실행 방법
### Docker로 실행
```bash
docker-compose up --build
```
### 로컬에서 실행
```bash
uvicorn app.utils.main:app --reload
```  