"""
API统一响应工具模块
基于赫菲斯托斯的API响应格式规范实现
"""
from flask import jsonify, request
from datetime import datetime
import uuid


def api_response(code=200, message="success", data=None, success=None):
    """
    统一API响应格式
    
    Args:
        code: 业务状态码 (200=成功, 400xxx=客户端错误, 500xxx=服务器错误)
        message: 状态描述
        data: 业务数据
        success: 是否成功 (None时自动根据code判断)
    
    Returns:
        tuple: (response_body, http_status_code)
    """
    # 获取或生成request_id
    try:
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4())[:12])
    except RuntimeError:
        # 不在请求上下文中时生成随机ID
        request_id = str(uuid.uuid4())[:12]
    
    # 自动判断success
    if success is None:
        success = code == 200 or (code < 400 and code >= 200)
    
    response_body = {
        "success": success,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id
    }
    
    # HTTP状态码：业务码小于1000时直接使用，否则根据类型判断
    if code < 1000:
        http_status = code
    elif code >= 500000:
        http_status = 500
    elif code >= 400000:
        http_status = 400 if code < 500 else code // 1000
    else:
        http_status = 200
    
    return jsonify(response_body), http_status


# 常用错误响应快捷函数

def error_param_missing(field):
    """参数缺失错误"""
    return api_response(
        code=400001,
        message=f"参数错误：{field}不能为空",
        data={"field": field, "error_type": "missing_required"}
    )


def error_param_invalid(field, reason):
    """参数验证失败"""
    return api_response(
        code=400002,
        message=f"{field}验证失败：{reason}",
        data={"field": field, "reason": reason}
    )


def error_unauthorized():
    """未授权错误"""
    return api_response(
        code=401001,
        message="未授权，请先登录",
        data=None
    )


def error_token_expired():
    """Token过期错误"""
    return api_response(
        code=401002,
        message="登录已过期，请重新登录",
        data=None
    )


def error_forbidden(resource="该资源"):
    """禁止访问错误"""
    return api_response(
        code=403001,
        message=f"无权访问{resource}",
        data=None
    )


def error_not_found(resource="资源"):
    """资源不存在错误"""
    return api_response(
        code=404001,
        message=f"{resource}不存在",
        data=None
    )


def error_duplicate(resource="资源", field=""):
    """资源冲突/重复错误"""
    return api_response(
        code=409001,
        message=f"{resource}已存在" + (f"：{field}" if field else ""),
        data=None
    )


def error_internal(message="服务器内部错误，请稍后重试"):
    """服务器内部错误"""
    return api_response(
        code=500001,
        message=message,
        data=None
    )
