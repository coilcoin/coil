# Coil

Coil is an experimental micro cryptocurrency written in Python. It is by no means secure; much of the validation has not yet been implemented. *Coil* refers to the protocol and software, *Coilcoin* refers to the currency (COL).

## Getting Started
### Linux / Mac
To run the coil daemon, clone the git repo to a sensible place in your HOME directory. Next set the environment variable `COIL` to the location of the coil git repository. This may mean adding the following line to your `.profile` or `.bashrc` file in your HOME directory. You should also append the coil directory to your PATH variable so that the coild file can be run from anywhere in the terminal. For instance...

```bash
export COIL=$HOME/path/to/coil
export PATH=$PATH:$COIL/bin
```

Next run the setup script to initialize some required `.config` files and directories.
```bash
cd $COIL
./scripts/setup.sh
```

Next install the dependencies using pip3...
```
sudo apt install python3 python3-pip3
sudo pip3 install flask requests
```

Add a known peer to the peers.txt folder (remove any existing IPs) and then edit the `config.py` file within the COIL directory and point it to your wallets directory (should just be a case of changing the username within the path).

Finally generate a new wallet for the node to use and run the `coild` program
```bash
./new.py master
coild
```

### Alternatively, you can run the coil.py script from within the COIL directory.

To initialize a node, run the python script...
```bash
python coil.py
```

## Wallet
To generate a wallet, visit `/wallet` on the server or to name the file, visit `/wallet/wallet_name`.

## Proof of work
The proof of work algorithm used by Coil is called current. A valid proof is constructed from a nonce and previous hash. The resulting hash of these components must contain a character that is repeated atleast as many times as the TARGET value.

```python
[ Proof of working is undergoing work ]
```

## Mining
Coil comes with a built in miner. To use the miner, update the details in the file and then run `miner2.py`.

## Dependencies
* Python 3.6 (only tested with Ubuntu 17.10)
* Flask
* requests

## Contributing
I am looking to build a small community to develop coil further. If you're interested in contributing servers,
code or just ideas, why not join the gitter community.