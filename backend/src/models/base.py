"""
SQLAlchemy 基础模型类

定义所有数据模型的基类和通用字段
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

# 创建基础模型类
Base = declarative_base()


class TimestampMixin:
    """时间戳混入类，为模型添加创建和更新时间字段"""

    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )


class BaseModel(Base, TimestampMixin):
    """基础模型类，包含ID和时间戳字段"""

    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    @declared_attr
    def __tablename__(cls):
        """自动生成表名（类名转小写复数）"""
        return cls.__name__.lower() + 's'

    def to_dict(self):
        """转换为字典格式"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"