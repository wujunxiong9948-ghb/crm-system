from app import create_app
import json

app = create_app()
print('='*60)
print('Test opportunities endpoints')
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
    
    # 2. Get opportunities
    print('\n[2] GET /opportunities')
    resp = client.get('/api/v1/opportunities',
        headers={'Authorization': 'Bearer ' + token})
    print('    Status: ' + str(resp.status_code))
    if resp.status_code == 200:
        data = json.loads(resp.data)
        print('    Total: ' + str(data['pagination']['total']))
    else:
        print('    Error: ' + resp.data.decode()[:200])
    
    # 3. Get filter options
    print('\n[3] GET /opportunities/filters/options')
    resp = client.get('/api/v1/opportunities/filters/options',
        headers={'Authorization': 'Bearer ' + token})
    print('    Status: ' + str(resp.status_code))
    if resp.status_code == 200:
        print('    Response: ' + str(json.loads(resp.data)))
    else:
        print('    Error: ' + resp.data.decode()[:200])

print('\n' + '='*60)
print('Test complete!')
print('='*60)
