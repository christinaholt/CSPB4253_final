
import requests
import json
import time
import sys, os
import jsonpickle


host, cmd, date, fcst, field, level = sys.argv[1:]

addr = f'http://{host}'

if cmd == 'map':
    headers = {'content-type': 'application/json'}
    url = f'{addr}/plot/map'
    data = {
        'start': date,
        'fcst': fcst,
        'field': field,
        'level': level,
        }
    response = requests.post(
            url,
            data=jsonpickle.encode(data),
            headers=headers)

else:
    print(f'Unknown option for cmd: {cmd}')
