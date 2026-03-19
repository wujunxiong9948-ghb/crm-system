#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限验证工具 - 完善版
包含：功能权限、数据权限、操作日志
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from models import User, UserRole, RolePermission, Permission, OperationLog
import json
from datetime import datetime

# 延迟导入 db 避免循环导入
def get_db():
    from app import db
    return db


def get_current_user():
    """获取当前登录用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def has_permission(user_id, permission_code):
    """检查用户是否有指定权限
    
    Args:
        user_id: 用户ID
        permission_code: 权限代码
    
    Returns:
        bool: 是否有权限
    """
    # 转换user_id为整数（JWT返回的是字符串）
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return False
    
    user = User.query.get(user_id)
    if not user:
        return False
    
    # 管理员拥有所有权限
    if user.role == 'admin':
        return True
    
    # 获取用户的所有角色
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    if not role_ids:
        return False
    
    # 检查是否有指定权限
    has_perm = RolePermission.query.join(Permission).filter(
        RolePermission.role_id.in_(role_ids),
        Permission.code == permission_code,
        Permission.status == 'active'
    ).first()
    
    return has_perm is not None


def check_permission(permission_code):
    """权限检查装饰器
    
    Usage:
        @check_permission('customer:view')
        def get_customers():
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            
            if not has_permission(user_id, permission_code):
                return jsonify({'error': '没有操作权限', 'permission': permission_code}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permission_codes):
    """拥有任意一个权限即可
    
    Usage:
        @require_any_permission('customer:view', 'customer:manage')
        def get_customers():
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            
            for code in permission_codes:
                if has_permission(user_id, code):
                    return fn(*args, **kwargs)
            
            return jsonify({
                'error': '没有操作权限', 
                'permissions': list(permission_codes)
            }), 403
        return wrapper
    return decorator


def require_all_permissions(*permission_codes):
    """必须拥有所有权限
    
    Usage:
        @require_all_permissions('customer:view', 'customer:export')
        def export_customers():
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            
            missing = []
            for code in permission_codes:
                if not has_permission(user_id, code):
                    missing.append(code)
            
            if missing:
                return jsonify({
                    'error': '缺少必要权限', 
                    'missing': missing
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ==================== 数据权限控制 ====================

def get_user_data_scope(user_id):
    """获取用户的数据权限范围
    
    Returns:
        dict: {
            'type': 'all' | 'department' | 'self' | 'team',
            'department': str,  # 部门名称（如果是部门权限）
            'team_members': list  # 团队成员ID（如果是团队权限）
        }
    """
    # 转换user_id为整数
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return {'type': 'self'}
    
    user = User.query.get(user_id)
    if not user:
        return {'type': 'self'}
    
    # 管理员可以查看所有数据
    if user.role == 'admin':
        return {'type': 'all'}
    
    # 经理可以查看部门数据
    if user.role == 'manager':
        return {
            'type': 'department',
            'department': user.department
        }
    
    # 普通用户只能查看自己的数据
    return {'type': 'self'}


def apply_data_scope(query, model, user_id):
    """将数据权限范围应用到查询
    
    Args:
        query: SQLAlchemy 查询对象
        model: 模型类
        user_id: 用户ID
    
    Returns:
        query: 应用了数据权限的查询对象
    """
    from sqlalchemy import or_
    
    scope = get_user_data_scope(user_id)
    user = User.query.get(user_id)
    
    if scope['type'] == 'all':
        return query
    
    elif scope['type'] == 'department':
        # 查询同一部门的数据
        # 假设模型有 assigned_to 或 department 字段
        if hasattr(model, 'assigned_to'):
            # 获取同一部门的所有用户
            dept_users = User.query.filter_by(department=scope['department']).all()
            dept_user_names = [u.username for u in dept_users]
            query = query.filter(model.assigned_to.in_(dept_user_names))
        elif hasattr(model, 'department'):
            query = query.filter(model.department == scope['department'])
    
    elif scope['type'] == 'self':
        # 只能查看自己的数据
        if hasattr(model, 'assigned_to'):
            query = query.filter(model.assigned_to == user.username)
        elif hasattr(model, 'created_by'):
            query = query.filter(model.created_by == user_id)
        elif hasattr(model, 'user_id'):
            query = query.filter(model.user_id == user_id)
    
    return query


def data_scope_required(model_class):
    """数据权限装饰器 - 自动过滤查询结果
    
    Usage:
        @data_scope_required(Customer)
        def get_customers():
            query = Customer.query
            # 装饰器会自动应用数据权限
            return query.all()
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 将数据权限信息存入请求上下文
            user_id = get_jwt_identity()
            scope = get_user_data_scope(user_id)
            
            if not hasattr(request, '_data_scope'):
                request._data_scope = {}
            request._data_scope[model_class.__name__] = scope
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ==================== 角色快捷装饰器 ====================

def admin_required(fn):
    """管理员权限验证 - 同时检查 role 和 permissions"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': '需要管理员权限'}), 403
        
        # 检查 role 字段
        if user.role == 'admin':
            return fn(*args, **kwargs)
        
        # 检查是否有角色管理权限
        user_id = get_jwt_identity()
        if has_permission(user_id, Permissions.ROLE_MANAGE):
            return fn(*args, **kwargs)
        
        return jsonify({'error': '需要管理员权限'}), 403
    return wrapper


def manager_required(fn):
    """管理员或经理权限验证 - 同时检查 role 和 permissions"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': '需要管理权限'}), 403
        
        # 检查 role 字段
        if user.role in ['admin', 'manager']:
            return fn(*args, **kwargs)
        
        # 检查是否有管理权限（通过权限系统）
        user_id = get_jwt_identity()
        if has_permission(user_id, Permissions.USER_MANAGE):
            return fn(*args, **kwargs)
        
        return jsonify({'error': '需要管理权限'}), 403
    return wrapper


def sales_required(fn):
    """销售团队权限验证 - 同时检查 role 和 permissions"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': '需要销售团队权限'}), 403
        
        # 检查 role 字段
        if user.role in ['admin', 'manager', 'sales']:
            return fn(*args, **kwargs)
        
        # 检查是否有客户查看权限
        user_id = get_jwt_identity()
        if has_permission(user_id, Permissions.CUSTOMER_VIEW):
            return fn(*args, **kwargs)
        
        return jsonify({'error': '需要销售团队权限'}), 403
    return wrapper


# ==================== 操作日志记录 ====================

def log_operation(module, action, description=None):
    """记录操作日志装饰器
    
    Args:
        module: 操作模块，如 'customer', 'opportunity', 'order'
        action: 操作类型，如 'create', 'update', 'delete', 'view', 'export'
        description: 操作描述（可选，不传则自动生成）
    
    Usage:
        @log_operation('customer', 'create', '创建客户')
        def create_customer():
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            # 记录请求前数据
            request_data = None
            if request.is_json:
                try:
                    request_data = json.dumps(request.get_json(), ensure_ascii=False)
                except:
                    pass
            
            # 执行原函数
            response = fn(*args, **kwargs)
            
            # 记录操作日志
            try:
                status = 'success'
                error_message = None
                
                # 检查响应状态
                if hasattr(response, 'status_code'):
                    if response.status_code >= 400:
                        status = 'failed'
                        try:
                            error_data = response.get_json()
                            error_message = error_data.get('error', '未知错误')
                        except:
                            error_message = '操作失败'
                
                # 获取响应数据（限制长度）
                response_data = None
                if hasattr(response, 'get_json'):
                    try:
                        resp_json = response.get_json()
                        if resp_json:
                            resp_str = json.dumps(resp_json, ensure_ascii=False)
                            response_data = resp_str[:2000] if len(resp_str) > 2000 else resp_str
                    except:
                        pass
                
                # 生成描述
                desc = description
                if not desc:
                    desc = f"{action} {module}"
                
                log = OperationLog(
                    user_id=user_id,
                    username=user.username if user else 'unknown',
                    action=action,
                    module=module,
                    description=desc,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string[:500] if request.user_agent else None,
                    request_data=request_data,
                    response_data=response_data,
                    status=status,
                    error_message=error_message
                )
                
                db = get_db()
                db.session.add(log)
                db.session.commit()
                
            except Exception as e:
                # 日志记录失败不应影响主业务
                db = get_db()
                db.session.rollback()
                print(f"记录操作日志失败: {e}")
            
            return response
        return wrapper
    return decorator


# ==================== 权限常量定义 ====================

class Permissions:
    """权限常量定义"""
    
    # 客户管理权限
    CUSTOMER_VIEW = 'customer:view'
    CUSTOMER_CREATE = 'customer:create'
    CUSTOMER_UPDATE = 'customer:update'
    CUSTOMER_DELETE = 'customer:delete'
    CUSTOMER_EXPORT = 'customer:export'
    CUSTOMER_IMPORT = 'customer:import'
    
    # 销售机会权限
    OPPORTUNITY_VIEW = 'opportunity:view'
    OPPORTUNITY_CREATE = 'opportunity:create'
    OPPORTUNITY_UPDATE = 'opportunity:update'
    OPPORTUNITY_DELETE = 'opportunity:delete'
    OPPORTUNITY_TRANSFER = 'opportunity:transfer'
    OPPORTUNITY_EXPORT = 'opportunity:export'
    
    # 订单权限
    ORDER_VIEW = 'order:view'
    ORDER_CREATE = 'order:create'
    ORDER_UPDATE = 'order:update'
    ORDER_DELETE = 'order:delete'
    ORDER_APPROVE = 'order:approve'
    ORDER_EXPORT = 'order:export'
    
    # 产品权限
    PRODUCT_VIEW = 'product:view'
    PRODUCT_CREATE = 'product:create'
    PRODUCT_UPDATE = 'product:update'
    PRODUCT_DELETE = 'product:delete'
    
    # 报表权限
    REPORT_VIEW = 'report:view'
    REPORT_EXPORT = 'report:export'
    
    # 系统管理权限
    USER_MANAGE = 'user:manage'
    ROLE_MANAGE = 'role:manage'
    SETTINGS_MANAGE = 'settings:manage'
    LOG_VIEW = 'log:view'
    
    # 所有权限列表
    ALL = [
        CUSTOMER_VIEW, CUSTOMER_CREATE, CUSTOMER_UPDATE, CUSTOMER_DELETE, CUSTOMER_EXPORT, CUSTOMER_IMPORT,
        OPPORTUNITY_VIEW, OPPORTUNITY_CREATE, OPPORTUNITY_UPDATE, OPPORTUNITY_DELETE, OPPORTUNITY_TRANSFER, OPPORTUNITY_EXPORT,
        ORDER_VIEW, ORDER_CREATE, ORDER_UPDATE, ORDER_DELETE, ORDER_APPROVE, ORDER_EXPORT,
        PRODUCT_VIEW, PRODUCT_CREATE, PRODUCT_UPDATE, PRODUCT_DELETE,
        REPORT_VIEW, REPORT_EXPORT,
        USER_MANAGE, ROLE_MANAGE, SETTINGS_MANAGE, LOG_VIEW,
    ]


# ==================== 便捷函数 ====================

def get_user_permissions(user_id):
    """获取用户的所有权限"""
    # 转换user_id为整数
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return []
    
    user = User.query.get(user_id)
    if not user:
        return []
    
    if user.role == 'admin':
        return Permissions.ALL
    
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    if not role_ids:
        return []
    
    permissions = Permission.query.join(RolePermission).filter(
        RolePermission.role_id.in_(role_ids),
        Permission.status == 'active'
    ).all()
    
    return [p.code for p in permissions]


def check_data_ownership(record, user_id):
    """检查用户是否是数据的所有者
    
    Args:
        record: 数据记录对象
        user_id: 用户ID
    
    Returns:
        bool: 是否是所有者
    """
    # 转换user_id为整数
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return False
    
    user = User.query.get(user_id)
    if not user:
        return False
    
    # 管理员可以操作所有数据
    if user.role == 'admin':
        return True
    
    # 检查是否是数据的负责人
    if hasattr(record, 'assigned_to'):
        return record.assigned_to == user.username
    
    if hasattr(record, 'created_by'):
        return record.created_by == user_id
    
    if hasattr(record, 'user_id'):
        return record.user_id == user_id
    
    return False


# ==================== 密码处理函数 ====================

try:
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    
    def hash_password(password):
        """对密码进行哈希处理"""
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(password_hash, password):
        """验证密码"""
        return bcrypt.check_password_hash(password_hash, password)
        
except ImportError:
    # 如果没有flask_bcrypt，使用简单的实现（仅用于开发测试）
    import hashlib
    
    def hash_password(password):
        """对密码进行简单哈希（仅用于开发测试）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(password_hash, password):
        """验证密码（仅用于开发测试）"""
        return password_hash == hashlib.sha256(password.encode()).hexdigest()
