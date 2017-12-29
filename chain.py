# chain.py

import chash
import block
import proof
import tx

# Chain is responsible for...
# 1. Verifying transactions
# 2. Maintaining the mempool
# 3. Verifying blocks
# 4. Maintaining the blockchain

def calculateInflow(chain, tx):
	totalIn = 0
	for i in tx.inputs:
		block = chain[i["index"]]
		# Check that output index points to
		# a valid transaction output
		transaction = None
		for t in block.transactions:
			print(t.hash()) # Genesis
			print(i["prevTransHash"])
			if t.hash() == i["prevTransHash"]:
				print("MATCH")
				transaction = t
			else:
				# Input Transaction does not exist
				return False

		# Does the current input specify
		# an amount to be given
		foundAmount = False
		for o in transaction["outputs"]:
			if o.address == tx.wallet.address:
				totalIn += o.amount
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
	totalIn = calculateInflow(chain, tx)
	totalOut = calculateOutflow(tx)

	if totalIn:
		print(totalIn)
		print(totalOut)

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
	def __init__(self, creator):
		self.chain = []
		self.mempool = set()
		self.creator = creator

		# Create genesis block
		genesis = block.Genesis(self.creator)
		self.chain.append(genesis)

	@property
	def blockHeight(self):
		return len(self.chain)

	@property
	def lastBlock(self):
		return self.chain[-1]

	def appendTransaction(self, transaction):
		if verifyTransaction(self.chain, transaction):
			mempool.add(transaction)
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

			# TODO: FIX THIS TXS HASHES
			# FIX: JUST USE ALL TRANSITIONS
			txs = list(self.mempool)

			# Create Coinbase for Miner
			txs.append(tx.Coinbase(minerAddress))

			# TODO: Create Merkle Root
			mr = ""

			# Add new block
			b = block.Block(self.lastBlock.hash(), nonce, txs, mr)
			self.chain.append(b)
	
			# Remove mined transactions from pool
			# for tr in txs:
			# 	self.mempool.remove(tr)

			return True
		else:
			return False

	def display(self):
		print("Block height:", self.blockHeight)
		newchain = []
		for block in self.chain:
			newblock = block.__dict__
			newblock["transactions"] = [ t.__dict__ for t in block.transactions ]
			newchain.append(newblock)

		print(newchain)