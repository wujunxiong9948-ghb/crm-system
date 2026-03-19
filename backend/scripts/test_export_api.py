#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据导出导入API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

with app.test_client() as client:
    # 1. 登录
    print("=== 1. 登录测试 ===")
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
    
    print("✅ 登录成功！")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 测试导出客户
    print("\n=== 2. 导出客户测试 ===")
    resp = client.get('/api/v1/export/customers', headers=headers)
    print(f"状态码: {resp.status_code}")
    print(f"Content-Type: {resp.content_type}")
    if resp.status_code == 200:
        print(f"文件大小: {len(resp.data)} bytes")
        print("✅ 导出客户成功！")
    else:
        print(f"❌ 导出失败: {resp.get_json()}")
    
    # 3. 测试下载导入模板
    print("\n=== 3. 下载导入模板测试 ===")
    resp = client.get('/api/v1/export/customers/template', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        print(f"文件大小: {len(resp.data)} bytes")
        print("✅ 下载模板成功！")
    else:
        print(f"❌ 下载模板失败: {resp.get_json()}")
    
    # 4. 测试导出销售机会
    print("\n=== 4. 导出销售机会测试 ===")
    resp = client.get('/api/v1/export/opportunities', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        print(f"文件大小: {len(resp.data)} bytes")
        print("✅ 导出销售机会成功！")
    else:
        print(f"❌ 导出失败: {resp.get_json()}")
    
    # 5. 测试导出订单
    print("\n=== 5. 导出订单测试 ===")
    resp = client.get('/api/v1/export/orders', headers=headers)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 200:
        print(f"文件大小: {len(resp.data)} bytes")
        print("✅ 导出订单成功！")
    else:
        print(f"❌ 导出失败: {resp.get_json()}")
    
    print("\n=== 所有测试完成！===")
