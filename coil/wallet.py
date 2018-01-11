# wallet.py
from coil import key
from coil import chash

import binascii
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

def generateAddress(pubkey):
    # Use network key in address
    SPECIAL_NUMBER = key.activation_key
    h1 = chash.doubleHashEncode(str(pubkey))
    h2 = chash.doubleHashEncode(str(SPECIAL_NUMBER) + h1)
    return h2[:26]

def verifySignature(pubkey, message, signature):
    verifier = PKCS1_v1_5.new(pubkey)
    h = SHA.new(message.encode("utf8"))
    return verifier.verify(h, binascii.unhexlify(signature))

def exportWallet(wallet):
    return { "importKey": wallet.importKey.decode("utf8") }

def writeWallet(filename, wallet):
    f = open(filename, "wb")
    f.write(wallet.importKey)
    f.close()

def readWallet(filename):
    f = open(filename, "rb")
    return Wallet(importKey=f.read())

class Wallet(object):
    def __init__(self, importKey=None):
        if not importKey:
            generator = Crypto.Random.new().read
            self.privateKey = RSA.generate(1024, generator)
            self.importKey = self.privateKey.exportKey("PEM")
        else:
            self.importKey = importKey
            self.privateKey = RSA.importKey(self.importKey)

        self.publicKey = self.privateKey.publickey()
        self.address = generateAddress(self.publicKey)
        self.publicKeyHex = binascii.hexlify(self.publicKey.exportKey("PEM")).decode("utf8")
        self.privateKeyHex = binascii.hexlify(self.privateKey.exportKey("PEM")).decode("utf8")
        self.signature = PKCS1_v1_5.new(self.privateKey)

    def sign(self, message):
        h = SHA.new(message.encode("utf8"))
        return binascii.hexlify(self.signature.sign(h)).decode("ascii")