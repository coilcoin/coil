# block.py

import time
import json

from coil import chash
from coil import merkle
from coil import tx

class Block(object):
    def __init__(self, prevHash, nonce, txs, merkle):
        self.previousBlockHash = prevHash
        self.nonce = nonce
        self.transactions = txs
        self.merkleRoot = merkle
        self.timestamp = time.time()

    def hash(self):
        return chash.doubleHashEncodeJSON(self.__dict__)

    def json(self):
        newblock = self.__dict__
        newtransactions = []

        for t in newblock["transactions"]:
            if type(t).__name__ != "dict":
                newtransactions.append(t.__dict__)
            else:
                newtransactions.append(t)

        newblock["transactions"] = newtransactions
        return json.dumps(newblock)

class Genesis(Block):
    def __init__(self, creator, pubkey):
        # ICO of 120 coins
        txs = [
            tx.Coinbase(creator, pubkey, amount=12000000),
            tx.Coinbase("fd56d7ba8a4cd057f066a1c6d1", "2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d4947664d413047435371475349623344514542415155414134474e4144434269514b42675144594b6f4c7772545a6e514533746e38304b71627444737a5a440a655653324a6c776b584a63737956746839696d314568707a61636173362b4e35612f424254502f34716b497545434b39764e7378503256775631617455742b420a355938423169727944526e5a2b4652775156654f74726b417a792f3263627871785678397733794a4f636b5557314d346f4c2b61333778374e74535361704e4b0a774444307364324c735a6b454f6f337a71774944415141420a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d", amount=12000000)
        ]

        txs_dict = [ str(t.__dict__) for t in txs ]
        mr = merkle.generateMerkleRoot(txs_dict)

        super(Genesis, self).__init__(None, None, txs, mr)