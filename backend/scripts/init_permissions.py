#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限系统初始化脚本
创建默认权限和角色
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import Permission, Role, RolePermission, UserRole


def init_permissions():
    """初始化权限数据"""
    permissions = [
        # 客户管理权限
        {'name': '查看客户', 'code': 'customer:view', 'module': 'customer', 'description': '查看客户列表和详情'},
        {'name': '创建客户', 'code': 'customer:create', 'module': 'customer', 'description': '创建新客户'},
        {'name': '编辑客户', 'code': 'customer:update', 'module': 'customer', 'description': '编辑客户信息'},
        {'name': '删除客户', 'code': 'customer:delete', 'module': 'customer', 'description': '删除客户'},
        {'name': '导出客户', 'code': 'customer:export', 'module': 'customer', 'description': '导出客户数据'},
        {'name': '导入客户', 'code': 'customer:import', 'module': 'customer', 'description': '批量导入客户'},
        
        # 销售机会权限
        {'name': '查看机会', 'code': 'opportunity:view', 'module': 'opportunity', 'description': '查看销售机会'},
        {'name': '创建机会', 'code': 'opportunity:create', 'module': 'opportunity', 'description': '创建销售机会'},
        {'name': '编辑机会', 'code': 'opportunity:update', 'module': 'opportunity', 'description': '编辑销售机会'},
        {'name': '删除机会', 'code': 'opportunity:delete', 'module': 'opportunity', 'description': '删除销售机会'},
        {'name': '转移机会', 'code': 'opportunity:transfer', 'module': 'opportunity', 'description': '转移机会归属'},
        {'name': '导出机会', 'code': 'opportunity:export', 'module': 'opportunity', 'description': '导出机会数据'},
        
        # 订单权限
        {'name': '查看订单', 'code': 'order:view', 'module': 'order', 'description': '查看订单'},
        {'name': '创建订单', 'code': 'order:create', 'module': 'order', 'description': '创建订单'},
        {'name': '编辑订单', 'code': 'order:update', 'module': 'order', 'description': '编辑订单'},
        {'name': '删除订单', 'code': 'order:delete', 'module': 'order', 'description': '删除订单'},
        {'name': '审批订单', 'code': 'order:approve', 'module': 'order', 'description': '审批订单'},
        {'name': '导出订单', 'code': 'order:export', 'module': 'order', 'description': '导出订单数据'},
        
        # 产品权限
        {'name': '查看产品', 'code': 'product:view', 'module': 'product', 'description': '查看产品'},
        {'name': '创建产品', 'code': 'product:create', 'module': 'product', 'description': '创建产品'},
        {'name': '编辑产品', 'code': 'product:update', 'module': 'product', 'description': '编辑产品'},
        {'name': '删除产品', 'code': 'product:delete', 'module': 'product', 'description': '删除产品'},
        
        # 报表权限
        {'name': '查看报表', 'code': 'report:view', 'module': 'report', 'description': '查看数据报表'},
        {'name': '导出报表', 'code': 'report:export', 'module': 'report', 'description': '导出报表数据'},
        
        # 系统管理权限
        {'name': '用户管理', 'code': 'user:manage', 'module': 'system', 'description': '管理用户账户'},
        {'name': '角色管理', 'code': 'role:manage', 'module': 'system', 'description': '管理角色权限'},
        {'name': '系统设置', 'code': 'settings:manage', 'module': 'system', 'description': '管理系统设置'},
        {'name': '查看日志', 'code': 'log:view', 'module': 'system', 'description': '查看操作日志'},
    ]
    
    created_count = 0
    for perm_data in permissions:
        # 检查是否已存在
        existing = Permission.query.filter_by(code=perm_data['code']).first()
        if not existing:
            perm = Permission(**perm_data)
            db.session.add(perm)
            created_count += 1
            print(f"[+] 创建权限: {perm_data['name']} ({perm_data['code']})")
        else:
            # 更新现有权限
            existing.name = perm_data['name']
            existing.module = perm_data['module']
            existing.description = perm_data['description']
            print(f"[*] 更新权限: {perm_data['name']}")
    
    db.session.commit()
    print(f"\n权限初始化完成: 新增 {created_count} 个权限")
    return True


