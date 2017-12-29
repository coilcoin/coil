# Coil
# Primitive Cryptocurrency
# Written by Jesse Sibley
# MIT Licence (@chickencoder)

__version__ = "0.1.0"

from aiohttp import web
from wallet import Wallet
from node import Node

app = web.Application()

# Change this soon to a
# stored wallet
node_creator = Wallet()
node = Node(node_creator.address)

# Routes
async def index(request):
	return web.Response(text=f"Coil instance running at {node.host}:{node.port} v{__version__}")

async def chain(request):
	return web.Response(text=node.getChain(), content_type="application/json")

app.router.add_get("/", index)
app.router.add_get("/chain", chain)

web.run_app(app, host=node.host, port=node.port)