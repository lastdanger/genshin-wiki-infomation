"""
应用配置管理

使用 Pydantic Settings 管理环境变量和应用配置
"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """应用配置类"""

    # 基础应用配置
    app_name: str = Field(default="原神游戏信息网站", description="应用名称")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=True, description="调试模式")
    version: str = Field(default="1.0.0", description="应用版本")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8000, description="服务器端口")

    # 数据库配置
    database_url: str = Field(
        default="postgresql+asyncpg://genshin_user:genshin_password@localhost:5432/genshin_wiki",
        description="数据库连接URL"
    )
    database_pool_size: int = Field(default=20, description="数据库连接池大小")
    database_max_overflow: int = Field(default=30, description="数据库最大溢出连接数")

    # Redis配置
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis连接URL"
    )
    redis_cache_ttl: int = Field(default=3600, description="Redis缓存过期时间（秒）")

    # Celery配置
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery消息代理URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Celery结果存储URL"
    )

    # API配置
    api_v1_prefix: str = Field(default="/api", description="API v1路径前缀")
    max_page_size: int = Field(default=100, description="分页最大条数")
    default_page_size: int = Field(default=50, description="分页默认条数")

    # 安全配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="应用密钥"
    )
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")
    algorithm: str = Field(default="HS256", description="JWT加密算法")

    # CORS配置
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="允许的跨域来源"
    )

    # 文件上传配置
    upload_dir: str = Field(default="uploads", description="文件上传目录")
    max_upload_size: int = Field(default=10 * 1024 * 1024, description="最大上传文件大小（字节）")
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
        description="允许的图片类型"
    )

    # 外部API配置
    genshin_api_base_url: str = Field(
        default="https://genshin.jmp.blue",
        description="Genshin.dev API基础URL"
    )
    genshin_api_timeout: int = Field(default=10, description="Genshin API请求超时时间（秒）")

    # 爬虫配置
    scraper_user_agent: str = Field(
        default="Genshin-Info-Bot/1.0 (+https://genshin-info.com)",
        description="爬虫用户代理"
    )
    scraper_delay: float = Field(default=1.0, description="爬虫请求间隔（秒）")
    scraper_timeout: int = Field(default=15, description="爬虫请求超时时间（秒）")

    # 数据同步配置
    sync_interval_hours: int = Field(default=6, description="数据同步间隔（小时）")
    sync_retry_attempts: int = Field(default=3, description="同步重试次数")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    log_rotation: str = Field(default="1 day", description="日志轮转配置")
    log_retention: str = Field(default="30 days", description="日志保留时间")

    # 监控配置
    enable_metrics: bool = Field(default=True, description="启用性能指标")
    metrics_port: int = Field(default=8001, description="指标服务端口")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment.lower() in ("test", "testing")

    def get_database_url(self, async_driver: bool = True) -> str:
        """
        获取数据库连接URL

        Args:
            async_driver: 是否使用异步驱动

        Returns:
            数据库连接URL字符串
        """
        if async_driver:
            return self.database_url
        else:
            # 同步驱动（用于Alembic迁移）
            return self.database_url.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用配置单例

    使用lru_cache装饰器确保配置只加载一次
    """
    return Settings()


# 环境变量示例文件内容
ENV_EXAMPLE = """# 原神游戏信息网站环境变量配置示例
# 复制此文件为 .env 并修改相应值

# 基础配置
APP_NAME=原神游戏信息网站
ENVIRONMENT=development
DEBUG=true
VERSION=1.0.0

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=postgresql+asyncpg://genshin_user:genshin_password@localhost:5432/genshin_wiki
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 安全配置
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# 文件上传配置
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_IMAGE_TYPES=["image/jpeg","image/png","image/webp"]

# 外部API配置
GENSHIN_API_BASE_URL=https://genshin.jmp.blue
GENSHIN_API_TIMEOUT=10

# 爬虫配置
SCRAPER_USER_AGENT=Genshin-Info-Bot/1.0 (+https://genshin-info.com)
SCRAPER_DELAY=1.0
SCRAPER_TIMEOUT=15

# 数据同步配置
SYNC_INTERVAL_HOURS=6
SYNC_RETRY_ATTEMPTS=3

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_ROTATION=1 day
LOG_RETENTION=30 days

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=8001
"""