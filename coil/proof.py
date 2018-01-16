# proof.py

# The coil proof-of-work
# algorithm looks for four
# preceding 0's on the result
# double-sha256 of hash + nonce

from coil import chash

# Target is determined by proof_test.py

def proof(prevHash, nonce):
    result = chash.doubleHashEncode(str(prevHash) + str(nonce))
    if result[:4] == "0000" and int(result, 16) % 123 == 0:
        return result

def validProof(prevHash, nonce):
    result = chash.doubleHashEncode(str(prevHash) + str(nonce))
    return result[:4] == "0000" and int(result, 16) % 123 == 0