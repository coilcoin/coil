# merkle.py
# mainly thanks to...
# https://gist.github.com/brandomr/f5f325a0e9161d481714efe00d846880

from coil.chash import doubleHashEncode

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

# Produces mRoot from txs
# using a double SHA256 hash
def generateMerkleRoot(transactions):
    subTree = []
    for i in chunks(transactions, 2):
        if len(i) == 2:
            h = doubleHashEncode(str(i[0] + i[1]))
        else:
            h = doubleHashEncode(str(i[0] + i[0]))
    subTree.append(h)
    
    if len(subTree) == 1:
        return subTree[0]
    else:
        return generateMerkleRoot(subTree)