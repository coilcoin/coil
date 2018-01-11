# hash.py
# Some useful hashing methods

import hashlib

def doubleHash(input):
    return hashlib.sha256(hashlib.sha256(input).digest()).hexdigest()

def doubleHashEncode(input):
    return doubleHash(input.encode("utf8"))

def doubleHashEncodeJSON(input):
    return doubleHashEncode(str(input))
