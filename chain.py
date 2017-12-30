# chain.py

import chash
import block
import proof
import wallet
import merkle
import tx

# Chain is responsible for...
# 1. Verifying transactions
# 2. Maintaining the mempool
# 3. Verifying blocks
# 4. Maintaining the blockchain

def hashTransDict(d):
	# Delete Wallet
	if "address" in d:
		del d["address"]
	return chash.doubleHashEncodeJSON(d)

def calculateInflow(chain, tx):
	totalIn = 0
	for i in tx.inputs:
		block = chain[i["index"]]
		# Check that output index points to
		# a valid transaction output
		transaction = None
		for t in block.transactions:
			# Transaction must be converted
			# to dictionary since genesis
			# is also a dictionary
			if t.hash() == i["prevTransHash"]:
				transaction = t
			else:
				# Input Transaction does not exist
				return False

		# Does the current input specify
		# an amount to be given
		foundAmount = False
		for o in transaction.outputs:
			if o["address"] == tx.address:
				totalIn += o["amount"]
				foundAmount = True

		# If no amount given to address,
		# transaction must be invalid
		if not foundAmount:
			return False

	return totalIn

def calculateOutflow(tx):
	totalOut = 0
	for o in tx.outputs:
		totalOut += o["amount"]

	return totalOut

def verifyTransaction(chain, tx):
	# Verify that a single wallet
	# owns all of the inputs
	for i in tx.inputs:
		if i["address"] != tx.address:
			return False 

	# Verify that the wallet of
	# the tx has signed the tx
	# address, message, signature
	if not wallet.verifySignature(tx.address, tx.hash(), tx.signature):
		return False

	# Verify that the wallet has
	# sufficient funds
	totalIn = calculateInflow(chain, tx)
	totalOut = calculateOutflow(tx)

	if totalIn:
		# If funds are sufficient
		if totalIn >= totalOut:
			return True

	return False

def verifyBlock(chain, prevBlockHash, nonce, transactionHashes):
	# Verify Proof of Work
	if proof.validProof(prevBlockHash, nonce):
		# TODO: Verify that hashes are in the mempool
		return True
	else:
		return False

class Chain(object):
	def __init__(self, creator, genesis=None, chain=[]):
		self.chain = []
		self.mempool = set()

		# self.creator should be an address
		self.creator = creator

		# Create genesis block
		self.genesis = block.Genesis(self.creator)
		self.chain.append(self.genesis)

		print("Genesis Hash", self.genesis.transactions[0].hash())

	@property
	def blockHeight(self):
		return len(self.chain)

	@property
	def lastBlock(self):
		return self.chain[-1]

	def appendTransaction(self, transaction):
		if verifyTransaction(self.chain, transaction):
			self.mempool.add(transaction)
			return True
		else:
			return False

	def appendBlock(self, minerAddress, prevBlockHash, nonce, transactionHashes):
		if verifyBlock(self.chain, prevBlockHash, nonce, transactionHashes):
			# Select transactions
			txs = []
			for tr in self.mempool:
				for th in transactionHashes:
					if tr.hash() == th:
						txs.append(tr)

			# Create Coinbase for Miner
			txs.append(tx.Coinbase(minerAddress))

			# Generate Merkle Root
			txs_dict = [ str(t.__dict__) for t in txs ]
			mr = merkle.generateMerkleRoot(txs_dict)

			# Add new block
			b = block.Block(self.lastBlock.hash(), nonce, txs, mr)
			self.chain.append(b)
	
			# Remove mined transactions from pool
			# for tr in txs:
			# 	self.mempool.remove(tr)

			return True
		else:
			return False

	def displayJSON(self):
		import json

		newchain = []
		for block in self.chain:
			newblock = block.__dict__
			newtransactions = []

			for t in newblock["transactions"]:
				if type(t).__name__ != "dict":
					# tx = t.__dict__
					# Export wallets as { "importKey": "[PEM]" }
					# t.wallet = { "importKey": str(t.wallet.importKey) }
					newtransactions.append(t.__dict__)
				else:
					newtransactions.append(t)

			newblock["transactions"] = newtransactions
			newchain.append(newblock)

		return json.dumps(newchain)