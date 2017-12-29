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
	def __init__(self, wallet, inputs, outputs):
		self.wallet = wallet
		self.inputs = inputs
		self.outputs = outputs

	def hash(self):
		h = dict(self.__dict__)
		del h["wallet"]
		print(h)
		return chash.doubleHashEncodeJSON(self.__dict__)

class Coinbase(Transaction):
	def __init__(self, minerAddress):
		# Base reward for mining a block
		# is 50 coilcoins (no fees)
		inputs = []
		outputs = [createOutput(minerAddress, 50)]

		super(Coinbase, self).__init__(minerAddress, inputs, outputs)