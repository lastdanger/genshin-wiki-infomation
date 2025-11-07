"""
游戏机制 API 路由（占位符）

Phase 5 实现游戏机制系统时将完整开发
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/", include_in_schema=False)
async def game_mechanics_placeholder():
    """游戏机制API占位符 - Phase 5 实现"""
    return {
        "success": False,
        "error": "功能暂未实现",
        "message": "游戏机制系统将在 Phase 5 实现",
        "phase": 5
    }