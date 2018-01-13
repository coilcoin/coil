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
    h1 = chash.doubleHashEncode(pubkey)
    h2 = chash.doubleHashEncode(str(SPECIAL_NUMBER) + h1)
    return h2[:26]

def verifySignature(pubkey, message, signature):
    verifier = PKCS1_v1_5.new(pubkey)
    h = SHA.new(message.encode("utf8"))
    return verifier.verify(h, binascii.unhexlify(signature))

def exportWallet(wallet):
    return { "privateKey": wallet.privateKeyHex, "publicKey": wallet.publicKeyHex }

def writeWallet(privfilename, pubfilename, wallet):
    f = open(privfilename, "wb")
    f.write(wallet.privateKey.exportKey("PEM"))
    f.close()

    f = open(pubfilename, "wb")
    f.write(wallet.publicKey.exportKey("PEM"))
    f.close()

def readWallet(privfilename, pubfilename):
    pri = open(privfilename, "rb").read()
    pub = open(pubfilename, "rb").read()

    return Wallet(privateKey=pri, publicKey=pub)

class Wallet(object):
    def __init__(self, privateKey=None, publicKey=None):
        if privateKey == None or publicKey == None:
            generator = Crypto.Random.new().read
            self.privateKey = RSA.generate(1024, generator)
            self.publicKey = self.privateKey.publickey()
        else:
            self.privateKey = RSA.importKey(privateKey)
            self.publicKey = RSA.importKey(publicKey)

        self.publicKeyHex = binascii.hexlify(self.publicKey.exportKey("PEM")).decode("utf8")
        self.privateKeyHex = binascii.hexlify(self.privateKey.exportKey("PEM")).decode("utf8")
        self.address = generateAddress(self.publicKeyHex)
        self.signature = PKCS1_v1_5.new(self.privateKey)

    def sign(self, message):
        h = SHA.new(message.encode("utf8"))
        return binascii.hexlify(self.signature.sign(h)).decode("ascii")