#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统工具函数
"""

import os
import json
import hashlib
import random
import string
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

def generate_order_number(prefix: str = "ORD") -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_str}"

def generate_product_code(category: str, sequence: int) -> str:
    """生成产品编码"""
    category_code = category[:3].upper() if category else "GEN"
    return f"FURN-{category_code}-{sequence:04d}"

def format_currency(amount: float, currency: str = "CNY") -> str:
    """格式化货币金额"""
    if currency == "CNY":
        return f"¥{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_age(birth_date: date) -> int:
    """计算年龄"""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    import re
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """哈希密码"""
    if salt is None:
        salt = os.urandom(16).hex()

    # 使用PBKDF2进行密码哈希
    import hashlib
    import binascii

    dk = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 迭代次数
    )
    password_hash = binascii.hexlify(dk).decode('utf-8')

    return password_hash, salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """验证密码"""
    new_hash, _ = hash_password(password, salt)
    return new_hash == password_hash

def generate_random_string(length: int = 8) -> str:
    """生成随机字符串"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def format_date(date_obj: Union[date, datetime, str], format_str: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except ValueError:
            return date_obj

    if isinstance(date_obj, (date, datetime)):
        return date_obj.strftime(format_str)

    return str(date_obj)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[date]:
    """解析日期字符串"""
    try:
        return datetime.strptime(date_str, format_str).date()
    except (ValueError, TypeError):
        return None

def calculate_days_between(start_date: date, end_date: date) -> int:
    """计算两个日期之间的天数"""
    return (end_date - start_date).days

def get_week_range(target_date: date = None) -> tuple:
    """获取一周的日期范围"""
    if target_date is None:
        target_date = date.today()

    # 周一作为一周的开始
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week, end_of_week

def get_month_range(target_date: date = None) -> tuple:
    """获取一个月的日期范围"""
    if target_date is None:
        target_date = date.today()

    start_of_month = date(target_date.year, target_date.month, 1)

    if target_date.month == 12:
        end_of_month = date(target_date.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)

    return start_of_month, end_of_month

def calculate_percentage(part: float, total: float) -> float:
    """计算百分比"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    import re
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 移除多余空格
    filename = re.sub(r'\s+', ' ', filename).strip()
    # 限制长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    return filename

def json_serializer(obj: Any) -> Any:
    """JSON序列化器"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def load_json_file(filepath: str) -> Optional[Dict]:
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"加载JSON文件失败 {filepath}: {e}")
        return None

def save_json_file(data: Dict, filepath: str, indent: int = 2) -> bool:
    """保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=json_serializer)
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败 {filepath}: {e}")
        return False

def get_file_hash(filepath: str, algorithm: str = 'sha256') -> Optional[str]:
    """计算文件哈希值"""
    try:
        hash_func = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logger.error(f"计算文件哈希失败 {filepath}: {e}")
        return None

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_list(nested_list: List) -> List:
    """展平嵌套列表"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result

def remove_duplicates(lst: List) -> List:
    """移除列表中的重复项（保持顺序）"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def safe_get(dictionary: Dict, keys: List[str], default: Any = None) -> Any:
    """安全获取嵌套字典的值"""
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def format_duration(seconds: int) -> str:
    """格式化时间间隔"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}天{hours}小时"

def is_business_day(check_date: date) -> bool:
    """检查是否为工作日（周一至周五）"""
    return check_date.weekday() < 5  # 0=周一, 4=周五

def get_next_business_day(start_date: date = None, days: int = 1) -> date:
    """获取下一个工作日"""
    if start_date is None:
        start_date = date.today()

    current_date = start_date
    business_days_added = 0

    while business_days_added < days:
        current_date += timedelta(days=1)
        if is_business_day(current_date):
            business_days_added += 1

    return current_date

if __name__ == "__main__":
    # 测试工具函数
    print("测试工具函数:")
    print(f"订单号: {generate_order_number()}")
    print(f"产品编码: {generate_product_code('床', 1)}")
    print(f"货币格式化: {format_currency(1234567.89)}")
    print(f"邮箱验证: {validate_email('test@example.com')}")
    print(f"手机号验证: {validate_phone('13800138000')}")
    print(f"随机字符串: {generate_random_string()}")
    print(f"日期格式化: {format_date(date.today())}")
    print(f"文件大小格式化: {format_file_size(1024 * 1024)}")
    print("✅ 工具函数测试完成")