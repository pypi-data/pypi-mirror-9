import hmac
import hashlib
import base64
import time
import sys, traceback

try:
    from urllib.parse import quote_plus as encode_query
except:
    from urllib import quote_plus as encode_query

import requests
import simplejson as json

TIMEOUT = 5
VERIFY_SSL = True

_methods = ("GET", "POST", "PUT", "PATCH", "DELETE")
_b64alt = bytes("-_".encode("utf-8"))

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
    return "%s=%s" % (encode_query(key), encode_query(query[key]))

def _sign(private_key, method, query):
    query["ts"] = str(int(time.time()))
    query_string = '&'.join(map(lambda key: _sig_part(query, key), sorted(query)))
    s = "%s:%s" % (method.upper(), query_string)
    return query_string, _sig(s, private_key)

def sign_query(private_key, method, query):
    '''Signs the given query-string dictionary, query, with the given key.
    '''
    query_string, data = _sign(private_key, method, query)
    return "%s&data=%s" % (query_string, data)

def sign(key, private_key, method, url, query={}):
    '''Returns a signed URL.
    '''
    query["apikey"] = key
    query_string = sign_query(private_key, method, query=query)
    return "%s?%s" % (url, query_string)

def validate(private_key, query, method="GET"):
    data = query["data"]
    del(query["data"])
    sig = _sign(private_key, method, query)
    return sig == data

def request(key, private_key, url, method="GET", query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes a request.
    returns a request.
    '''
    if method not in _methods:
        raise Exception("Invalid HTTP method, {}.".format(method))

    signed_url = sign(key, private_key, method, url, query=query)
    return requests.__dict__[method.lower()](signed_url, data=data, timeout=timeout, verify=verify_ssl)

def get(key, private_key, url, query={}, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes GET request.
    '''
    return request(key, private_key, url, query=query, timeout=timeout, verify_ssl=verify_ssl)

def post(key, private_key, url, query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes POST request.
    '''
    return request(key, private_key, url, method="POST", query=query, data=data, timeout=timeout, verify_ssl=verify_ssl)

def put(key, private_key, url, query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes PUT request.
    '''
    return request(key, private_key, url, method="PUT", query=query, data=data, timeout=timeout, verify_ssl=verify_ssl)

def delete(key, private_key, url, query={}, data=None, timeout=TIMEOUT, verify_ssl=VERIFY_SSL):
    '''Signs the given url with the given key and invokes DELETE request.
    '''
    return request(key, private_key, url, method="DELETE", query=query, data=data, timeout=timeout, verify_ssl=verify_ssl)
