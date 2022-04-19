import requests

BASE = 'http://127.0.0.1:5000/'

data = { 
    'IP': '127.0.0.1:5000', 
    'port': 80,
    'password': 'password'
}

def handle_request(response):
    try:
        return response.json()
    except:
        return response

print('get all')
response = requests.get(BASE + 'peers/')
print(handle_request(response))

print('delete Daniel')
response = requests.delete(BASE + 'peers/Daniel', json = data)
print(handle_request(response))

jmdata = {
    'IP': '10.0.0.94', 
    'port': 50000,
    'password': 'hello'
}
print('delete jm')
response = requests.delete(BASE + 'peers/jm', json = jmdata)
print(handle_request(response))

tiffadata = {
    'IP': '10.0.0.94', 
    'port': 50001,
    'password': 'hello'
}
print('delete tiffany')
response = requests.delete(BASE + 'peers/tiffa', json = jmdata)
print(handle_request(response))

print('get Daniel')
response = requests.get(BASE + 'peers/Daniel')
print(handle_request(response))

print('post Daniel')
response = requests.post(BASE + 'peers/Daniel', json = data)
print(handle_request(response))

print('post Daniel')
response = requests.post(BASE + 'peers/Daniel', json = data)
print(handle_request(response))

print('post Adrian')
response = requests.post(BASE + 'peers/Adrian', json = data)
print(handle_request(response))

print('get Daniel')
response = requests.get(BASE + 'peers/Daniel')
print(handle_request(response))

baddata = { 
    'IP': '127.0.0.1:5000', 
    'port': 80,
    'password': 'wordpass'
}
print('delete Daniel w/ wrong password')
response = requests.delete(BASE + 'peers/Daniel', json = baddata)
print(handle_request(response))

print('get all')
response = requests.get(BASE + 'peers/')
print(handle_request(response))





