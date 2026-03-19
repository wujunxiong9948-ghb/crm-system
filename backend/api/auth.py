"""
认证API模块 - 处理登录、注册、Token刷新
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import User, db
from utils.auth import verify_password
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'error': '用户名或密码错误'}), 401
        
        if user.status != 'active':
            return jsonify({'error': '账号已被禁用'}), 403
        
        # 验证密码
        if not verify_password(user.password_hash, password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        db.session.commit()
        
        # 生成Token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'username': user.username,
                'role': user.role,
                'full_name': user.full_name
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role,
                    'department': user.department,
                    'avatar': user.avatar
                }
            }
        })
        
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({'error': '登录失败，请稍后重试'}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        
        # 验证必填字段
        if not all([username, password, full_name, email]):
            return jsonify({'error': '请填写所有必填字段'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 409
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被使用'}), 409
        
        # 创建新用户
        from utils.auth import hash_password
        new_user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            email=email,
            role='user',
            status='active'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'id': new_user.id,
                'username': new_user.username,
                'full_name': new_user.full_name
            }
        }), 201
        
    except Exception as e:
        logger.error(f"注册失败: {e}")
        db.session.rollback()
        return jsonify({'error': '注册失败，请稍后重试'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.status != 'active':
            return jsonify({'error': '用户不存在或已被禁用'}), 401
        
        new_token = create_access_token(
            identity=user_id,
            additional_claims={
                'username': user.username,
                'role': user.role,
                'full_name': user.full_name
            }
        )
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': new_token,
                'token_type': 'Bearer'
            }
        })
        
    except Exception as e:
        logger.error(f"刷新Token失败: {e}")
        return jsonify({'error': '刷新失败'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    # JWT是无状态的，客户端需要删除Token
    return jsonify({
        'success': True,
        'message': '登出成功'
    })


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'department': user.department,
                'position': user.position,
                'avatar': user.avatar,
                'status': user.status,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({'error': '获取用户信息失败'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 允许更新的字段
        allowed_fields = ['full_name', 'email', 'phone', 'avatar']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '个人信息更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'avatar': user.avatar
            }
        })
        
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}")
        db.session.rollback()
        return jsonify({'error': '更新失败'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({'error': '请提供旧密码和新密码'}), 400
        
        # 验证旧密码
        if not verify_password(user.password_hash, old_password):
            return jsonify({'error': '旧密码错误'}), 400
        
        # 更新密码
        from utils.auth import hash_password
        user.password_hash = hash_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
        
    except Exception as e:
        logger.error(f"修改密码失败: {e}")
        db.session.rollback()
        return jsonify({'error': '修改密码失败'}), 500
