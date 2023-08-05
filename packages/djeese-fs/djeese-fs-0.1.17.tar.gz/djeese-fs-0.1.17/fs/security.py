# -*- coding: utf-8 -*-
import hashlib
import hmac
import urllib


# START: COPIED FROM DJANGO
def _constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0
# END: COPIED FROM DJANGO


def sign(key, data):
    data = urllib.urlencode(sorted(data.items()))
    signature = hmac.new(str(key), str(data), digestmod=hashlib.sha256).hexdigest()
    return signature


def verify(key, signature, data):
    expected = sign(key, data)
    return _constant_time_compare(signature, expected)
