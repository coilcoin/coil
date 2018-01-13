# Coil

Coil is an experimental micro cryptocurrency written in Python. It is by no means secure; much of the validation has not yet been implemented. *Coil* refers to the protocol and software, *Coilcoin* refers to the currency (COL).

## Getting Started
### Linux / Mac
To run the coil dameon, clone the git repo to a sensible place in your HOME directory. Next set the environment variable `COIL` to the location of the coil git repository. This may mean adding the following line to your `.profile` or `.bashrc` file in your HOME directory. You should also append the coil directory to your PATH variable so that the coild file can be run from anywhere in the terminal. For instance...

```bash
export COIL=$HOME/path/to/coil
export PATH=$PATH:$COIL/bin
```

Next run the setup script to initialize some required `.config` files and directories.
```bash
cd $COIL
./scripts/setup.sh
```

Next install the dependencies using pip3
```
sudo apt install python3 python3-pip3
sudo pip3 install flask requests
```

Finally run the `coild` program
```bash
coild
```

### Alternatively, you can run the coil.py script from within the COIL directory.

To initialize a node, run the python script...
```bash
python coil.py
```

## Wallet

**The current web wallet has been deprecated and now lives in a legacy repository. A new wallet in under development and shall be available for testing soon**
The wallet is a simple Python Flask application that stores the wallet meta data on disk meaning that anyone who is connected to the server can process a transaction. Therefore, DO NOT allow others to access your wallet server, instead only run the server locally on a trusted and secure network.

To run the server, within the coil directory, simply run the following code in bash...

```bash
python web-wallet/wallet.py
```

This will start a local server running on port 5000. To access the wallet, open a browser and visit `http://localhost:5000/`. The wallet details are stored in the directory `web-wallet/wallet`, so to export or import a wallet it is suggested that you manage this folder yourself.

## Proof of work
The proof of work algorithm used by Coil is called current. A valid proof is constructed from a nonce and previous hash. The resulting hash of these components must have 5 preceeding 0s and the hex equivalent of the hexdigest must be divisible by 5.

```python
def validProof(prevHash, nonce):
	result = doubleHashEncode(str(prevHash) + str(nonce))
	return result[:5] == "00000" and int(result, 16) % 5 == 0
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