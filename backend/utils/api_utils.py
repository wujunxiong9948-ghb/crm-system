"""
API工具函数 - 统一接口响应和数据处理
基于API响应格式规范 v1.0
"""
from flask import jsonify, request
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import uuid
import logging

logger = logging.getLogger(__name__)


def generate_request_id():
    """生成请求ID"""
    try:
        return request.headers.get('X-Request-ID', str(uuid.uuid4())[:12])
    except RuntimeError:
        return str(uuid.uuid4())[:12]


class APIResponse:
    """统一API响应格式 - v1.0规范"""
    
    @staticmethod
    def success(data: Any = None, message: str = 'success', code: int = 200) -> tuple:
        """成功响应 - 标准格式 {success, code, message, data, timestamp, request_id}"""
        response_body = {
            'success': True,
            'code': code,
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': generate_request_id()
        }
        return jsonify(response_body), code
    
    @staticmethod
    def error(message: str = '操作失败', code: int = 400001, data: Any = None) -> tuple:
        """错误响应 - 标准格式"""
        # 判断HTTP状态码
        if code >= 500000:
            http_status = 500
        elif code >= 400000:
            http_status = code // 1000 if code // 1000 in [400, 401, 403, 404, 409, 422] else 400
        else:
            http_status = 400
        
        response_body = {
            'success': False,
            'code': code,
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': generate_request_id()
        }
        return jsonify(response_body), http_status
    
    @staticmethod
    def paginated(
        items: List[Any], 
        total: int, 
        page: int, 
        per_page: int,
        message: str = 'success'
    ) -> tuple:
        """分页响应 - 标准格式"""
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
                    'total_pages': (total + per_page - 1) // per_page,
                    'has_next': page * per_page < total,
                    'has_prev': page > 1
                }
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': generate_request_id()
        }), 200


# 便捷错误响应函数
def error_param_missing(field: str):
    """参数缺失错误 - 400001"""
    return APIResponse.error(
        code=400001,
        message=f'参数错误：{field}不能为空',
        data={'field': field, 'error_type': 'missing_required'}
    )


def error_unauthorized():
    """未授权错误 - 401001"""
    return APIResponse.error(
        code=401001,
        message='未授权，请先登录',
        data=None
    )


def error_forbidden(resource: str = '该资源'):
    """禁止访问错误 - 403001"""
    return APIResponse.error(
        code=403001,
        message=f'无权访问{resource}',
        data=None
    )


def error_not_found(resource: str = '资源'):
    """资源不存在错误 - 404001"""
    return APIResponse.error(
        code=404001,
        message=f'{resource}不存在',
        data=None
    )


def error_duplicate(resource: str = '资源', field: str = ''):
    """资源冲突/重复错误 - 409001"""
    msg = f'{resource}已存在'
    if field:
        msg += f'：{field}'
    return APIResponse.error(
        code=409001,
        message=msg,
        data=None
    )


def error_internal(message: str = '服务器内部错误，请稍后重试'):
    """服务器内部错误 - 500001"""
    return APIResponse.error(
        code=500001,
        message=message,
        data=None
    )


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
