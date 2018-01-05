# Coil
# Primitive Cryptocurrency
# Written by Jesse Sibley
# MIT Licence (@chickencoder)

__version__ = "0.1.0"

import json
import base64
from cryptography import fernet
from Crypto.PublicKey import RSA

import aiohttp_cors
from aiohttp import web
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from wallet import Wallet, exportWallet
from tx import Transaction
from node import Node

# pk = open("../wallet.pem", "r").read().strip()
# node_creator = Wallet(importKey=pk)

# Uncomment line below not creator
node_creator = Wallet()

node = Node(node_creator.address)

# Write out details for use in wallet
f = open("wallet.pem", "wb")
f.write(node_creator.importKey)
f.close()

f = open("address", "w")
f.write(str(node_creator.address))
f.close()

f = open("pubkey", "w")
f.write(str(node_creator.publicKey.exportKey()))
f.close()

def respond(message):
	txt = json.dumps({ "message": message })
	return web.Response(text=txt, content_type="application/json") 

def respondJSON(message):
	txt = json.dumps(message)
	return web.Response(text=txt, content_type="application/json")

def respondPlain(message):
	return web.Response(text=message, content_type="application/json")

# Routes
async def index(request):
	""" Display META information """
	return respond(f"Coil instance running at {node.host}:{node.port} v{__version__}")

async def chain(request):
	""" Return JSON object of Node's chain"""
	return respondPlain(node.getChain())

async def block(request):
	""" Return JSON object of last block"""
	lastBlock = node.chain.lastBlock
	return respondPlain(lastBlock.json())

async def balance(request):
	""" Return balance for an address
	{ address: <> }
	"""

	data = await request.post()
	address = data["address"]
	
	if "address" in data:
		balance = 0
		for block in node.chain.chain:
			for tx in block.transactions:
				# This is annoying. Must fix
				if type(tx).__name__ != "dict":
					tx = tx.__dict__

				if tx["address"] == address:
					for o in tx["outputs"]:
						if not tx["inputs"] == []: 
							balance -= o["amount"]

				for o in tx["outputs"]:
					if o["address"] == address:
						# Ignore Coinbase
						if tx["inputs"] == []:
							balance += o["amount"]

		return respondJSON({"address": address, "balance": balance})
	else:
		return respond("Invalid Request Data")

async def last_block_hash(request):
	""" Returns hash of last block"""
	return respond(node.chain.lastBlock.hash())

async def resolve(request):
	""" Resolve conflicts in chain with peers """
	# Visit all peers, collect the length of chains
	# 
	return respond(node.getChain())

async def new_wallet(request):
	"""
	Handle Random Wallet

	request...
	{ importWallet: true, privateKey: "[blah]", label: "mywallet" }

	or...
	{ importWallet: false }
	"""

	data = await request.post()
	session = await get_session(request)

	if "importWallet" in data:
		label = data["label"]
		wallet = None
		if data["importWallet"] == "true":
			wallet = Wallet(importKey=data["privateKey"])
		else:
			wallet = Wallet()

		# Store wallet in wallet bank
		session["wallet"] = exportWallet(wallet)

		return respond(f"Successfully created wallet '{label}'")

	else:
		return respond("Invalid request data")

async def new_wallet_get(request):
	"""
	Handle Random Wallet
	"""
	session = await get_session(request)
	wallet = Wallet()

	session["wallet"] = exportWallet(wallet)

	return respondJSON({"message": "Successfully created wallet", "privateKey": session["wallet"]["importKey"], "address": wallet.address})

async def new_transaction(request):
	"""
	Process a new transaction

	expects...
	{ wallet: "key", inputs: [  ], outputs: [ ] }
	"""

	data = await request.json()

	if 'wallet' in data and 'inputs' in data and 'outputs' in data:
		# Retrieve Wallet
		inputs = data["inputs"]
		outputs = data["outputs"]
		label = data["wallet"]

		# Fetch wallet
		# wallet_export = session["wallet"]
		wallet = Wallet(importKey=label)
		if wallet:
			tx = Transaction(wallet.address, inputs, outputs, wallet.publicKey)
			tx.sign(wallet.sign(tx.hash()))

			success = node.chain.appendTransaction(tx)

			if success:
				return respondJSON({"message": "Transaction Successful", "blockHash": node.chain.lastBlock.hash() } )
			else:
				return respond("Transaction Failed")
		else:
			return respond("Wallet not found")

	else:
		return respond("Invalid request data")

async def mine_block(request):
	"""
	Mine a block
	
	expects...
	{
		"minerAddress": <blah>
		"previousBlockHash": <balh>
		"nonce": <blah>,
		"transactionHashes": [<blah>...]
	}
	"""
	data = await request.post()

	if "minerAddress" in data and "minerPubKey" in data \
		and "previousBlockHash" in data and \
		"nonce" in data and "transactionHashes" in data:

		address = data["minerAddress"]
		minerPubKey = data["minerPubKey"]
		previousBlockHash = data["previousBlockHash"]
		nonce = data["nonce"]
		transactionHashes = data["transactionHashes"]

		pubkey = RSA.importKey(minerPubKey)
		success = node.chain.appendBlock(address, minerPubKey, previousBlockHash, nonce, transactionHashes)

		# RESOLVE CHAIN

		if success:
			return respond("Succesfully mine a block")
		else:
			return respond("Could not mine a block")
	else:
		return respond("Invalid request data")

def make_app():
	app = web.Application()
	fernet_key = fernet.Fernet.generate_key()
	secret_key = base64.urlsafe_b64decode(fernet_key)
	setup(app, EncryptedCookieStorage(secret_key))

	app.router.add_get("/", index)
	app.router.add_get("/chain", chain)
	app.router.add_get("/chain/resolve", resolve)
	app.router.add_get("/block", block)
	app.router.add_get("/block/hash", last_block_hash)
	app.router.add_get("/wallet/new", new_wallet_get)
	app.router.add_post("/wallet", new_wallet)
	app.router.add_post("/transaction/new", new_transaction)
	app.router.add_post("/mine", mine_block)
	app.router.add_post("/balance", balance)

	return app

web.run_app(make_app(), host=node.host, port=node.port)