# pubfrompriv.py

import sys
from Crypto.PublicKey import RSA

filename = sys.argv[1]

f = open(filename, "r")
key = f.read()

public = RSA.importKey(key).publickey()
print(public.exportKey("PEM"))