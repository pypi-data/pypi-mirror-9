import requests
import re
import time
from six import text_type


def response_str(response):
    headers = response.headers
    res = []
    for k in sorted(headers.keys()):
        res.append(str((k, headers[k])) + '\n')
    res.append('\n')
    res.append(text_type(response.content, response.apparent_encoding))
    return ''.join(res)

KEYS = frozenset([
    'host', 'name', 'port', 'scheme', 'regexes', 'status_code', 'auth', 'path',
    'files', 'method', 'data', 'tries'])

CARRIED = frozenset(('host', 'port', 'scheme', 'auth'))


def run(script_str):
    reqs = eval(script_str)
    defreq = {
        'host': 'localhost', 'port': 80, 'scheme': 'http'}
    failed = False
    for req in reqs:
        unrec = set(req.keys()) - KEYS
        if len(unrec) > 0:
            failed = True
            yield "The keys " + str(unrec) + " aren't recognized."
            break

        for k in CARRIED & set(req.keys()):
            defreq[k] = req[k]

        url = defreq['scheme'] + '://' + defreq['host'] + ':' + \
            str(defreq['port']) + req['path']

        try:
            auth = defreq['auth']
        except KeyError:
            auth = None

        try:
            method = req['method']
        except KeyError:
            method = 'get'

        try:
            yield "Name: " + req['name'] + '\n'
        except KeyError:
            pass

        try:
            files = dict(
                (k, open(v, 'r')) for k, v in req['files'].items())
        except KeyError:
            files = None

        try:
            data = req['data']
        except KeyError:
            data = None

        yield "Request: " + url + "\n"

        try:
            tries = req['tries']
        except KeyError:
            tries = {'number': 1, 'period': 1}

        try:
            num_tries = tries['number']
        except KeyError:
            num_tries = 1

        try:
            period = tries['period']
        except KeyError:
            period = 1

        for i in range(num_tries):
            if i > 0:
                time.sleep(period)
            try:
                r = requests.request(
                    method, url, files=files, data=data, allow_redirects=False,
                    auth=auth)
            except requests.exceptions.InvalidURL as e:
                failed = True
                yield "Invalid URL: " + str(e) + '\n'
                break

        if 'status_code' in req:
            req_status_code = int(req['status_code'])
            if r.status_code != req_status_code:
                failed = True
                yield "The desired status code " + str(req_status_code) + \
                    " doesn't match the actual status code " + \
                    str(r.status_code) + ".\n" + response_str(r)
                break

        if 'regexes' in req:
            for pattern in req['regexes']:
                if re.search(
                        pattern, text_type(r.content, r.apparent_encoding),
                        flags=re.MULTILINE) is None:
                    failed = True
                    yield "The regular expression '" + pattern + \
                        "' fails.\n" + response_str(r)
                    break

    if not failed:
        yield "Passed all tests!\n"
        yield None
