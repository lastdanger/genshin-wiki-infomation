"""
图片管理 API 路由（占位符）

Phase 7 实现图片系统时将完整开发
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/", include_in_schema=False)
async def images_placeholder():
    """图片API占位符 - Phase 7 实现"""
    return {
        "success": False,
        "error": "功能暂未实现",
        "message": "图片系统将在 Phase 7 实现",
        "phase": 7
    }