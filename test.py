import requests

token = requests.post('http://127.0.0.1:5000/api/signup').json()['token']
print(token)

print(requests.post('http://127.0.0.1:5000/api/boards/create',
             headers={
                'Authorization': f'Bearer {token}',
                 'Content-Type': 'application/json'
             },
                    json={
                        'name': 'doska2'
                    }
).text)

print(requests.post('http://127.0.0.1:5000/api/boards/create',
             headers={
                'Authorization': f'Bearer {token}',
                 'Content-Type': 'application/json'
             },
                    json={
                        'name': 'doska23'
                    }
).text)

r = requests.get('http://127.0.0.1:5000/api/boards',
             headers={
                'Authorization': f'Bearer {token}'
             }
).json()

print(r)

print(requests.post(f'http://127.0.0.1:5000/api/boards/{r[0]['id']}/edit',
             headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
             },
            json = {
                'name': 'doska1'
            }
).text)

print(requests.get('http://127.0.0.1:5000/api/boards',
             headers={
                'Authorization': f'Bearer {token}'
             }
).json())

print(requests.post(f'http://127.0.0.1:5000/api/boards/{r[0]['id']}/tasks/create',
             headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
             },
            json = {
                'title': 'kakat',
                'description': 'pokakat',
                'status': 1
            }
).text)

print(requests.post(f'http://127.0.0.1:5000/api/boards/{r[0]['id']}/tasks/create',
             headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
             },
            json = {
                'title': 'popa',
                'description': 'viteret',
                'status': 1
            }
).text)

print(requests.post(f'http://127.0.0.1:5000/api/boards/{r[0]['id']}/tasks/1/edit',
             headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
             },
            json = {
                'title': 'popa',
                'description': 'viteret',
                'status': 2
            }
).text)

print(requests.get('http://127.0.0.1:5000/api/boards',
             headers={
                'Authorization': f'Bearer {token}'
             }
).json())

print(requests.post('http://127.0.0.1:5000/api/boards/2/delete',
             headers={
                'Authorization': f'Bearer {token}'
             }
).text)

print(requests.post('http://127.0.0.1:5000/api/boards/1/tasks/1/delete',
             headers={
                'Authorization': f'Bearer {token}'
             }
).text)