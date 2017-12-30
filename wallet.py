# wallet.py
import key
import chash
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
	return h2[:25]

def verifySignature(address, message, signature):
    pubkey = RSA.importKey(binascii.unhexlify(address))
    verifier = PKCS1_v1_5.new(pubkey)
    h = SHA.new(message.encode('utf8'))
    return verifier.verify(h, binascii.unhexlify(signature))

def exportWallet(wallet):
	return { "importKey": wallet.importKey.decode("utf-8") }

class Wallet(object):
    def __init__(self, importKey=""):
        if not importKey:
            generator = Crypto.Random.new().read
            self.privateKey = RSA.generate(1024, generator)
            self.publicKey = self.privateKey.publickey()
            self.signature = PKCS1_v1_5.new(self.privateKey)
            self.importKey = self.privateKey.exportKey("PEM")
        else:
            self.privateKey = RSA.importKey(importKey.encode("utf-8"))
            self.publicKey = self.privateKey.publickey()
            self.signature = PKCS1_v1_5.new(self.privateKey)
            self.importKey = importKey

        self.address = generateAddress(self.publicKey)

    def sign(self, message):
    	h = SHA.new(message.encode('utf8'))
    	return binascii.hexlify(self.signature.sign(h)).decode("ascii")