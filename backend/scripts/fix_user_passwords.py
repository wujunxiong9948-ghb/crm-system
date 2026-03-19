#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查用户并修复密码
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User
from utils.auth import hash_password

app = create_app()

with app.app_context():
    # 列出所有用户
    users = User.query.all()
    print("当前用户列表:")
    for u in users:
        print(f"  - {u.username} ({u.full_name}), role={u.role}, status={u.status}")
    
    # 确保admin用户存在且密码正确
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"\n重置admin密码...")
        admin.password_hash = hash_password('admin123')
        db.session.commit()
        print("✅ admin密码已重置为 admin123")
    
    # 确保sales1用户存在且密码正确
    sales1 = User.query.filter_by(username='sales1').first()
    if sales1:
        print(f"\n重置sales1密码...")
        sales1.password_hash = hash_password('sales123')
        db.session.commit()
        print("✅ sales1密码已重置为 sales123")
