# node.py
import requests
import json
import sys
import os

from urllib.parse import urlparse
from pathlib import Path
from time import time

from coil.tx import Transaction, Coinbase, createInput
from coil.block import Block
from coil.chain import Chain
from coil.wallet import Wallet

CONFIG_FOLDER = str(Path.home()) + "/.config/coil"

def log(info):
    print(f"[Message] {info}")

def transactionFromDict(d):
    if d["inputs"] == []:
        # Coinbase Transaction
        o = d["outputs"][0]
        return Coinbase(o["address"], d["pubkey"], amount=o["amount"])
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
    try:
        pubkey = genesis.transactions[0]["pubkey"]
    except:
        pubkey = genesis.transactions[0].__dict__["pubkey"]

    return Chain(creator, pubkey, genesis=genesis, chain=blocks)

def chainFromPeers(peers):
    # Iterate through peers until a
    # valid chain is found
    peer_index = 0
    while peer_index < len(peers):
        url = "http://" + list(peers)[peer_index] + "/chain/"

        try:
            response = requests.get(url)
            return chainFromResponse(response.json())

        except requests.exceptions.RequestException:
            peer_index += 1		

    log("Could not download blockchain from peers.")
    return False

class Node(object):
    def __init__(self, creator, creatorPubKey, nodeLoc):
        self.peers = set()
        self.chain = None
        self.creator = creator
        self.creatorPubKey = creatorPubKey
        self.mempool = []
        self.nodeLoc = nodeLoc

        # Read Peers
        # Deprecated: REMOVED use of peers.txt
        # This should prevent issues for nodes
        # running on the same system (although
        # not advised)
        # peers = [ s.strip() for s in open(os.environ.get("COIL") + "/peers.txt", "r").readlines() ]
        # if peers != []:
        #     for peer in peers:
        #         if peer != "http://" + self.nodeLoc:
        #             parsed_url = urlparse(peer.strip())
        #             self.peers.add(parsed_url.netloc)
                    
        #             # Attempt to find chain from peers
        #             # if not, initialize a chain
        #             self.chain = chainFromPeers(self.peers)
        #             if not self.chain:
        #                 self.chain = Chain(self.creator, self.creatorPubKey)
                
        #     if not self.chain:
        #         self.chain = Chain(self.creator, self.creatorPubKey)
        # else:

        # If we already have a local copy of the blockchain
        # then load it in and then resolve, else just create
        # a new blockchain object
        if not self.readFromDisk():
            self.chain = Chain(self.creator, self.creatorPubKey)
        else:
            self.chain = chain=self.readFromDisk()

        self.resolveChain()

    def writeToDisk(self):
        # Save chain to disk
        fullChain = { "chain": self.chain.displayDict() }
        jsonString = json.dumps(fullChain)

        f = open(CONFIG_FOLDER + "/blockchain/chain.json", "w")
        f.write(jsonString)
        f.close()

    def readFromDisk(self):
        try:
            f = open(CONFIG_FOLDER + "/blockchain/chain.json", "r")
            response = json.loads(f.read())
            return chainFromResponse(response["chain"])
        except:
            return False
        
    def ping(self, nodeloc):
        # Pinging a Wire node...
        # expects a plain text
        try:
            response = requests.get("http://" + nodeloc + "/ping/").json()
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
        print("Broadcasting to all peers", route)
        if self.peers:
            for peer in self.peers.copy():
                if peer != self.nodeLoc:
                    if self.ping(peer):
                        print("Sending request to ", peer)
                        try:
                            requests.get("http://" + peer + route, timeout=5)
                        except:
                            return False
                    # else:
                        # Remove peer from pool
                        # & then broastcast
                        # self.peers.remove(peer)
                        # self.broadcast("/resolve/peers")

    def registerPeer(self, address):
        parsed_url = urlparse("http://" + address.strip())
        if parsed_url.netloc:
            self.peers.add(parsed_url.netloc)

        # This this peer is the first
        # peer this node knows about,
        # resolve the chain too
        if len(self.peers) == 1:
            self.resolveChain()

        # Tell nodes to add new peer
        self.broadcast("/join/" + address + "/")

        # Broadcast to all nodes
        self.broadcast("/resolve/peers/")

        return self.peers

    def resolvePeers(self):
        peersLists = {}

        for peer in self.peers:
            print(self.ping(peer))
            if self.ping(peer):
                peerList = requests.get("http://" + peer + "/peers/").json()
                if peerList:
                    peersLists[peer] = json.loads(peerList)

        print(peersLists)
        if peersLists != {}:
            self.peers = sorted(peersList, key=lambda l: len(peersList[l]), reverse=True)[0]
            print(self.peers)

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
                response = requests.get("http://" + peer + "/chain/").json()
                maxHeights[peer] = response["blockHeight"]
            # else:
            #     # Remove peers & resolve
            #     self.peers.remove(peer)
            #     self.broadcast("/resolve/peers") 

        # Replace chain
        if maxHeights != {}:
            response = requests.get("http://" + max(maxHeights) + "/chain/").json()
            # Save changes to disk
            self.chain = Chain(self.creator, self.creatorPubKey, chain=chainFromResponse(response["chain"]))
            
        self.writeToDisk()

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

    def submitBlock(self, address, minerPubKey, previousBlockHash, nonce, transactionHashes):
        # Broadcast to all the new block
        self.chain.appendBlock(address, minerPubKey, previousBlockHash, nonce, transactionHashes)
        self.broadcast("/resolve/chain/")