def init_roles():
    """初始化角色数据"""
    roles = [
        {
            'name': '系统管理员',
            'code': 'admin',
            'description': '拥有系统所有权限',
            'is_system': True,
            'permissions': []  # 管理员自动拥有所有权限
        },
        {
            'name': '销售经理',
            'code': 'manager',
            'description': '管理销售团队，查看部门数据',
            'is_system': True,
            'permissions': [
                'customer:view', 'customer:create', 'customer:update', 'customer:export',
                'opportunity:view', 'opportunity:create', 'opportunity:update', 'opportunity:delete', 'opportunity:transfer', 'opportunity:export',
                'order:view', 'order:create', 'order:update', 'order:export',
                'product:view',
                'report:view', 'report:export',
                'log:view'
            ]
        },
        {
            'name': '销售员',
            'code': 'sales',
            'description': '负责客户跟进和销售机会',
            'is_system': True,
            'permissions': [
                'customer:view', 'customer:create', 'customer:update', 'customer:export',
                'opportunity:view', 'opportunity:create', 'opportunity:update', 'opportunity:export',
                'order:view', 'order:create', 'order:export',
                'product:view',
                'report:view'
            ]
        },
        {
            'name': '普通用户',
            'code': 'user',
            'description': '只能查看自己的数据',
            'is_system': True,
            'permissions': [
                'customer:view',
                'opportunity:view',
                'order:view',
                'product:view'
            ]
        },
        {
            'name': '产品管理员',
            'code': 'product_manager',
            'description': '管理产品信息',
            'is_system': False,
            'permissions': [
                'product:view', 'product:create', 'product:update', 'product:delete'
            ]
        }
    ]
    
    created_count = 0
    for role_data in roles:
        permissions = role_data.pop('permissions')
        
        # 检查是否已存在
        existing = Role.query.filter_by(code=role_data['code']).first()
        if not existing:
            role = Role(**role_data)
            db.session.add(role)
            db.session.flush()  # 获取role.id
            created_count += 1
            print(f"[+] 创建角色: {role_data['name']}")
        else:
            # 更新现有角色
            existing.name = role_data['name']
            existing.description = role_data['description']
            existing.is_system = role_data['is_system']
            role = existing
            print(f"[*] 更新角色: {role_data['name']}")
        
        # 分配权限
        if permissions:
            # 清除旧权限
            RolePermission.query.filter_by(role_id=role.id).delete()
            
            for perm_code in permissions:
                perm = Permission.query.filter_by(code=perm_code).first()
                if perm:
                    rp = RolePermission(role_id=role.id, permission_id=perm.id)
                    db.session.add(rp)
            
            print(f"    -> 分配 {len(permissions)} 个权限")
    
    db.session.commit()
    print(f"\n角色初始化完成")
    return True


def update_admin_user():
    """更新admin用户角色关联"""
    from models import User
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        print("[!] 未找到 admin 用户")
        return False
    
    # 获取admin角色
    admin_role = Role.query.filter_by(code='admin').first()
    if not admin_role:
        print("[!] 未找到 admin 角色")
        return False
    
    # 检查是否已关联
    existing = UserRole.query.filter_by(user_id=admin_user.id, role_id=admin_role.id).first()
    if not existing:
        ur = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        db.session.add(ur)
        db.session.commit()
        print(f"[+] 已为 admin 用户分配管理员角色")
    else:
        print(f"[*] admin 用户已有关联角色")
    
    return True


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("CRM 权限系统初始化")
        print("=" * 50)
        
        try:
            # 初始化权限
            print("\n[1] 初始化权限...")
            init_permissions()
            
            # 初始化角色
            print("\n[2] 初始化角色...")
            init_roles()
            
            # 更新admin用户
            print("\n[3] 更新管理员用户...")
            update_admin_user()
            
            print("\n" + "=" * 50)
            print("权限系统初始化完成！")
            print("=" * 50)
            
        except Exception as e:
            print(f"\n[X] 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
