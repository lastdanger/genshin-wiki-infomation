"""
数据验证工具

提供常用的数据验证和转换函数
"""
import re
from typing import Any, List, Optional
from pathlib import Path

from src.utils.exceptions import ValidationException


def validate_element_type(element: str) -> bool:
    """
    验证元素类型

    Args:
        element: 元素类型字符串

    Returns:
        验证是否通过
    """
    valid_elements = {
        "Pyro", "Hydro", "Anemo", "Electro",
        "Dendro", "Cryo", "Geo"
    }
    return element in valid_elements


def validate_weapon_type(weapon_type: str) -> bool:
    """
    验证武器类型

    Args:
        weapon_type: 武器类型字符串

    Returns:
        验证是否通过
    """
    valid_weapons = {
        "Sword", "Claymore", "Polearm", "Bow", "Catalyst"
    }
    return weapon_type in valid_weapons


def validate_rarity(rarity: int, min_rarity: int = 1, max_rarity: int = 5) -> bool:
    """
    验证稀有度

    Args:
        rarity: 稀有度值
        min_rarity: 最小稀有度
        max_rarity: 最大稀有度

    Returns:
        验证是否通过
    """
    return isinstance(rarity, int) and min_rarity <= rarity <= max_rarity


def validate_image_file(filename: str, allowed_extensions: List[str] = None) -> bool:
    """
    验证图片文件名

    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表

    Returns:
        验证是否通过
    """
    if allowed_extensions is None:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']

    file_path = Path(filename)
    extension = file_path.suffix.lower()

    return extension in allowed_extensions


def validate_chinese_text(text: str, min_length: int = 1, max_length: int = 1000) -> bool:
    """
    验证中文文本

    Args:
        text: 待验证的文本
        min_length: 最小长度
        max_length: 最大长度

    Returns:
        验证是否通过
    """
    if not isinstance(text, str):
        return False

    text = text.strip()
    if not (min_length <= len(text) <= max_length):
        return False

    # 检查是否包含中文字符
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))


def validate_url(url: str) -> bool:
    """
    验证URL格式

    Args:
        url: URL字符串

    Returns:
        验证是否通过
    """
    url_pattern = re.compile(
        r'^https?://'  # 协议
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # 端口
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


def validate_page_params(page: int, per_page: int, max_per_page: int = 100) -> tuple[int, int]:
    """
    验证和标准化分页参数

    Args:
        page: 页码
        per_page: 每页数量
        max_per_page: 每页最大数量

    Returns:
        标准化后的页码和每页数量

    Raises:
        ValidationException: 参数验证失败时
    """
    if page < 1:
        raise ValidationException("page", "页码必须大于0")

    if per_page < 1:
        raise ValidationException("per_page", "每页数量必须大于0")

    if per_page > max_per_page:
        per_page = max_per_page

    return page, per_page


def sanitize_search_query(query: str) -> str:
    """
    清理搜索查询字符串

    Args:
        query: 原始查询字符串

    Returns:
        清理后的查询字符串
    """
    if not query:
        return ""

    # 移除特殊字符，保留中文、英文、数字和空格
    sanitized = re.sub(r'[^\u4e00-\u9fff\w\s]', '', query)

    # 标准化空白字符
    sanitized = ' '.join(sanitized.split())

    # 限制长度
    return sanitized[:100] if sanitized else ""


def validate_json_data(data: Any, required_fields: List[str] = None) -> bool:
    """
    验证JSON数据结构

    Args:
        data: JSON数据
        required_fields: 必需字段列表

    Returns:
        验证是否通过
    """
    if not isinstance(data, dict):
        return False

    if required_fields:
        for field in required_fields:
            if field not in data:
                return False

    return True


def normalize_character_name(name: str) -> str:
    """
    标准化角色名称

    Args:
        name: 原始角色名称

    Returns:
        标准化后的角色名称
    """
    if not name:
        return ""

    # 移除前后空格
    name = name.strip()

    # 统一常见的异体字和变体
    name_mappings = {
        "钟离": "钟离",
        "雷电将军": "雷电将军",
        "胡桃": "胡桃",
        # 可以根据需要添加更多映射
    }

    return name_mappings.get(name, name)


class ValidationResult:
    """验证结果类"""

    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(error)
        self.is_valid = False

    def __bool__(self):
        return self.is_valid


def validate_character_data(data: dict) -> ValidationResult:
    """
    验证角色数据完整性

    Args:
        data: 角色数据字典

    Returns:
        验证结果
    """
    result = ValidationResult(True)

    # 验证必需字段
    required_fields = ['name', 'element', 'weapon_type', 'rarity']
    for field in required_fields:
        if field not in data or not data[field]:
            result.add_error(f"缺少必需字段: {field}")

    # 验证元素类型
    if 'element' in data and not validate_element_type(data['element']):
        result.add_error(f"无效的元素类型: {data['element']}")

    # 验证武器类型
    if 'weapon_type' in data and not validate_weapon_type(data['weapon_type']):
        result.add_error(f"无效的武器类型: {data['weapon_type']}")

    # 验证稀有度
    if 'rarity' in data and not validate_rarity(data['rarity'], 4, 5):
        result.add_error(f"无效的稀有度: {data['rarity']} (只支持4星和5星角色)")

    return result