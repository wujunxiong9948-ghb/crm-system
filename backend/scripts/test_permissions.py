#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限功能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import Permission, Role, User, UserRole
from utils.auth import has_permission, get_user_permissions, check_data_ownership, Permissions


def test_permissions():
    """测试权限数据"""
    print("\n[测试1] 检查权限数据...")
    
    perms = Permission.query.all()
    print(f"  数据库中有 {len(perms)} 个权限")
    
    # 检查关键权限
    key_perms = [
        Permissions.CUSTOMER_VIEW,
        Permissions.CUSTOMER_CREATE,
        Permissions.OPPORTUNITY_VIEW,
        Permissions.OPPORTUNITY_TRANSFER,
    ]
    
    for perm_code in key_perms:
        perm = Permission.query.filter_by(code=perm_code).first()
        if perm:
            print(f"  [OK] {perm_code}: {perm.name}")
        else:
            print(f"  [FAIL] {perm_code} 不存在")
    
    return True


def test_roles():
    """测试角色数据"""
    print("\n[测试2] 检查角色数据...")
    
    roles = Role.query.all()
    print(f"  数据库中有 {len(roles)} 个角色")
    
    for role in roles:
        perm_count = len(role.permissions)
        print(f"  [OK] {role.name} ({role.code}): {perm_count} 个权限")
    
    return True


def test_admin_permissions():
    """测试管理员权限"""
    print("\n[测试3] 测试管理员权限...")
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("  [FAIL] admin 用户不存在")
        return False
    
    print(f"  admin 用户ID: {admin.id}")
    
    # 检查角色关联
    user_roles = UserRole.query.filter_by(user_id=admin.id).all()
    print(f"  admin 有 {len(user_roles)} 个角色关联")
    
    # 测试权限检查
    result = has_permission(admin.id, 'customer:view')
    print(f"  has_permission(customer:view) = {result}")
    
    result = has_permission(admin.id, 'nonexistent:permission')
    print(f"  has_permission(nonexistent:permission) = {result}")
    
    # 获取所有权限
    all_perms = get_user_permissions(admin.id)
    print(f"  admin 共有 {len(all_perms)} 个权限")
    
    return True


def test_data_scope():
    """测试数据权限范围"""
    print("\n[测试4] 测试数据权限范围...")
    
    from utils.auth import get_user_data_scope
    
    admin = User.query.filter_by(username='admin').first()
    scope = get_user_data_scope(admin.id)
    print(f"  admin 数据权限范围: {scope}")
    
    return True


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("CRM 权限功能测试")
        print("=" * 50)
        
        try:
            test_permissions()
            test_roles()
            test_admin_permissions()
            test_data_scope()
            
            print("\n" + "=" * 50)
            print("测试完成！")
            print("=" * 50)
            
        except Exception as e:
            print(f"\n[X] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
