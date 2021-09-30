import requests

data = {'name': 'ue', 'ip': '192.168.1.1', 'port':5500}

requests.post('http://100.1.1.1:6600/start/', data=data)