"""
日志配置和处理

使用 structlog 提供结构化日志，支持中文输出和性能监控
"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog import configure, get_logger
from structlog.processors import CallsiteParameterAdder, TimeStamper

from src.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    配置应用日志系统

    设置 structlog 和标准 logging，支持控制台和文件输出
    """
    # 创建日志目录
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # 配置标准 logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([logging.FileHandler(settings.log_file)] if settings.log_file else [])
        ]
    )

    # 配置 structlog
    configure(
        processors=[
            # 添加调用位置信息（开发环境）
            CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ) if settings.is_development else structlog.processors.CallsiteParameterAdder(),

            # 添加时间戳
            TimeStamper(fmt="ISO", utc=True),

            # 添加日志级别
            structlog.stdlib.add_log_level,

            # 添加记录器名称
            structlog.stdlib.add_logger_name,

            # 处理异常信息
            structlog.processors.format_exc_info,

            # JSON格式化（生产环境）或彩色输出（开发环境）
            structlog.processors.JSONRenderer(ensure_ascii=False)
            if settings.is_production
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


class LoggerMixin:
    """
    日志记录混入类

    为类提供结构化日志记录功能
    """

    @property
    def logger(self):
        """获取当前类的logger实例"""
        return get_logger(self.__class__.__name__)

    def log_info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(message, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(message, **kwargs)

    def log_error(self, message: str, error: Exception = None, **kwargs):
        """记录错误日志"""
        if error:
            kwargs["error_type"] = error.__class__.__name__
            kwargs["error_message"] = str(error)
        self.logger.error(message, **kwargs)

    def log_debug(self, message: str, **kwargs):
        """记录调试日志"""
        if settings.debug:
            self.logger.debug(message, **kwargs)


def log_api_request(method: str, path: str, **kwargs):
    """记录API请求日志"""
    logger = get_logger("api_request")
    logger.info(
        "API请求",
        method=method,
        path=path,
        **kwargs
    )


def log_api_response(method: str, path: str, status_code: int, process_time: float, **kwargs):
    """记录API响应日志"""
    logger = get_logger("api_response")
    logger.info(
        "API响应",
        method=method,
        path=path,
        status_code=status_code,
        process_time_ms=round(process_time * 1000, 2),
        **kwargs
    )


def log_database_operation(operation: str, table: str, **kwargs):
    """记录数据库操作日志"""
    logger = get_logger("database")
    logger.debug(
        "数据库操作",
        operation=operation,
        table=table,
        **kwargs
    )


def log_external_api_call(api_name: str, endpoint: str, **kwargs):
    """记录外部API调用日志"""
    logger = get_logger("external_api")
    logger.info(
        "外部API调用",
        api_name=api_name,
        endpoint=endpoint,
        **kwargs
    )


def log_cache_operation(operation: str, key: str, **kwargs):
    """记录缓存操作日志"""
    logger = get_logger("cache")
    logger.debug(
        "缓存操作",
        operation=operation,
        key=key,
        **kwargs
    )


def log_scraper_activity(scraper_name: str, action: str, **kwargs):
    """记录爬虫活动日志"""
    logger = get_logger("scraper")
    logger.info(
        "爬虫活动",
        scraper_name=scraper_name,
        action=action,
        **kwargs
    )