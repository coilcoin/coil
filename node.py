# node.py
import requests

from urllib.parse import urlparse
from tx import Transaction, Coinbase, createInput
from chain import Chain

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

		return Transaction(d["address"], inputs, outputs)

def blockFromDict(d):
	pass

def chainFromPeers(peers):
	pass

class Node(object):
	def __init__(self, creator):
		self.peers = set()
		self.chain = None
		self.host = "0.0.0.0"
		self.port = 1337
		self.creator = creator

		# Read Peers
		peers = open("peers.txt", "r").readlines()
		if peers != []:
			for peer in peers:
				parsed_url = urlparse(peer.strip())
				self.peers.add(parsed_url.netloc)
		else:
			self.chain = Chain(self.creator)

	def registerPeer(self, address):
		parsed_url = urlparse(peer.strip())
		self.peers.add(parsed_url.netloc)

	def getChain(self):
		return self.chain.displayJSON()