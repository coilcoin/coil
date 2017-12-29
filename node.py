# node.py

import chain

class Node(object):
	def __init__(self):
		self.peers = set()
		self.chain = Chain()