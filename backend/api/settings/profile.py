#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人设置API
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from . import settings_bp
from models import db, User


@settings_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取个人信息"""
    try:
        user_id = get_jwt_identity()
        # 转换为整数
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': '无效的用户ID'}), 400
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取用户角色
        from models import UserRole, Role
        user_roles = UserRole.query.filter_by(user_id=user.id).all()
        roles = []
        for ur in user_roles:
            role = Role.query.get(ur.role_id)
            if role:
                roles.append({
                    'id': role.id,
                    'name': role.name,
                    'code': role.code
                })

        user_dict = user.to_dict()
        user_dict['roles'] = roles

        # 将头像URL转换为完整URL
        if user_dict.get('avatar') and user_dict['avatar'].startswith('/'):
            base_url = request.host_url.rstrip('/')
            user_dict['avatar'] = f"{base_url}{user_dict['avatar']}"

        return jsonify(user_dict)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新个人信息"""
    try:
        user_id = get_jwt_identity()
        # 转换为整数
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': '无效的用户ID'}), 400
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        data = request.get_json()

        # 更新可修改的字段
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
        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'department' in data:
            user.department = data['department']
        if 'position' in data:
            user.position = data['position']

        # 个人设置
        if 'theme' in data:
            user.theme = data['theme']
        if 'language' in data:
            user.language = data['language']
        if 'timezone' in data:
            user.timezone = data['timezone']
        if 'date_format' in data:
            user.date_format = data['date_format']

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '个人信息更新成功',
            'user': user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        # 转换为整数
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': '无效的用户ID'}), 400
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        data = request.get_json()

        # 验证必填字段
        if not data.get('old_password'):
            return jsonify({'error': '请输入原密码'}), 400
        if not data.get('new_password'):
            return jsonify({'error': '请输入新密码'}), 400

        # 验证原密码
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()

        if not bcrypt.check_password_hash(user.password_hash, data['old_password']):
            return jsonify({'error': '原密码不正确'}), 400

        # 验证新密码强度
        if len(data['new_password']) < 6:
            return jsonify({'error': '新密码长度至少6位'}), 400

        # 更新密码
        user.password_hash = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': '密码修改成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/profile/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """上传头像"""
    try:
        user_id = get_jwt_identity()
        # 转换为整数
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': '无效的用户ID'}), 400
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        if 'avatar' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['avatar']

        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': '只允许上传图片文件'}), 400

        # 保存文件
        import os
        from werkzeug.utils import secure_filename

        filename = secure_filename(f"avatar_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1]}")
        upload_path = os.path.join('uploads', 'avatars')
        os.makedirs(upload_path, exist_ok=True)

        file_path = os.path.join(upload_path, filename)
        file.save(file_path)

        # 更新用户头像 - 使用相对路径存储
        avatar_path = f'/uploads/avatars/{filename}'
        user.avatar = avatar_path
        user.updated_at = datetime.utcnow()
        db.session.commit()

        # 构建完整的URL
        from flask import request as flask_request
        base_url = flask_request.host_url.rstrip('/')
        full_avatar_url = f"{base_url}{avatar_path}"

        return jsonify({
            'message': '头像上传成功',
            'avatar_url': full_avatar_url
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
