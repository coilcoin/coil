# proof.py

# The coil proof-of-work
# algorithm looks for four
# preceding 0's on the result
# double-sha256 of hash + nonce

from coil import chash

# Target is determined by proof_test.py

def proof(prevHash, nonce):
    result = chash.doubleHashEncode(str(prevHash) + str(nonce))
    if result[:6] == "000000":
        return result

def validProof(prevHash, nonce):
    result = chash.doubleHashEncode(str(prevHash) + str(nonce))
    return result[:6] == "000000"