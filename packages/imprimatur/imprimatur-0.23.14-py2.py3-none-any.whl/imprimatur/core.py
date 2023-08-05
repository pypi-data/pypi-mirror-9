import requests
import re
import time


def response_str(response):
    headers = response.headers
    res = []
    for k in sorted(headers.keys()):
        res.append(str((k, headers[k])) + '\n')
    res.append('\n')
    res.append(str(response.content, response.apparent_encoding))
    return ''.join(res)


def run(script_str):
    reqs = eval(script_str)
    defreq = {
        'host': 'localhost', 'port': 80, 'scheme': 'http'}
    failed = False
    for req in reqs:
        for k in ('host', 'port', 'scheme'):
            try:
                defreq[k] = req[k]
            except KeyError:
                pass

        url = defreq['scheme'] + '://' + defreq['host'] + ':' + \
            str(defreq['port']) + req['path']

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
                    method, url, files=files, data=data, allow_redirects=False)
            except requests.exceptions.InvalidURL as e:
                failed = True
                yield "Invalid URL: " + str(e) + '\n'
                break

        if 'status_code' in req and r.status_code != req['status_code']:
            failed = True
            yield "The status code doesn't match.\n" + response_str(r)
            break

        if 'regexes' in req:
            for pattern in req['regexes']:
                if re.search(
                        pattern, str(r.content, r.apparent_encoding),
                        flags=re.MULTILINE) is None:
                    failed = True
                    yield "The regular expression '" + pattern + \
                        "' fails.\n" + response_str(r)
                    break

    if not failed:
        yield "Passed all tests!"
        yield None
