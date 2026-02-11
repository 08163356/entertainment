from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import rooms, matches, players, websocket
from app.routers import basketball_rooms, basketball_matches, basketball_practices, basketball_websocket

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

# 台球路由
app.include_router(rooms.router, prefix="/api/rooms", tags=["billiards-rooms"])
app.include_router(matches.router, prefix="/api/matches", tags=["billiards-matches"])
app.include_router(players.router, prefix="/api/players", tags=["billiards-players"])
app.include_router(websocket.router, tags=["billiards-websocket"])

# 投篮路由
app.include_router(basketball_rooms.router, prefix="/api/basketball/rooms", tags=["basketball-rooms"])
app.include_router(basketball_matches.router, prefix="/api/basketball/matches", tags=["basketball-matches"])
app.include_router(basketball_practices.router, prefix="/api/basketball/practices", tags=["basketball-practices"])
app.include_router(basketball_websocket.router, tags=["basketball-websocket"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
