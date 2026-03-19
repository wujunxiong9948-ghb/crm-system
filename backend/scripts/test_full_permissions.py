#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整权限功能测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import User, Role, Permission, UserRole, Customer
from utils.auth import (
    has_permission, get_user_permissions, 
    get_user_data_scope, check_data_ownership,
    Permissions
)


def test_role_permissions():
    """测试各角色权限"""
    print("\n" + "="*50)
    print("测试1: 各角色权限验证")
    print("="*50)
    
    roles_to_test = ['admin', 'manager', 'sales', 'user']
    
    for role_code in roles_to_test:
        role = Role.query.filter_by(code=role_code).first()
        if not role:
            print(f"[X] 角色 {role_code} 不存在")
            continue
        
        # 找一个有该角色的用户
        user_role = UserRole.query.filter_by(role_id=role.id).first()
        if user_role:
            user = User.query.get(user_role.user_id)
            perms = get_user_permissions(user.id)
            print(f"\n[{role_code}] {role.name}")
            print(f"  用户: {user.username}")
            print(f"  权限数量: {len(perms)}")
            print(f"  关键权限: ", end="")
            key_perms = ['customer:view', 'customer:create', 'user:manage']
            for p in key_perms:
                if p in perms:
                    print(f"{p} ✓ ", end="")
                else:
                    print(f"{p} ✗ ", end="")
            print()


def test_data_scope():
    """测试数据权限范围"""
    print("\n" + "="*50)
    print("测试2: 数据权限范围")
    print("="*50)
    
    users_to_test = [
        ('admin', 'all'),
        ('manager', 'department'),
        ('sales', 'self'),
    ]
    
    for username, expected_scope in users_to_test:
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"[X] 用户 {username} 不存在")
            continue
        
        scope = get_user_data_scope(user.id)
        status = "✓" if scope['type'] == expected_scope else "✗"
        print(f"[{status}] {username}: {scope['type']} (期望: {expected_scope})")


def test_permission_check():
    """测试权限检查函数"""
    print("\n" + "="*50)
    print("测试3: 权限检查函数")
    print("="*50)
    
    # admin 应该拥有所有权限
    admin = User.query.filter_by(username='admin').first()
    if admin:
        tests = [
            (Permissions.CUSTOMER_VIEW, True, "admin查看客户"),
            (Permissions.USER_MANAGE, True, "admin管理用户"),
            (Permissions.ROLE_MANAGE, True, "admin管理角色"),
            ('nonexistent:perm', True, "admin不存在权限也返回True"),
        ]
        
        for perm, expected, desc in tests:
            result = has_permission(admin.id, perm)
            status = "✓" if result == expected else "✗"
            print(f"[{status}] {desc}: {result}")


def test_customer_ownership():
    """测试客户数据所有权"""
    print("\n" + "="*50)
    print("测试4: 客户数据所有权")
    print("="*50)
    
    # 获取一个客户
    customer = Customer.query.first()
    if not customer:
        print("[!] 没有客户数据，跳过测试")
        return
    
    print(f"客户: {customer.name}")
    print(f"负责人: {customer.assigned_to}")
    print(f"创建者: {customer.created_by}")
    
    # 测试所有权检查
    admin = User.query.filter_by(username='admin').first()
    if admin and customer.assigned_to:
        assigned_user = User.query.filter_by(username=customer.assigned_to).first()
        if assigned_user:
            is_owner = check_data_ownership(customer, assigned_user.id)
            print(f"[✓] 负责人({assigned_user.username})拥有所有权: {is_owner}")


def test_api_endpoints():
    """测试API端点权限"""
    print("\n" + "="*50)
    print("测试5: API端点权限映射")
    print("="*50)
    
    endpoints = [
        ("GET /api/customers", Permissions.CUSTOMER_VIEW),
        ("POST /api/customers", Permissions.CUSTOMER_CREATE),
        ("PUT /api/customers/:id", Permissions.CUSTOMER_UPDATE),
        ("DELETE /api/customers/:id", Permissions.CUSTOMER_DELETE),
        ("GET /api/opportunities", Permissions.OPPORTUNITY_VIEW),
        ("POST /api/opportunities", Permissions.OPPORTUNITY_CREATE),
        ("GET /api/settings/users", Permissions.USER_MANAGE),
        ("GET /api/settings/roles", Permissions.ROLE_MANAGE),
    ]
    
    admin = User.query.filter_by(username='admin').first()
    if admin:
        for endpoint, perm in endpoints:
            has_perm = has_permission(admin.id, perm)
            status = "✓" if has_perm else "✗"
            print(f"[{status}] {endpoint} -> {perm}")


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*50)
        print("CRM 权限功能完整测试")
        print("="*50)
        
        try:
            test_role_permissions()
            test_data_scope()
            test_permission_check()
            test_customer_ownership()
            test_api_endpoints()
            
            print("\n" + "="*50)
            print("测试完成！")
            print("="*50)
            
        except Exception as e:
            print(f"\n[X] 测试失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
