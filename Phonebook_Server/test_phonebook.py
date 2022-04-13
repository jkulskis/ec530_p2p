import requests

BASE = 'http://127.0.0.1:5000/'

data = { 
    'IP': '127.0.0.1:5000', 
    'port': 80,
    'password': 'password'
}

print('get all')
response = requests.get(BASE + 'peers/')
print(response.json())

print('delete Daniel')
response = requests.delete(BASE + 'peers/Daniel', json = data)
print(response)

print('get Daniel')
response = requests.get(BASE + 'peers/Daniel')
print(response.json())

print('post Daniel')
response = requests.post(BASE + 'peers/Daniel', json = data)
print(response)

print('post Daniel')
response = requests.post(BASE + 'peers/Daniel', json = data)
print(response)

print('post Adrian')
response = requests.post(BASE + 'peers/Adrian', json = data)
print(response)

print('get Daniel')
response = requests.get(BASE + 'peers/Daniel')
print(response.json())

baddata = { 
    'IP': '127.0.0.1:5000', 
    'port': 80,
    'password': 'wordpass'
}
print('delete Daniel w/ wrong password')
response = requests.delete(BASE + 'peers/Daniel', json = baddata)
print(response)

print('get all')
response = requests.get(BASE + 'peers/')
print(response.json())





