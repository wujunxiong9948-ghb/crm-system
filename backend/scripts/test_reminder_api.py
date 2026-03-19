#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试提醒系统API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

with app.test_client() as client:
    # 1. 登录获取token
    print("=== 1. 登录测试 ===")
    login_resp = client.post('/api/v1/auth/login', 
        json={"username": "admin", "password": "admin123"})
    print(f"登录状态码: {login_resp.status_code}")
    
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
    
    # 2. 测试创建提醒
    print("\n=== 2. 创建提醒测试 ===")
    from datetime import datetime, timedelta
    reminder_data = {
        "reminder_type": "follow_up",
        "related_type": "customer",
        "related_id": 1,
        "title": "跟进客户：测试客户",
        "content": "该客户已7天未联系，建议跟进",
        "remind_at": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    
    resp = client.post('/api/v1/reminders/', 
        json=reminder_data, 
        headers=headers)
    print(f"创建提醒状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"响应: {data}")
    
    if data and data.get('success'):
        print("✅ 创建提醒成功！")
        reminder_id = data.get('data', {}).get('id')
    else:
        print("❌ 创建提醒失败")
        reminder_id = None
    
    # 3. 测试获取提醒列表
    print("\n=== 3. 获取提醒列表测试 ===")
    resp = client.get('/api/v1/reminders/', headers=headers)
    print(f"获取列表状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"提醒数量: {len(data.get('data', {}).get('items', []))}")
    print("✅ 获取提醒列表成功！")
    
    # 4. 测试获取提醒统计
    print("\n=== 4. 获取提醒统计测试 ===")
    resp = client.get('/api/v1/reminders/stats', headers=headers)
    print(f"获取统计状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"统计: {data.get('data')}")
    print("✅ 获取提醒统计成功！")
    
    # 5. 测试更新提醒状态
    if reminder_id:
        print("\n=== 5. 更新提醒状态测试 ===")
        resp = client.put(f'/api/v1/reminders/{reminder_id}',
            json={"status": "dismissed"},
            headers=headers)
        print(f"更新状态码: {resp.status_code}")
        data = resp.get_json()
        if data and data.get('success'):
            print("✅ 更新提醒状态成功！")
        else:
            print(f"❌ 更新提醒状态失败: {data}")
    
    print("\n=== 所有测试完成！===")
