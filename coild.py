# coild.py
# Coil Daemon
# Primitive Cryptocurrency
# Written by Jesse Sibley
# MIT Licence (@chickencoder)

# API Overview
# /chain/<opt_block_no>
# /chain/last
# /join/<address:port>
# /resolve/peers
# /tx
# /mine
# /ping

__version__ = "0.1.0"

from coil.wallet import readWallet, writeWallet, Wallet
from coil.node import Node

from time import time
from flask import Flask, Response, jsonify
app = Flask(__name__)

# Initialize default node wallet

################################################
# creator = Wallet()
# writeWallet("default.pem", creator)
################################################

creator = readWallet("master.pem")
node = Node(creator.address, creator.publicKeyHex)

def respondPlain(txt):
    return Response(response=txt, content_type="application/json")

def respondMessage(txt):
    msg = '{ message: "' + txt + '"}'
    return Response(response=msg, content_type="application/json")

@app.route("/ping/")
def ping():
    return jsonify(time=time())

@app.route("/chain/")
@app.route("/chain/<index>/")
def chain(index=None):
    if index:
        try:
            return respondPlain(node.getBlock(int(index)))
        except Exception:
            return respondMessage("Invalid block index.")
    else:
        return respondPlain(node.getChain())

@app.route("/chain/last/")
def last():
    return respondPlain(node.getLastBlock())

@app.route("/join/<address>/")
def join(address):
    peers = node.registerPeer(address)
    return respondPlain(peers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337, debug=True)