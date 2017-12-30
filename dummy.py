# dummy.py

# This creates a fake node
# hosting a random chain

from aiohttp import web
from wallet import Wallet
from node import Node

app = web.Application()

# Change this soon to a
# stored wallet
node_creator = Wallet()
node = Node(node_creator)

async def chain(request):
	return web.Response(text=node.getChain(), content_type="application/json")

app.router.add_get("/chain", chain)

web.run_app(app, host="127.0.0.1", port=8080)
print("RUNNING DUMMY NODE")