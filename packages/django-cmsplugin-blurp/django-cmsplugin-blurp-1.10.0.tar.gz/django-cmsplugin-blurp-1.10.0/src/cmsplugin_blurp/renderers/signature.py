import datetime
import base64
import hmac
import hashlib
import urllib
import random
import urlparse

'''Simple signature scheme for query strings'''

def sign_url(url, key, algo='sha256', timestamp=None, nonce=None):
    parsed = urlparse.urlparse(url)
    new_query = sign_query(parsed.query, key, algo, timestamp, nonce)
    return urlparse.urlunparse(parsed[:4] + (new_query,) + parsed[5:])

def sign_query(query, key, algo='sha256', timestamp=None, nonce=None):
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()
    timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    if nonce is None:
        nonce = hex(random.getrandbits(128))[2:]
    new_query = query
    if new_query:
        new_query += '&'
    new_query += urllib.urlencode((
        ('algo', algo),
        ('timestamp', timestamp),
        ('nonce', nonce)))
    signature = base64.b64encode(sign_string(new_query, key, algo=algo))
    new_query += '&signature=' + urllib.quote(signature)
    return new_query

def sign_string(s, key, algo='sha256', timedelta=30):
    digestmod = getattr(hashlib, algo)
    hash = hmac.HMAC(key, digestmod=digestmod, msg=s)
    return hash.digest()

def check_url(url, key, known_nonce=None, timedelta=30):
    parsed = urlparse.urlparse(url, 'https')
    return check_query(parsed.query, key)

def check_query(query, key, known_nonce=None, timedelta=30):
    parsed = urlparse.parse_qs(query)
    signature = base64.b64decode(parsed['signature'][0])
    algo = parsed['algo'][0]
    timestamp = parsed['timestamp'][0]
    timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    nonce = parsed['nonce']
    unsigned_query = query.split('&signature=')[0]
    if known_nonce is not None and known_nonce(nonce):
        return False
    print 'timedelta', datetime.datetime.utcnow() - timestamp
    if abs(datetime.datetime.utcnow() - timestamp) > datetime.timedelta(seconds=timedelta):
        return False
    return check_string(unsigned_query, signature, key, algo=algo)

def check_string(s, signature, key, algo='sha256'):
    # constant time compare
    signature2 = sign_string(s, key, algo=algo)
    if len(signature2) != len(signature):
        return False
    res = 0
    for a, b in zip(signature, signature2):
        res |= ord(a) ^ ord(b)
    return res == 0

if __name__ == '__main__':
    test_key = '12345'
    signed_query = sign_query('NameId=_12345&orig=montpellier', test_key)
    assert check_query(signed_query, test_key, timedelta=0) is False
    assert check_query(signed_query, test_key) is True
