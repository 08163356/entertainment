from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import rooms, matches, players, websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理

app = FastAPI(
    title="Entertainment API",
    description="娱乐工具集后端 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(websocket.router, tags=["websocket"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
