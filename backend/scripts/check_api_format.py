#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一检查所有API返回格式
确保所有列表接口返回 {data: [...], pagination: {...}} 格式
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

endpoints = [
    ('/api/v1/customers', 'customers'),
    ('/api/v1/opportunities', 'opportunities'),
    ('/api/v1/orders', 'orders'),
    ('/api/v1/products', 'products'),
    ('/api/v1/contacts', 'contacts'),
    ('/api/v1/reminders/', 'reminders'),
]

print("=" * 60)
print("API接口格式统一检查")
print("=" * 60)

with app.test_client() as client:
    # 登录
    login_resp = client.post('/api/v1/auth/login', 
        json={"username": "admin", "password": "admin123"})
    
    token_data = login_resp.get_json()
    if token_data.get('success') and token_data.get('data'):
        token = token_data['data']['access_token']
    elif token_data.get('access_token'):
        token = token_data['access_token']
    else:
        print(f"登录失败: {token_data}")
        sys.exit(1)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for endpoint, name in endpoints:
        print(f"\n【{name}】{endpoint}")
        resp = client.get(endpoint, headers=headers)
        print(f"  状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.get_json()
            print(f"  返回结构: {list(data.keys()) if data else 'None'}")
            
            # 检查是否符合标准格式
            has_data = 'data' in data if data else False
            has_items = 'items' in data.get('data', {}) if data and isinstance(data.get('data'), dict) else False
            has_custom_field = any(k in ['customers', 'opportunities', 'orders', 'products', 'contacts', 'reminders'] 
                                   for k in (data.keys() if data else []))
            
            if has_data:
                if has_items:
                    items = data.get('data', {}).get('items', [])
                    print(f"  ✅ 标准格式 {{data: {{items: [...]}}}}")
                    print(f"  数据条数: {len(items)}")
                elif isinstance(data.get('data'), list):
                    print(f"  ⚠️  非标准格式 {{data: [...]}}  (应为 {{data: {{items: [...]}}}})")
                    print(f"  数据条数: {len(data.get('data', []))}")
                else:
                    print(f"  ⚠️  未知data格式")
            elif has_custom_field:
                for k in data.keys():
                    if k in ['customers', 'opportunities', 'orders', 'products', 'contacts', 'reminders']:
                        print(f"  ❌ 非标准格式 {{{k}: [...]}}  (应为 {{data: {{items: [...]}}}})")
                        print(f"  数据条数: {len(data.get(k, []))}")
                        break
            else:
                print(f"  ❓ 未知格式")
        else:
            print(f"  ❌ 请求失败")

print("\n" + "=" * 60)
print("检查完成！")
print("=" * 60)
