#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证工具
"""


def validate_required(data, required_fields):
    """
    验证必填字段

    Args:
        data: 数据字典
        required_fields: 必填字段列表

    Returns:
        list: 错误信息列表，为空表示验证通过
    """
    errors = []
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            errors.append(f'{field} 是必填字段')
    return errors


def validate_required_fields(data, required_fields):
    """
    验证必填字段 - 返回字符串错误信息或None

    Args:
        data: 数据字典
        required_fields: 必填字段列表

    Returns:
        str or None: 错误信息，None表示验证通过
    """
    errors = validate_required(data, required_fields)
    if errors:
        return '；'.join(errors)
    return None


def validate_email(email):
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """验证手机号格式（中国大陆）"""
    import re
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def validate_length(value, min_length=None, max_length=None):
    """验证字符串长度"""
    if value is None:
        return False

    length = len(str(value))

    if min_length is not None and length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True
