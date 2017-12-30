# proof.py

# The coil proof-of-work
# algorithm looks for four
# preceding 0's on the result
# double-sha256 of hash + nonce

import chash

def validProof(prevHash, nonce):
	return chash.doubleHashEncode(str(prevHash) + str(nonce))[:5] == "00000"