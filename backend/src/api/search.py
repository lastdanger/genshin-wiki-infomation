"""
统一搜索 API 路由（占位符）

Phase 8 实现统一搜索系统时将完整开发
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/", include_in_schema=False)
async def search_placeholder():
    """统一搜索API占位符 - Phase 8 实现"""
    return {
        "success": False,
        "error": "功能暂未实现",
        "message": "统一搜索系统将在 Phase 8 实现",
        "phase": 8
    }