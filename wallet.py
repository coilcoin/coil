# wallet.py

import chash

def generateAddress(pubkey):
	SPECIAL_NUMBER = 17111999
	h1 = chash.doubleHashEncode(pubkey)
	h2 = chash.doubleHashEncode(str(SPECIAL_NUMBER) + h1)
	return h2[:25]

class Wallet(object):
	def __init__(self):
		pass