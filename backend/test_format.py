#!/usr/bin/env python3
"""测试 API 响应格式"""
import json
from app import create_app

app = create_app()

with app.test_client() as client:
    # Login
    resp = client.post('/api/v1/auth/login', 
                      data=json.dumps({'username': 'admin', 'password': 'admin123'}), 
                      content_type='application/json')
    token = json.loads(resp.data)['access_token']
    
    # Get opportunities
    resp = client.get('/api/v1/opportunities', headers={'Authorization': 'Bearer ' + token})
    data = json.loads(resp.data)
    
    print('Response keys:', list(data.keys()))
    print('Data count:', len(data.get('data', [])))
    
    if 'data' in data:
        print('SUCCESS: Response uses "data" key')
    elif 'opportunities' in data:
        print('ERROR: Still using "opportunities" key')
    else:
        print('WARNING: Unknown response format')
