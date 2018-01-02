# Coil
# Primitive Cryptocurrency
# Written by Jesse Sibley
# MIT Licence (@chickencoder)

__version__ = "0.1.0"

import json
import base64
from cryptography import fernet
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
	{ importWallet: false, label: "mywallet" }
	"""

	data = await request.post()
	session = await get_session(request)

	if not "wallets" in session:
		session["wallets"] = {}

	if "importWallet" in data and "label" in data:
		label = data["label"]
		wallet = None
		if data["importWallet"] == "true":
			wallet = Wallet(importKey=data["privateKey"])
		else:
			wallet = Wallet()

		# Store wallet in wallet bank
		session["wallets"][label] = exportWallet(wallet)

		return respond(f"Successfully created wallet '{label}'")

	else:
		return respond("Invalid request data got ono ")

async def new_wallet_get(request):
	"""
	Handle Random Wallet
	"""
	session = await get_session(request)
	label = request.match_info["label"]

	if not "wallets" in session:
		session["wallets"] = {}

	wallet = Wallet()

	# Store wallet in wallet bank
	session["wallets"][label] = exportWallet(wallet)

	return respond(f"Successfully created wallet '{label}'")

async def get_wallet(request):
	""" Get wallet address (/wallet/label) """
	session = await get_session(request)

	label = request.match_info["label"]

	if label in session["wallets"]:
		wallet = Wallet(importKey=session["wallets"][label]["importKey"])
		return respondJSON({ "label": label, "address": wallet.address })
	else:
		return respond("Undefined wallet label")


async def new_transaction(request):
	"""
	Process a new transaction

	expects...
	{ wallet: "<label>", inputs: [  ], outputs: [ ] }
	"""

	data = await request.post()
	session = await get_session(request)

	if "wallet" in data and "inputs" in data and "outputs" in data:
		# Retrieve Wallet
		inputs = data["inputs"]
		outputs = data["outputs"]
		label = data["wallet"]

		# Fetch wallet
		wallet_export = session["wallets"][label]
		wallet = Wallet(importKey=wallet_export["importKey"])
		if wallet:
			tx = Transaction(wallet.address, inputs, outputs)
			tx.sign(wallet.sign(tx.hash()))

			success = node.chain.appendTransaction(tx)

			if success:
				return respond("Transaction Successful")
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

	if "minerAddress" in data and "previousBlockHash" in data and \
		"nonce" in data and "transactionHashes" in data:

		address = data["minerAddress"]
		previousBlockHash = data["previousBlockHash"]
		nonce = data["nonce"]
		transactionHashes = data["transactionHashes"]
		success = node.chain.appendBlock(address, previousBlockHash, nonce, transactionHashes)

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
	app.router.add_post("/wallet/new", new_wallet)
	app.router.add_get("/wallet/new/{label}", new_wallet_get)
	app.router.add_get("/wallet/{label}", get_wallet)
	app.router.add_post("/transaction/new", new_transaction)
	app.router.add_post("/mine", mine_block)

	return app

web.run_app(make_app(), host=node.host, port=node.port)