#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

with app.test_client() as client:
    # 1. 登录
    print("=== 1. 登录 ===")
    login_resp = client.post('/api/v1/auth/login', 
        json={"username": "admin", "password": "admin123"})
    print(f"登录状态: {login_resp.status_code}")
    
    token_data = login_resp.get_json()
    if token_data.get('success') and token_data.get('data'):
        token = token_data['data']['access_token']
    elif token_data.get('access_token'):
        token = token_data['access_token']
    else:
        print(f"登录失败: {token_data}")
        sys.exit(1)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 测试客户列表
    print("\n=== 2. 测试客户列表 ===")
    resp = client.get('/api/v1/customers?page=1&per_page=20', headers=headers)
    print(f"状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"响应结构: {list(data.keys()) if data else 'None'}")
    if data and data.get('data'):
        print(f"客户数量: {len(data.get('data', []))}")
    else:
        print(f"错误: {data}")
    
    # 3. 测试联系记录
    print("\n=== 3. 测试联系记录 ===")
    resp = client.get('/api/v1/contacts?page=1&per_page=20', headers=headers)
    print(f"状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"响应结构: {list(data.keys()) if data else 'None'}")
    if data and data.get('data'):
        print(f"记录数量: {len(data.get('data', []))}")
    else:
        print(f"错误: {data}")
    
    # 4. 测试提醒中心
    print("\n=== 4. 测试提醒中心 ===")
    resp = client.get('/api/v1/reminders/', headers=headers)
    print(f"状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"响应结构: {list(data.keys()) if data else 'None'}")
    if data and data.get('data'):
        items = data.get('data', {}).get('items', [])
        print(f"提醒数量: {len(items)}")
    else:
        print(f"错误: {data}")
    
    # 5. 测试提醒统计
    print("\n=== 5. 测试提醒统计 ===")
    resp = client.get('/api/v1/reminders/stats', headers=headers)
    print(f"状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"响应: {data}")

    print("\n=== 测试完成 ===")
