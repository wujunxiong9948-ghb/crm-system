#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分页工具
"""


def paginate_query(query, request, default_page=1, default_per_page=20, max_per_page=100):
    """
    分页查询 - 别名函数，兼容不同导入方式
    """
    return paginate(query, request, default_page, default_per_page, max_per_page)


def paginate(query, request, default_page=1, default_per_page=20, max_per_page=100):
    """
    分页查询

    Args:
        query: SQLAlchemy查询对象
        request: Flask请求对象
        default_page: 默认页码
        default_per_page: 默认每页数量
        max_per_page: 最大每页数量

    Returns:
        dict: 分页结果
    """
    try:
        page = int(request.args.get('page', default_page))
    except (ValueError, TypeError):
        page = default_page

    try:
        per_page = int(request.args.get('per_page', default_per_page))
    except (ValueError, TypeError):
        per_page = default_per_page

    # 限制每页最大数量
    per_page = min(per_page, max_per_page)

    # 确保页码至少为1
    page = max(page, 1)

    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'items': pagination.items,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }
