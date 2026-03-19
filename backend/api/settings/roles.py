#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色权限管理API
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from datetime import datetime

from . import settings_bp
from models import db, Role, Permission, RolePermission
from utils.auth import admin_required, manager_required
from utils.pagination import paginate
from utils.validators import validate_required


@settings_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """获取角色列表"""
    try:
        # 查询参数
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')

        query = Role.query

        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Role.name.contains(keyword),
                    Role.code.contains(keyword),
                    Role.description.contains(keyword)
                )
            )

        # 状态筛选
        if status:
            query = query.filter(Role.status == status)

        # 排序
        query = query.order_by(Role.created_at.desc())

        # 分页
        result = paginate(query, request)

        # 转换数据
        items = []
        for role in result['items']:
            role_dict = role.to_dict()
            # 获取角色权限
            role_permissions = RolePermission.query.filter_by(role_id=role.id).all()
            permissions = []
            for rp in role_permissions:
                perm = Permission.query.get(rp.permission_id)
                if perm:
                    permissions.append({
                        'id': perm.id,
                        'name': perm.name,
                        'code': perm.code,
                        'module': perm.module
                    })
            role_dict['permissions'] = permissions
            items.append(role_dict)

        result['items'] = items
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/roles/all', methods=['GET'])
@jwt_required()
def get_all_roles():
    """获取所有角色（不分页）"""
    try:
        roles = Role.query.filter_by(status='active').all()
        return jsonify([{
            'id': role.id,
            'name': role.name,
            'code': role.code,
            'description': role.description
        } for role in roles])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/roles/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    """获取角色详情"""
    try:
        role = Role.query.get_or_404(role_id)
        role_dict = role.to_dict()

        # 获取角色权限
        role_permissions = RolePermission.query.filter_by(role_id=role.id).all()
        permissions = []
        permission_ids = []
        for rp in role_permissions:
            perm = Permission.query.get(rp.permission_id)
            if perm:
                permissions.append({
                    'id': perm.id,
                    'name': perm.name,
                    'code': perm.code,
                    'module': perm.module
                })
                permission_ids.append(perm.id)

        role_dict['permissions'] = permissions
        role_dict['permission_ids'] = permission_ids

        return jsonify(role_dict)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/roles', methods=['POST'])
@jwt_required()
@manager_required
def create_role():
    """创建角色"""
    try:
        data = request.get_json()

        # 验证必填字段
        errors = validate_required(data, ['name', 'code'])
        if errors:
            return jsonify({'error': '缺少必填字段', 'details': errors}), 400

        # 检查角色代码是否已存在
        if Role.query.filter_by(code=data['code']).first():
            return jsonify({'error': '角色代码已存在'}), 400

        # 创建角色
        role = Role(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            status=data.get('status', 'active'),
            is_system=False
        )

        db.session.add(role)
        db.session.flush()

        # 分配权限
        permission_ids = data.get('permission_ids', [])
        if permission_ids:
            for perm_id in permission_ids:
                role_perm = RolePermission(role_id=role.id, permission_id=perm_id)
                db.session.add(role_perm)

        db.session.commit()

        return jsonify({
            'message': '角色创建成功',
            'role': role.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/roles/<int:role_id>', methods=['PUT'])
@jwt_required()
@manager_required
def update_role(role_id):
    """更新角色"""
    try:
        role = Role.query.get_or_404(role_id)

        # 系统内置角色不能修改代码
        if role.is_system:
            return jsonify({'error': '系统内置角色不能修改'}), 400

        data = request.get_json()

        # 更新基本信息
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']
        if 'status' in data:
            role.status = data['status']

        # 更新权限
        if 'permission_ids' in data:
            # 删除旧权限
            RolePermission.query.filter_by(role_id=role_id).delete()
            # 添加新权限
            for perm_id in data['permission_ids']:
                role_perm = RolePermission(role_id=role_id, permission_id=perm_id)
                db.session.add(role_perm)

        role.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '角色更新成功',
            'role': role.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_role(role_id):
    """删除角色"""
    try:
        role = Role.query.get_or_404(role_id)

        # 系统内置角色不能删除
        if role.is_system:
            return jsonify({'error': '系统内置角色不能删除'}), 400

        # 删除角色权限关联
        RolePermission.query.filter_by(role_id=role_id).delete()

        # 删除用户角色关联
        from models import UserRole
        UserRole.query.filter_by(role_id=role_id).delete()

        # 删除角色
        db.session.delete(role)
        db.session.commit()

        return jsonify({'message': '角色删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 权限管理 ====================

@settings_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    """获取权限列表"""
    try:
        # 查询参数
        module = request.args.get('module', '')

        query = Permission.query

        # 模块筛选
        if module:
            query = query.filter(Permission.module == module)

        # 排序
        query = query.order_by(Permission.module, Permission.code)

        permissions = query.all()

        # 按模块分组
        result = {}
        for perm in permissions:
            if perm.module not in result:
                result[perm.module] = []
            result[perm.module].append({
                'id': perm.id,
                'name': perm.name,
                'code': perm.code,
                'description': perm.description,
                'status': perm.status
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/permissions', methods=['POST'])
@jwt_required()
@admin_required
def create_permission():
    """创建权限"""
    try:
        data = request.get_json()

        # 验证必填字段
        errors = validate_required(data, ['name', 'code', 'module'])
        if errors:
            return jsonify({'error': '缺少必填字段', 'details': errors}), 400

        # 检查权限代码是否已存在
        if Permission.query.filter_by(code=data['code']).first():
            return jsonify({'error': '权限代码已存在'}), 400

        # 创建权限
        permission = Permission(
            name=data['name'],
            code=data['code'],
            module=data['module'],
            description=data.get('description'),
            status=data.get('status', 'active')
        )

        db.session.add(permission)
        db.session.commit()

        return jsonify({
            'message': '权限创建成功',
            'permission': permission.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/permissions/<int:perm_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_permission(perm_id):
    """更新权限"""
    try:
        permission = Permission.query.get_or_404(perm_id)
        data = request.get_json()

        if 'name' in data:
            permission.name = data['name']
        if 'description' in data:
            permission.description = data['description']
        if 'status' in data:
            permission.status = data['status']

        permission.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '权限更新成功',
            'permission': permission.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/permissions/<int:perm_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_permission(perm_id):
    """删除权限"""
    try:
        permission = Permission.query.get_or_404(perm_id)

        # 删除角色权限关联
        RolePermission.query.filter_by(permission_id=perm_id).delete()

        # 删除权限
        db.session.delete(permission)
        db.session.commit()

        return jsonify({'message': '权限删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/permissions/modules', methods=['GET'])
@jwt_required()
def get_permission_modules():
    """获取权限模块列表"""
    try:
        modules = db.session.query(Permission.module).distinct().all()
        return jsonify([m[0] for m in modules])

    except Exception as e:
        return jsonify({'error': str(e)}), 500
