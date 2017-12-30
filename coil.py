# Coil
# Primitive Cryptocurrency
# Written by Jesse Sibley
# MIT Licence (@chickencoder)

__version__ = "0.1.0"

import json
import base64
from aiohttp import web
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCoo

from wallet import Wallet
from tx import Transaction
from node import Node

# Change this soon to a
# stored wallet
node_creator = Wallet()
node = Node(node_creator.address)

def respond(message):
	txt = json.dumps({ "message": message })
	return web.Response(text=respond(), content_type="application/json") 

# Routes
async def index(request):
	""" Display META information """
	return respond(f"Coil instance running at {node.host}:{node.port} v{__version__}")

async def chain(request):
	""" Return JSON object of Node's chain"""
	return respond(node.getChain())

async def block(request):
	""" Return JSON object of last block"""
	lastBlock = json.dumps(node.chain.lastBlock.__dict__)
	return respond(lastBlock)

async def resolve(request):
	""" Resolve conflicts in chain with peers """
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

	if "importKey" in data and "label" in data:
		wallet = None
		if data["importKey"]:
			wallet = Wallet(importKey=data["privateKey"])
		else:
			wallet = Wallet()

		# Store wallet in wallet bank
		sessions["wallets"][label] = wallet

		return respond(f"Successfully created wallet '{label}'")

	else:
		return respond("Invalid request data")

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

		wallet = session["wallets"][label]

		if wallet:
			tx = Transaction(wallet, inputs, outputs)
			success = node.chain.appendTransaction(tx)

			if success:
				return respond("Transaction Successful")
			else:
				return respond("Transaction Failed")
		else:
			return respond("Wallet not found")

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

	return app

web.run_app(make_app(), host=node.host, port=node.port)