# Coil

Coil is a crypt-platform for Coilcoin, a micro-crypto currency. Coil is written in Python for educational purposes and features a minimum viable blockchain distributed public ledger solution.

## Wire
Wire is the HTTP Protocol (API) that Coil is built around. Wire is designed to be a minimum viable protocol meaning that much of it's algorithms are fairly primitive.

A Wire node should only keep track of a copy of the public ledger and a set of peers that it maintains. Both of these states are managed and shared through the Coil Consensus Algorithm **Spring**.

A single Wire node should provide the following functionality...
1. Allow clients to view the ledger
2. Allow clients to submit transactions
3. Allow miners to submit a mined block
4. Allow clients/miners to calculate balances
5. Allows clients/miners to view the mempool

### Managaing Peers
Once a node is live, it only requires the address and port to a node that is live within the network. One startup, the node sends a request to its peers to request a list of all other nodes on the network. The peer that receieves the request will then broadcast a message to all of the other known peers. When a node receives this message, a concensus is held between nodes and the longest peer node (that contains live nodes; validated through PING) wins.

## Spring