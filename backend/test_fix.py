from app import create_app
import json

app = create_app()
print('='*60)
print('CRM Test')
print('='*60)

with app.test_client() as client:
    # 1. Login
    print('\n[1] Login')
    resp = client.post('/api/v1/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json')
    assert resp.status_code == 200
    token = json.loads(resp.data)['access_token']
    print('    OK')
    
    # 2. Get Profile
    print('\n[2] Get Profile')
    resp = client.get('/api/v1/auth/profile',
        headers={'Authorization': 'Bearer ' + token})
    assert resp.status_code == 200
    user = json.loads(resp.data)['user']
    print('    OK - ' + user['username'])
    
    # 3. Update Profile
    print('\n[3] Update Profile')
    resp = client.put('/api/v1/auth/profile',
        headers={'Authorization': 'Bearer ' + token},
        data=json.dumps({'full_name': 'Admin Test', 'email': 'test@example.com'}),
        content_type='application/json')
    assert resp.status_code == 200
    print('    OK')
    
    # 4. Check Auth
    print('\n[4] Check Auth')
    resp = client.get('/api/v1/auth/check',
        headers={'Authorization': 'Bearer ' + token})
    assert resp.status_code == 200
    print('    OK')
    
    # 5. Opportunities
    print('\n[5] Opportunities')
    resp = client.get('/api/v1/opportunities',
        headers={'Authorization': 'Bearer ' + token})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    print('    OK - Total: ' + str(data['pagination']['total']))
    
    # 6. Customers
    print('\n[6] Customers')
    resp = client.get('/api/v1/customers',
        headers={'Authorization': 'Bearer ' + token})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    print('    OK - Total: ' + str(data['pagination']['total']))

print('\n' + '='*60)
print('All tests passed!')
print('='*60)
