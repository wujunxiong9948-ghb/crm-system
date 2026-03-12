#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统主应用
"""

import os
import sys
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from datetime import timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db

# 导入配置
from config import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""

    # 获取前端构建目录路径
    frontend_build_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'build')

    app = Flask(__name__, static_folder=frontend_build_path, static_url_path='')

    # 加载配置
    app.config.from_object(settings)

    # 设置SQLAlchemy配置
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': settings.DATABASE_POOL_SIZE,
        'max_overflow': settings.DATABASE_MAX_OVERFLOW,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # 配置JWT
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = settings.JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = settings.JWT_REFRESH_TOKEN_EXPIRES
    app.config['JWT_TOKEN_LOCATION'] = settings.JWT_TOKEN_LOCATION
    app.config['JWT_HEADER_NAME'] = settings.JWT_HEADER_NAME
    app.config['JWT_HEADER_TYPE'] = settings.JWT_HEADER_TYPE

    # 配置CORS
    CORS(app, origins=settings.CORS_ORIGINS, supports_credentials=True)

    # 初始化扩展
    db.init_app(app)
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 注册命令行命令
    register_commands(app)

    # 健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'service': settings.APP_NAME,
            'version': settings.APP_VERSION,
            'timestamp': get_current_timestamp()
        })

    # API文档端点
    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        """API文档"""
        if not settings.API_DOCS_ENABLED:
            return jsonify({'error': 'API文档已禁用'}), 403

        docs = {
            'api': {
                'version': settings.API_VERSION,
                'prefix': settings.API_PREFIX,
                'endpoints': get_api_endpoints(app)
            },
            'authentication': {
                'jwt': {
                    'header': settings.JWT_HEADER_NAME,
                    'type': settings.JWT_HEADER_TYPE,
                    'access_expires': str(settings.JWT_ACCESS_TOKEN_EXPIRES),
                    'refresh_expires': str(settings.JWT_REFRESH_TOKEN_EXPIRES)
                }
            },
            'pagination': {
                'default_page_size': settings.DEFAULT_PAGE_SIZE,
                'max_page_size': settings.MAX_PAGE_SIZE
            }
        }

        return jsonify(docs)

    # 前端路由处理 - 所有非API路由都返回index.html
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """服务前端应用"""
        # 如果是API请求，返回404
        if path.startswith('api/'):
            return jsonify({'error': 'API端点不存在'}), 404

        # 检查静态文件是否存在
        file_path = os.path.join(app.static_folder, path)
        if path and os.path.exists(file_path) and os.path.isfile(file_path):
            return app.send_static_file(path)

        # 否则返回index.html（前端路由处理）
        return app.send_static_file('index.html')

    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 应用初始化完成")

    return app

def register_blueprints(app):
    """注册蓝图"""

    # 导入蓝图
    from api.auth import auth_bp
    from api.customers import customers_bp
    from api.products import products_bp
    from api.orders import orders_bp
    from api.opportunities import opportunities_bp

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix=f'{settings.API_PREFIX}/{settings.API_VERSION}/auth')
    app.register_blueprint(customers_bp, url_prefix=f'{settings.API_PREFIX}/{settings.API_VERSION}/customers')
    app.register_blueprint(products_bp, url_prefix=f'{settings.API_PREFIX}/{settings.API_VERSION}/products')
    app.register_blueprint(orders_bp, url_prefix=f'{settings.API_PREFIX}/{settings.API_VERSION}/orders')
    app.register_blueprint(opportunities_bp, url_prefix=f'{settings.API_PREFIX}/{settings.API_VERSION}/opportunities')

    # 临时示例端点
    @app.route(f'{settings.API_PREFIX}/{settings.API_VERSION}/test', methods=['GET'])
    def test_endpoint():
        """测试端点"""
        return jsonify({
            'message': 'CRM系统API运行正常',
            'timestamp': get_current_timestamp(),
            'endpoint': '/api/v1/test'
        })

def register_error_handlers(app):
    """注册错误处理器"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': '请求参数错误',
            'message': str(error.description) if hasattr(error, 'description') else str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': '未授权访问',
            'message': '请先登录或提供有效的认证令牌'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': '禁止访问',
            'message': '您没有权限执行此操作'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        # 如果是API请求，返回JSON错误
        if request.path.startswith('/api/'):
            return jsonify({
                'error': '资源未找到',
                'message': '请求的API端点或资源不存在'
            }), 404
        # 否则返回前端应用（前端路由处理）
        return app.send_static_file('index.html')

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': '方法不允许',
            'message': '该HTTP方法不被支持'
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"服务器内部错误: {error}")
        return jsonify({
            'error': '服务器内部错误',
            'message': '服务器处理请求时发生错误'
        }), 500

def register_commands(app):
    """注册命令行命令"""

    @app.cli.command('init-db')
    def init_db_command():
        """初始化数据库"""
        from database.init_database import create_database
        create_database()
        print("数据库初始化完成")

    @app.cli.command('backup-db')
    def backup_db_command():
        """备份数据库"""
        from database.backup_database import DatabaseBackup
        backup_tool = DatabaseBackup()
        backup_file = backup_tool.backup_database()
        if backup_file:
            print(f"数据库备份完成: {backup_file}")
        else:
            print("数据库备份失败")

    @app.cli.command('migrate-db')
    def migrate_db_command():
        """迁移数据库"""
        from database.migrate_database import DatabaseMigrator
        migrator = DatabaseMigrator()
        if migrator.migrate_to_version():
            print("数据库迁移完成")
        else:
            print("数据库迁移失败")

def get_api_endpoints(app):
    """获取所有API端点"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith(settings.API_PREFIX):
            endpoints.append({
                'endpoint': rule.rule,
                'methods': list(rule.methods - {'OPTIONS', 'HEAD'}),
                'function': rule.endpoint
            })
    return endpoints

def get_current_timestamp():
    """获取当前时间戳"""
    from datetime import datetime
    return datetime.utcnow().isoformat() + 'Z'

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 启动开发服务器
    print("=" * 60)
    print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 60)
    print(f"运行模式: {'开发' if settings.DEBUG else '生产'}")
    print(f"数据库: {settings.DATABASE_URL}")
    print(f"日志级别: {settings.LOG_LEVEL}")
    print(f"API前缀: {settings.API_PREFIX}/{settings.API_VERSION}")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=settings.DEBUG,
        threaded=True
    )