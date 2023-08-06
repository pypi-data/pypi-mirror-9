import hmac
import hashlib
import base64
import time
import sys, traceback
try:
    from urllib.parse import quote_plus
    from urllib.parse import urlencode
except:
    from urllib import quote_plus
    from urllib import urlencode

import requests
import json

TIMEOUT = 5
VERIFY_SSL = True
DEBUG = False

_methods = ("GET", "POST", "PUT", "PATCH", "DELETE")
_b64alt = bytes("-_".encode("utf-8"))

def _is_valid_time(ts, expire_seconds):
    '''Validates that the given timestamp `ts` is within `expire_seconds`
    of the current UTC time.
    '''
    try:
        ts = int(ts)
    except ValueError:
        return False
    now = int(time.time())
    duration = now - ts
    if duration < 0:
        duration = duration  * -1
    return duration <= expire_seconds

def _sig(query_string, private_key):
    '''Signs a query-string with the given private key,
    and appends it to the query-string as "&data=###".
    '''
    enc_key = bytes(private_key.encode("utf-8"))
    enc_query = bytes(query_string.encode("utf-8"))
    h = hmac.new(enc_key, msg=enc_query, digestmod=hashlib.sha256).digest()
    return base64.b64encode(h, altchars=_b64alt).decode()

def _sig_part(query, key):
    ''' return an escaped query-string KVP.
    '''
    if isinstance(query[key], list):
        if len(query[key]) > 0 and isinstance(query[key][0], bytes):
            sep = b','
        else:
            sep = ','
        quoted_value = quote_plus(sep.join(sorted(query[key])))
    else:
        quoted_value = quote_plus(query[key])
    return "%s=%s" % (quote_plus(key), quoted_value)

def _sign(private_key, method, query):
    query_string = '&'.join(map(lambda key: _sig_part(query, key), sorted(query)))
    s = "%s:%s" % (method.upper(), query_string)
    return query_string, _sig(s, private_key)

def sign_query(private_key, method, query):
    '''Signs the given query-string dictionary, query, with the given key.
    '''
    query["ts"] = str(int(time.time()))
    query_string, data = _sign(private_key, method, query)
    return "%s&data=%s" % (query_string, data)

def sign(key, private_key, method, url, query={}):
    '''Returns a signed URL.
    '''
    query["apikey"] = key
    query_string = sign_query(private_key, method, query=query)
    return "%s?%s" % (url, query_string)

def validate(private_key, query, expire_seconds, method="GET"):
    '''Validates that the given query `data` value
    matches the signature generated from the given `private_key`
    and query values.
    '''
    if expire_seconds == -1:   # Ignore expire time
        pass
    elif expire_seconds == -2: # Disable security
        del(query["data"])
        del(query["apikey"])
        del(query["ts"])
        return (200, None)
    else:                      # Validate timestamp
        ts = query.get("ts")
        if not ts:
            return (406, "Missing `ts` from query-string.")
        if isinstance(ts, list):
            ts = ts[0]
        if not _is_valid_time(ts, expire_seconds):
            if isinstance(ts, bytes):
                ts = ts.decode()
            return (406, "Expired or invalid timestamp given: `%s`" % (ts,))

    # Get the `data` param as a string.
    if "data" in query:
        data = query["data"]
        if isinstance(data, list):
            data = data[0]
        if isinstance(data, bytes):
            data = data.decode()
        del(query["data"])
    else:
        data = ''

    # Generate and compare the signatures.
    _, sig = _sign(private_key, method, query)
    if sig != data:
        return (401, "signature mismatch, `%s` != `%s`" % (sig, data))
    return (200, None)

def request(key, private_key, url, method="GET", query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes a request.
    returns a request.
    '''
    if method not in _methods:
        raise Exception("Invalid HTTP method, {}.".format(method))

    signed_url = sign(key, private_key, method, url, query=query)
    if DEBUG:
        print("hancock: ", signed_url)
    return requests.__dict__[method.lower()](signed_url, data=data, timeout=TIMEOUT, verify=VERIFY_SSL)

def get(key, private_key, url, query={}, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes GET request.
    '''
    return request(key, private_key, url, query=query, timeout=TIMEOUT, verify_ssl=VERIFY_SSL)

def post(key, private_key, url, query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes POST request.
    '''
    return request(key, private_key, url, method="POST", query=query, data=data, timeout=TIMEOUT, verify_ssl=VERIFY_SSL)

def put(key, private_key, url, query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes PUT request.
    '''
    return request(key, private_key, url, method="PUT", query=query, data=data, timeout=TIMEOUT, verify_ssl=VERIFY_SSL)

def delete(key, private_key, url, query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes DELETE request.
    '''
    return request(key, private_key, url, method="DELETE", query=query, data=data, timeout=TIMEOUT, verify_ssl=VERIFY_SSL)
