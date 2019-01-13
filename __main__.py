#!/usr/bin/python3

import json
import socket
import sys
from datetime import datetime, time
from time import sleep


def encode_color(red, green, blue, priority=700):
    if priority < 0:
        priority = 0
    for channel in (red, green, blue):
        if channel < minimum:
            channel = minimum
        elif channel > maximum:
            channel = maximum
    return json.dumps({
            'color': (red, green, blue),
            'command': 'color',
            'priority': priority
        }).encode('utf-8') + b'\n'


def clear_all():
    return json.dumps({'command': 'clearall'}).encode('utf-8') + b'\n'


def status():
    return json.dumps({'command': 'serverinfo'}).encode('utf-8') + b'\n'


def send(data, host='127.0.0.1'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, 19444))
    except:
        raise
    else:
        sock.send(data)
        return sock


def process_response(response):
    try:
        decoded = json.loads(response.decode())
    except json.decoder.JSONDecodeError:
        return False
    try:
        successful = decoded['success']
    except KeyError:
        return False
    else:
        return successful


def wait_for_response(sock):
    try:
        response = sock.recv(8192)
    except socket.error:
        return False
    else:
        return process_response(response)


def send_color(values, host):
    return wait_for_response(send(encode_color(*values), host))


def run(
        color, host='127.0.0.1', start=None, stop=None,
        force=False, sleepTime=4, **kwargs
    ):
    if start is None:
        start = (17, 30)
    if stop is None:
        stop = (23, 59, 59)
    on, off = time(*start), time(*stop)
    while True:
        now = datetime.time(datetime.now())
        if (on < now < off) or force:
            send_color(color, host)
        elif not (on < now < off):
            send_color((minimum for i in range(3)), host)
        sleep(sleepTime)


def parse_args():
    kwargs, explicitKey = {}, None
    for arg in sys.argv[1:]:
        values = arg.split(',')
        times = arg.split(':')
        address = arg.split('.')
        if explicitKey:
            try:
                value = int(arg)
            except:
                value = arg
            kwargs[explicitKey] = value
            explicitKey = None
        if len(values) > 1:
            kwargs['color'] = tuple(int(digit) for digit in values)
        elif len(times) > 1:
            if 'start' not in kwargs.keys():
                kwargs['start'] = tuple(int(digit) for digit in times)
            elif 'stop' not in kwargs.keys():
                kwargs['stop'] = tuple(int(digit) for digit in times)
        elif len(address) == 4 and all(i.isdigit() for i in address):
            kwargs['host'] = arg
        elif arg.startswith('--'):
            explicitKey = arg.lstrip('--')
    return kwargs


if __name__ == '__main__':
    kwargs = parse_args()
    if 'color' not in kwargs.keys():
        kwargs['color'] = 157, 124, 37
    if 'resolution' in kwargs.keys():
        resolution = kwargs.pop('resolution')
    else:
        resolution = 8
    if 'maximum' in kwargs.keys():
        maximum = kwargs.pop('maximum')
    else:
        maximum = (2 ** resolution) - 1
    if 'minimum' in kwargs.keys():
        minimum = kwargs.pop('minimum')
    else:
        minimum = 0
    run(kwargs.pop('color'), **kwargs)