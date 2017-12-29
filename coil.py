# Coilcoin - simple cryptocurrency
# Copyright 2017. All Rights Reserved.
# MIT Licence

from chain import Chain
from tx import createInput, createOutput, Transaction
from wallet import generateAddress
import chash

me = generateAddress("me")
bob = generateAddress("bob")
miner = generateAddress("miner")

bc = Chain(me)

# Quickly mine a block
n = 0
h = bc.lastBlock.hash()
proof = ""
while True:
	proof = chash.doubleHashEncode(str(h) + str(n))
	if proof[:4] == "0000":
		break
	else:
		n += 1

# Create a new transaction
# t1: Give 20 coins to bob

print("Last black", bc.lastBlock.hash())

t1 = Transaction(me,
	[ { "prevTransHash": h, "index": 0 } ],
	[ createOutput(bob, 20) ]
)

bc.appendTransaction(t1)

bc.appendBlock(me, h, n, t1.hash())

# bc.display()

