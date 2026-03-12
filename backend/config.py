#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统配置文件
"""

import os
from datetime import timedelta
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "酒店家具CRM系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # 数据库配置 - 使用绝对路径避免工作目录问题
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crm.db')}"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT配置
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)
    JWT_TOKEN_LOCATION: list = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"

    # CORS配置 - 允许所有来源（开发环境）
    CORS_ORIGINS: list = ["*"]

    # 文件上传配置
    UPLOAD_FOLDER: str = "../uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # 邮件配置
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_DEFAULT_SENDER: str = "noreply@example.com"

    # QQ通知配置
    QQ_NOTIFICATION_ENABLED: bool = True
    QQ_WEBHOOK_URL: Optional[str] = None
    QQ_API_KEY: Optional[str] = None

    # 备份配置
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL: str = "daily"  # daily, weekly, monthly
    BACKUP_RETENTION_DAYS: int = 30

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "../logs/crm.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 缓存配置
    CACHE_TYPE: str = "simple"  # simple, redis, memcached
    CACHE_REDIS_URL: Optional[str] = None
    CACHE_DEFAULT_TIMEOUT: int = 300  # 5分钟

    # 性能配置
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

    # 安全配置
    PASSWORD_HASH_METHOD: str = "pbkdf2:sha256"
    PASSWORD_SALT_LENGTH: int = 16
    PASSWORD_ITERATIONS: int = 260000

    # 会话配置
    SESSION_TYPE: str = "filesystem"
    SESSION_PERMANENT: bool = False
    SESSION_USE_SIGNER: bool = True
    SESSION_KEY_PREFIX: str = "crm_session:"

    # API配置
    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"
    API_DOCS_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings():
    """获取配置实例"""
    return Settings()

# 创建配置实例
settings = get_settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

# 确保日志目录存在
log_dir = os.path.dirname(settings.LOG_FILE)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)

if __name__ == "__main__":
    # 打印当前配置
    print("=" * 60)
    print("CRM系统配置")
    print("=" * 60)

    for key, value in settings.dict().items():
        if "PASSWORD" in key or "SECRET" in key or "KEY" in key:
            value = "***HIDDEN***"
        print(f"{key:30}: {value}")

    print("=" * 60)