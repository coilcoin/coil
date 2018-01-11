# proof.py

# The coil proof-of-work
# algorithm looks for four
# preceding 0's on the result
# double-sha256 of hash + nonce

import chash

def validProof(prevHash, nonce):
	result = chash.doubleHashEncode(str(prevHash) + str(nonce))
	return result[:5] == "00000" and int(result, 16) % 5 == 0
