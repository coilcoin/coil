# tx.py

# An Input
# { prevTransHash: [somehash], index: [someindex] }

# An Output
# { address: [someaddress], amount: [someamount] }

import chash

def createInput(transaction, index):
	return { 
		"prevTransHash": transaction.hash(),
		"index": index
	}

def createOutput(address, amount):
	return {
		"address": address,
		"amount": amount
	}

class Transaction(object):
	def __init__(self, address, inputs, outputs):
		self.address = address
		self.inputs = inputs
		self.outputs = outputs

	def sign(self, sig):
		self.signature = sig

	def hash(self):
		h = dict(self.__dict__)
		del h["address"]
		# del h["signature"]
		return chash.doubleHashEncodeJSON(self.__dict__)

class Coinbase(Transaction):
	def __init__(self, minerAddress, amount=50):
		# Base reward for mining a block
		# is 50 coilcoins (no fees)
		inputs = []
		outputs = [createOutput(minerAddress, amount)]

		super(Coinbase, self).__init__(minerAddress, inputs, outputs)