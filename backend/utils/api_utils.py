"""
API工具函数 - 统一接口响应和数据处理
"""
from flask import jsonify
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data: Any = None, message: str = '操作成功', code: int = 200) -> tuple:
        """成功响应"""
        return jsonify({
            'success': True,
            'code': code,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }), code
    
    @staticmethod
    def error(message: str = '操作失败', code: int = 400, data: Any = None) -> tuple:
        """错误响应"""
        return jsonify({
            'success': False,
            'code': code,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }), code
    
    @staticmethod
    def paginated(
        items: List[Any], 
        total: int, 
        page: int, 
        per_page: int,
        message: str = '获取成功'
    ) -> tuple:
        """分页响应"""
        return jsonify({
            'success': True,
            'code': 200,
            'message': message,
            'data': {
                'items': items,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
            },
            'timestamp': datetime.now().isoformat()
        }), 200


class DateTimeUtils:
    """日期时间处理工具"""
    
    @staticmethod
    def parse_datetime(value: Any) -> Optional[datetime]:
        """解析日期时间"""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                # 处理ISO格式
                if 'T' in value or 'Z' in value:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                # 处理普通格式
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError) as e:
                logger.warning(f"日期解析失败: {value}, 错误: {e}")
                return None
        return None
    
    @staticmethod
    def parse_date(value: Any) -> Optional[date]:
        """解析日期"""
        if not value:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                logger.warning(f"日期解析失败: {value}, 错误: {e}")
                return None
        return None
    
    @staticmethod
    def format_datetime(value: Optional[datetime]) -> Optional[str]:
        """格式化日期时间"""
        if not value:
            return None
        return value.isoformat()
    
    @staticmethod
    def format_date(value: Optional[date]) -> Optional[str]:
        """格式化日期"""
        if not value:
            return None
        return value.isoformat()


class PaginationUtils:
    """分页工具"""
    
    @staticmethod
    def get_params(request) -> tuple:
        """获取分页参数"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        # 限制最大每页数量
        per_page = min(per_page, 100)
        # 确保最小值
        page = max(page, 1)
        per_page = max(per_page, 1)
        return page, per_page


class ValidationUtils:
    """验证工具"""
    
    @staticmethod
    def required_fields(data: dict, fields: List[str]) -> Optional[str]:
        """验证必填字段"""
        for field in fields:
            if not data.get(field):
                return f'{field} 为必填字段'
        return None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号"""
        if not phone:
            return False
        import re
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱"""
        if not email:
            return False
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# 导出便捷函数
api_success = APIResponse.success
api_error = APIResponse.error
api_paginated = APIResponse.paginated

# 日期处理便捷函数
parse_datetime = DateTimeUtils.parse_datetime
parse_date = DateTimeUtils.parse_date
format_datetime = DateTimeUtils.format_datetime
format_date = DateTimeUtils.format_date

# 分页便捷函数
get_pagination_params = PaginationUtils.get_params

# 验证便捷函数
validate_required = ValidationUtils.required_fields
