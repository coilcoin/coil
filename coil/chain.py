# chain.py

from coil import chash
from coil import block
from coil import proof
from coil import wallet
from coil import merkle
from coil import tx

# Chain is responsible for...
# 1. Verifying transactions
# 2. Maintaining the mempool
# 3. Verifying blocks
# 4. Maintaining the blockchain

def hashTransDict(d):
    # Delete Wallet
    if "address" in d:
        del d["address"]
    return chash.doubleHashEncodeJSON(d)

def calculateInflow(chain, tx):
    totalIn = 0
    for i in tx.inputs:
        block = chain[i["index"]]
        # Check that output index points to
        # a valid transaction output
        transaction = None
        for t in block.transactions:
            # Transaction must be converted
            # to dictionary since genesis
            # is also a dictionary
            if t.hash() == i["prevTransHash"]:
                transaction = t
            else:
                # Input Transaction does not exist
                return False

        # Does the current input specify
        # an amount to be given
        foundAmount = False
        for o in transaction.outputs:
            if o["address"] == tx.address:
                totalIn += o["amount"]
                foundAmount = True

        # If no amount given to address,
        # transaction must be invalid
        if not foundAmount:
            return False

    return totalIn

def calculateOutflow(tx):
    totalOut = 0
    for o in tx.outputs:
        totalOut += o["amount"]

    return totalOut

def verifyTransaction(chain, tx):
    """
    Transaction codes
    1 .. Successful Transaction
    2 .. Corrupt inputs.
    3 .. Corrupt signature.
    4 .. Insufficient funds.
    """

    # Verify that a single wallet
    # owns all of the inputs
    # for i in tx.inputs:
    # 	if i["address"] != tx.address:
    # 		return 2

    # Verify that the wallet of
    # the tx has signed the tx
    # address, message, signature

    publicKey = binascii.unhexlify(tx.pubkey.encode("utf-8"))

    if not wallet.verifySignature(publicKey, tx.hash(), tx.signature):
        return 3

    # Verify that the wallet has
    # sufficient funds
    totalIn = calculateInflow(chain, tx)
    totalOut = calculateOutflow(tx)

    if totalIn:
        # If funds are sufficient
        if totalIn >= totalOut:
            return 1

    return 4

def verifyCoinbase(chain, tx):
    # Check coinbase is 50 coins
    if tx.outputs[0]["amount"] == 50:
        return True
    else:
        return False

def verifyBlock(chain, prevBlockHash, nonce, transactionHashes):
    # Verify Proof of Work
    if proof.validProof(prevBlockHash, nonce):
        # TODO: Verify that hashes are in the mempool
        return True
    else:
        return False

class Chain(object):
    def __init__(self, creator, creatorPubKey, genesis=None, chain=[]):
        self.mempool = set()

        # self.creator should be an address
        self.creator = creator
        self.creatorPubKey = creatorPubKey

        if not chain:
            self.chain = []

            # Create genesis block
            self.genesis = block.Genesis(self.creator, self.creatorPubKey)
            self.chain.append(self.genesis)
        else:
            self.chain = chain

        # print("Genesis Hash", self.genesis.transactions[0].hash())

    @property
    def blockHeight(self):
        return len(self.chain)

    @property
    def lastBlock(self):
        return self.chain[-1]

    def appendTransaction(self, transaction):
        transcode = verifyTransaction(self.chain, transaction)
        if transcode == 1:
            self.mempool.add(transaction)
        
        return transcode

    def appendBlock(self, minerAddress, minerPubKey, prevBlockHash, nonce, transactionHashes):
        if verifyBlock(self.chain, prevBlockHash, nonce, transactionHashes):
            txs = []

            # Create Coinbase for Miner
            cbase = tx.Coinbase(minerAddress, minerPubKey)

            # Verify Coinbase
            if verifyCoinbase(self.chain, cbase):
                txs.append(cbase)
            else:
                return False

            # Select transactions
            for tr in self.mempool:
                for th in transactionHashes:
                    if tr.hash() == th:
                        txs.append(tr)

            # Generate Merkle Root
            txs_dict = [ str(t.__dict__) for t in txs ]
            mr = merkle.generateMerkleRoot(txs_dict)

            # Add new block
            b = block.Block(self.lastBlock.hash(), nonce, txs, mr)
            self.chain.append(b)
    
            # Remove mined transactions from pool
            # for tr in txs:
            # 	self.mempool.remove(tr)

            return True
        else:
            return False

    def displayDict(self):
        newchain = []
        for block in self.chain:
            newblock = block.__dict__
            newtransactions = []

            for t in newblock["transactions"]:
                if type(t).__name__ != "dict":
                    newtransactions.append(t.__dict__)
                else:
                    newtransactions.append(t)

            newblock["transactions"] = newtransactions
            newchain.append(newblock)

        return newchain
    
    def displayJSON(self):
        import json
        return json.dumps(self.displayJSON(newchain))