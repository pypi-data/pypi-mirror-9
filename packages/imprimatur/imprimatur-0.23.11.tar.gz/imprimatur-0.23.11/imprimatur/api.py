import requests
import re
import time
from six import text_type
import traceback


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
    try:
        reqs = eval(script_str)
    except SyntaxError:
        yield "Problem with script: " + traceback.format_exc()
        return

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

        try:
            tries = req['tries']
        except KeyError:
            tries = {'max': 1, 'period': 1}

        try:
            max_tries = tries['max']
        except KeyError:
            max_tries = 10

        try:
            period = tries['period']
        except KeyError:
            period = 1

        j = 0
        failed = True
        msg = None
        while failed and j < max_tries:
            if j > 0:
                time.sleep(period)
            j += 1
            try:
                yield "Request: " + url + "\n"
                r = requests.request(
                    method, url, files=files, data=data, allow_redirects=False,
                    auth=auth)
            except requests.exceptions.InvalidURL as e:
                yield "Invalid URL: " + str(e) + '\n'
                break

            if 'status_code' in req:
                req_status_code = int(req['status_code'])
                if r.status_code != req_status_code:
                    msg = "The desired status code " + str(req_status_code) + \
                        " doesn't match the actual status code " + \
                        str(r.status_code) + ".\n" + response_str(r)
                    continue

            if 'regexes' in req:
                regex_failed = False
                k = 0
                while not regex_failed and k < len(req['regexes']):
                    pattern = req['regexes'][k]
                    k += 1
                    if re.search(
                            pattern, response_str(r),
                            flags=re.MULTILINE | re.DOTALL) is None:
                        regex_failed = True
                if regex_failed:
                    msg = "The regular expression '" + pattern + \
                        "' fails.\n" + response_str(r)
                    continue

            failed = False

        if failed:
            yield msg
            break

    if not failed:
        yield "Passed all tests!\n"
        yield None
