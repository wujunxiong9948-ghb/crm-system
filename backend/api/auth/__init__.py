#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证API模块
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from models import db, User
from datetime import datetime
import json

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()

        # 验证必填字段
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': '用户名和密码不能为空'}), 400

        # 查找用户
        user = User.query.filter_by(username=data['username']).first()

        if not user:
            return jsonify({'error': '用户名或密码错误'}), 401

        # 验证密码
        if not bcrypt.check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': '用户名或密码错误'}), 401

        # 检查用户状态
        if user.status != 'active':
            return jsonify({'error': '用户账户已被禁用'}), 403

        # 更新最后登录时间
        user.last_login = datetime.now()
        db.session.commit()

        # 创建token
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)

        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return jsonify({
            'access_token': access_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户资料"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户资料"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        data = request.get_json()

        # 更新允许的字段
        if 'full_name' in data:
            user.full_name = data['full_name']

        if 'email' in data:
            user.email = data['email']

        if 'password' in data and data['password']:
            user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        db.session.commit()

        return jsonify({
            'message': '资料更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        # JWT是无状态的，客户端需要删除token
        return jsonify({'message': '登出成功'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check', methods=['GET'])
@jwt_required()
def check_auth():
    """检查认证状态"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500