from fastapi import FastAPI
from .routers import user, post, auth

app = FastAPI()

# 라우터 등록
app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)