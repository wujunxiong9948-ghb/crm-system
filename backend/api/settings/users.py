#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理API - 修复权限关联
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from datetime import datetime
import re

from . import settings_bp
from models import db, User, Role, UserRole
from utils.auth import (
    admin_required, 
    manager_required,
    check_permission,
    log_operation,
    get_user_permissions,
    Permissions
)
from utils.pagination import paginate
from utils.validators import validate_required


@settings_bp.route('/users', methods=['GET'])
@jwt_required()
@check_permission(Permissions.USER_MANAGE)
@log_operation('user', 'view', '查看用户列表')
def get_users():
    """获取用户列表"""
    try:
        # 查询参数
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')
        role = request.args.get('role', '')

        query = User.query

        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    User.username.contains(keyword),
                    User.full_name.contains(keyword),
                    User.email.contains(keyword),
                    User.phone.contains(keyword)
                )
            )

        # 状态筛选
        if status:
            query = query.filter(User.status == status)

        # 角色筛选
        if role:
            query = query.filter(User.role == role)

        # 排序
        query = query.order_by(User.created_at.desc())

        # 分页
        result = paginate(query, request)

        # 转换数据
        items = []
        for user in result['items']:
            user_dict = user.to_dict()
            # 获取用户角色
            user_roles = UserRole.query.filter_by(user_id=user.id).all()
            roles = []
            role_codes = []
            for ur in user_roles:
                role_obj = Role.query.get(ur.role_id)
                if role_obj:
                    roles.append({
                        'id': role_obj.id,
                        'name': role_obj.name,
                        'code': role_obj.code
                    })
                    role_codes.append(role_obj.code)
            user_dict['roles'] = roles
            user_dict['role_codes'] = role_codes
            items.append(user_dict)

        result['items'] = items
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/users/me/permissions', methods=['GET'])
@jwt_required()
def get_my_permissions():
    """获取当前用户权限"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取用户权限
        permissions = get_user_permissions(user_id)
        
        # 获取用户角色
        user_roles = UserRole.query.filter_by(user_id=user_id).all()
        roles = []
        for ur in user_roles:
            role_obj = Role.query.get(ur.role_id)
            if role_obj:
                roles.append({
                    'id': role_obj.id,
                    'name': role_obj.name,
                    'code': role_obj.code
                })
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'role': user.role,
            'roles': roles,
            'permissions': permissions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@check_permission(Permissions.USER_MANAGE)
@log_operation('user', 'view', '查看用户详情')
def get_user(user_id):
    """获取用户详情"""
    try:
        user = User.query.get_or_404(user_id)
        user_dict = user.to_dict()

        # 获取用户角色
        user_roles = UserRole.query.filter_by(user_id=user.id).all()
        roles = []
        role_ids = []
        for ur in user_roles:
            role_obj = Role.query.get(ur.role_id)
            if role_obj:
                roles.append({
                    'id': role_obj.id,
                    'name': role_obj.name,
                    'code': role_obj.code
                })
                role_ids.append(role_obj.id)
        
        user_dict['roles'] = roles
        user_dict['role_ids'] = role_ids
        
        # 获取用户所有权限
        user_dict['permissions'] = get_user_permissions(user_id)

        return jsonify(user_dict)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/users', methods=['POST'])
@jwt_required()
@check_permission(Permissions.USER_MANAGE)
@log_operation('user', 'create', '创建用户')
def create_user():
    """创建用户"""
    try:
        data = request.get_json()

        # 验证必填字段
        errors = validate_required(data, ['username', 'password', 'full_name'])
        if errors:
            return jsonify({'error': '缺少必填字段', 'details': errors}), 400

        # 验证用户名格式
        if not re.match(r'^[a-zA-Z0-9_]{4,20}$', data['username']):
            return jsonify({'error': '用户名必须是4-20位字母、数字或下划线'}), 400

        # 验证密码强度
        if len(data['password']) < 6:
            return jsonify({'error': '密码长度至少6位'}), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400

        # 检查邮箱是否已存在
        if data.get('email') and User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已被使用'}), 400

        # 创建用户
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()

        user = User(
            username=data['username'],
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            full_name=data['full_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position'),
            role=data.get('role', 'user'),
            status=data.get('status', 'active')
        )

        db.session.add(user)
        db.session.flush()

        # 分配角色
        role_ids = data.get('role_ids', [])
        if role_ids:
            for role_id in role_ids:
                # 检查角色是否存在
                role_obj = Role.query.get(role_id)
                if role_obj:
                    user_role = UserRole(user_id=user.id, role_id=role_id)
                    db.session.add(user_role)

        db.session.commit()

        return jsonify({
            'message': '用户创建成功',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@check_permission(Permissions.USER_MANAGE)
@log_operation('user', 'update', '更新用户')
def update_user(user_id):
    """更新用户"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # 更新基本信息
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            # 检查邮箱是否被其他用户使用
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': '邮箱已被使用'}), 400
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'department' in data:
            user.department = data['department']
        if 'position' in data:
            user.position = data['position']
        if 'role' in data:
            user.role = data['role']
        if 'status' in data:
            user.status = data['status']
        if 'avatar' in data:
            user.avatar = data['avatar']

        # 更新密码
        if data.get('password'):
            if len(data['password']) < 6:
                return jsonify({'error': '密码长度至少6位'}), 400
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # 更新角色
        if 'role_ids' in data:
            # 删除旧角色
            UserRole.query.filter_by(user_id=user_id).delete()
            # 添加新角色
            for role_id in data['role_ids']:
                role_obj = Role.query.get(role_id)
                if role_obj:
                    user_role = UserRole(user_id=user_id, role_id=role_id)
                    db.session.add(user_role)

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '用户更新成功',
            'user': user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@check_permission(Permissions.USER_MANAGE)
@log_operation('user', 'delete', '删除用户')
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.get_or_404(user_id)

        # 不能删除自己
        current_user_id = get_jwt_identity()
        if user_id == int(current_user_id):
            return jsonify({'error': '不能删除当前登录用户'}), 400

        # 删除用户角色关联
        UserRole.query.filter_by(user_id=user_id).delete()

        # 删除用户
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': '用户删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
@check_permission(Permissions.USER_MANAGE)
@log_operation('user', 'reset_password', '重置用户密码')
def reset_user_password(user_id):
    """重置用户密码"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json() or {}

        new_password = data.get('password', '123456')

        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': '密码重置成功',
            'new_password': new_password
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
@check_permission(Permissions.USER_MANAGE)
@log_operation('user', 'toggle_status', '切换用户状态')
def toggle_user_status(user_id):
    """切换用户状态"""
    try:
        user = User.query.get_or_404(user_id)

        # 不能禁用自己
        current_user_id = get_jwt_identity()
        if user_id == int(current_user_id):
            return jsonify({'error': '不能禁用当前登录用户'}), 400

        user.status = 'inactive' if user.status == 'active' else 'active'
        user.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': f'用户已{"启用" if user.status == "active" else "禁用"}',
            'status': user.status
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
