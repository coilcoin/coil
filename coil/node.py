# node.py
import requests
import json
import sys

from urllib.parse import urlparse
from time import time

from coil.tx import Transaction, Coinbase, createInput
from coil.block import Block
from coil.chain import Chain
from coil.wallet import Wallet

def log(info):
    print(f"[Message] {info}")

def transactionFromDict(d):
    if d["inputs"] == []:
        # Coinbase Transaction
        o = d["outputs"][0]
        return Coinbase(o["address"], amount=o["amount"])
    else:
        inputs = []
        for i in d["inputs"]:
            inputs.append(createInput(i["prevTransHash"], i["index"]))

        outputs = []
        for o in d["outputs"]:
            outputs.append(createOutput(o["address"], o["amount"]))

        return Transaction(d["address"], d["signature"], inputs, outputs)

def blockFromDict(d):
    prevBlockHash = d["previousBlockHash"]
    nonce = d["nonce"]
    txs = [transactionFromDict(t) for t in d["transactions"]]
    merkleRoot = d["merkleRoot"]
    return Block(prevBlockHash, nonce, txs, merkleRoot)

def chainFromResponse(response):
    blocks = [ blockFromDict(b) for b in response ]

    # Get Genesis Block
    genesis = blocks[0]

    # This could be prettier
    creator = genesis.transactions[0].outputs[0]["address"]

    return Chain(creator, genesis=genesis, chain=blocks)

def chainFromPeers(peers):
    # Iterate through peers until a
    # valid chain is found
    peer_index = 0
    while peer_index < len(peers):
        url = "http://" + list(peers)[0] + "/chain"

        try:
            response = requests.get(url)
            return chainFromResponse(response.json())

        except requests.exceptions.RequestException:
            peer_index += 1		

    log("Could not download blockchain from peers.")

class Node(object):
    def __init__(self, creator, creatorPubKey):
        self.peers = set()
        self.chain = None
        self.host = "0.0.0.0"
        self.creator = creator
        self.creatorPubKey = creatorPubKey
        self.mempool = []

        if len(sys.argv) > 1:
            self.port = int(sys.argv[1])
        else:
            self.port = 1337

        # Read Peers
        peers = [ s.strip() for s in open("peers.txt", "r").readlines() ]
        if peers != []:
            for peer in peers:
                parsed_url = urlparse(peer.strip())
                self.peers.add(parsed_url.netloc)
                
                # Attempt to find chain from peers
                # if not, initialize a chain
                self.chain = chainFromPeers(self.peers)
                if not self.chain:
                    self.chain = Chain(self.creator, self.creatorPubKey)
        else:
            self.chain = Chain(self.creator, self.creatorPubKey)

    def ping(self, nodeloc):
        # Pinging a Wire node...
        # expects a plain text
        try:
            response = requests.get("http://" + nodeloc + "/ping").json()
            if response["time"]:
                return True
            else:
                return False

        except requests.exceptions.RequestException:
            # Remove peer from pool
            # & then broastcast
            return False

    def broadcast(self, route):
        # Send a GET request to all registered peers
        # PING all peers, if they're dead... update
        # self.peers
        if self.peers:
            for peer in self.peers.copy():
                if self.ping(peer):
                    requests.get("http://" + peer + route)
                # else:
                    # Remove peer from pool
                    # & then broastcast
                    # self.peers.remove(peer)
                    # self.broadcast("/resolve/peers")

    def registerPeer(self, address):
        parsed_url = urlparse("http://" + address.strip())
        if parsed_url.netloc:
            self.peers.add(parsed_url.netloc)
    
        # Broadcast to all nodes
        self.broadcast("/resolve/peers")

        return self.peers

    def resolvePeers(self):
        peersLists = {}

        for peer in self.peers:
            if self.ping(peer):
                peerList = requests.get("http://" + peer + "/peers").json()
                if peerList:
                    peersLists[peer] = json.loads(peerList)
 
        if peersLists != {}:
            self.peers = sorted(peersList, key=lambda l: len(peersList[l]), reverse=True)[0]

        return self.peers

    def getChain(self):
        fullChain = { "blockHeight": self.chain.blockHeight, "chain": self.chain.displayDict() }
        return json.dumps(fullChain)

    def getBlock(self, index):
        block = self.chain.chain[index].json()
        return block

    def getLastBlock(self):
        return self.chain.lastBlock.json()

    def resolveChain(self):
        maxHeights = {}

        for peer in self.peers.copy():
            if self.ping(peer):
                response = requests.get("http://" + peer + "/chain").json()
                maxHeights[peer] = response["blockHeight"]
            # else:
            #     # Remove peers & resolve
            #     self.peers.remove(peer)
            #     self.broadcast("/resolve/peers") 

        # Replace chain
        if maxHeights != {}:
            response = requests.get("http://" + max(maxHeights) + "/chain").json()
            self.chain = chainFromResponse(response["chain"])

        fullChain = { "blockHeight": self.chain.blockHeight, "chain": self.chain.displayDict() }
        return json.dumps(fullChain)

    def getMemPool(self):
        return [ tx.__dict__ for tx in self.mempool ]

    def resolveMemPool(self):
        memPools = {}

        for peer in self.peers:
            if self.ping(peer):
                response = requests.get("http://" + peer + "/mempool").json()
                memPools[peer] = response["pools"]

        if memPools != {}:
            self.mempool = sorted(memPools, key=lambda l: len(memPools[l]), reverse=True)[0]

        return [ tx.__dict__ for tx in self.mempool ]

    def submitTransaction(self, tx):
        # Broadcast to all the new transaction
        self.mempool.append(tx)
        self.broadcast("/resolve/mempool")

    def submitBlock(self, address, minerPubKey, previousBlockHash, nonce, transactionHashes):
        # Broadcast to all the new block
        self.chain.appendBlock(address, minerPubKey, previousBlockHash, nonce, transactionHashes)
        self.broadcast("/resolve/chain")