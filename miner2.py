import requests
import hashlib
import datetime

from pathlib import Path
from coil.wallet import readWallet
from coil.proof import validProof

WALLET_FOLDER = str(Path.home()) + "/.config/coil/wallets/"
miner = readWallet(WALLET_FOLDER + "master.pem", WALLET_FOLDER + "master.pub.pem")

started = datetime.datetime.now()
total = 0

def main():
	global total
	print("welcome to hacky miner2")
	print("we be mining all t'day")
	print("Ctrl-C to quit m'deer")

	s = requests.Session()
	#url = "http://localhost:1337"
	url = "http://80.42.86.151:1337"
	nonce = 0
	last_hash = None

	try:
		while True:
			# Check to see if last hash has changed
			if nonce % 50 == 0:
				try:
					last_hash = s.get(url + "/chain/lastHash/").json()["message"]
				except:
					raise Exception("Could not fetch last hash. Node offline?")

			if validProof(last_hash, nonce):
				payload = {
					'minerAddress': miner.address,
					'previousBlockHash': last_hash,
					'nonce': str(nonce),
					'transactionHashes': '',
					'minerPubKey': miner.publicKeyHex
				}

				r = s.post(url + "/mine/", payload)
				total += 1

				print("New block mined")
				elapsed = (datetime.datetime.now() - started).total_seconds()
				print("Time Elapsed: ", elapsed , "s")
				print("Average Speed:", (total / elapsed), " blocks per second")

				print("Node says:", r.text)
				print()

			nonce += 1


	except KeyboardInterrupt:
		print()

if __name__ == "__main__":
	main()
