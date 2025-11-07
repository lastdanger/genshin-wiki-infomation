"""
图片数据模型（基础结构）

将在Phase 7 (图片功能) 完整实现
"""
from sqlalchemy import Column, String, Integer, Boolean, Index
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Image(BaseModel):
    """图片模型（基础结构）"""

    __tablename__ = "images"

    entity_type = Column(String(20), nullable=False, comment="实体类型")
    entity_id = Column(Integer, nullable=False, comment="实体ID")
    image_type = Column(String(30), nullable=False, comment="图片类型")
    url = Column(String(500), nullable=False, comment="图片URL")
    filename = Column(String(255), nullable=False, comment="文件名")
    file_size = Column(Integer, nullable=False, comment="文件大小")
    mime_type = Column(String(50), nullable=False, comment="MIME类型")
    width = Column(Integer, nullable=False, comment="图片宽度")
    height = Column(Integer, nullable=False, comment="图片高度")
    is_official = Column(Boolean, default=True, comment="是否为官方图片")
    upload_user_id = Column(Integer, nullable=True, comment="上传用户ID")
    moderation_status = Column(String(20), default='approved', comment="审核状态")
    moderation_notes = Column(String(500), nullable=True, comment="审核备注")

    __table_args__ = (
        Index('idx_images_entity', 'entity_type', 'entity_id'),
        Index('idx_images_type', 'image_type'),
    )