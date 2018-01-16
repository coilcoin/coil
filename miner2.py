import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import hashlib
import datetime

from pathlib import Path
from coil.wallet import readWallet
from coil.proof import validProof, proof

WALLET_FOLDER = str(Path.home()) + "/.config/coil/wallets/"
miner = readWallet(WALLET_FOLDER + "master.json")

started = datetime.datetime.now()
total = 0

def requests_retry_session(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
	session = session or requests.Session()
	retry = Retry(
		total=retries,
		read=retries,
		connect=retries,
		backoff_factor=backoff_factor,
		status_forcelist=status_forcelist
	)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount("http://", adapter)
	return session

def main():
	global total
	print("welcome to hacky miner2")
	print("we be mining all t'day")
	print("Ctrl-C to quit m'deer")

	s = requests.Session()
	url = "http://localhost:1337"

	f = open(WALLET_FOLDER + "../peers.txt", "r")
	first = f.readlines()[0]
	if first:
		url = "http://" + first.strip()
	else:
		raise Exception("Could not connect to node 0 in peers.txt!")

	nonce = 0
	last_hash = None
	try:
		while True:
			# Check to see if last hash has changed
			new_last_hash = None
			if nonce % 500000 == 0:
				try:
					new_last_hash = requests_retry_session().get(url + "/chain/lastHash/")
				except Exception as x:
					print(x)
				
				else:
					response = new_last_hash.json()
					if ["message"] in response:
						new_last_hash = response["message"]
						if new_last_hash != last_hash:
							nonce = 0

			if validProof(last_hash, nonce):
				payload = {
					'minerAddress': miner.address,
					'previousBlockHash': last_hash,
					'nonce': str(nonce),
					'transactionHashes': '',
					'minerPubKey': miner.publicKeyHex
				}

				r = None
				try:
					r = requests_retry_session().post(url + "/mine/", payload)
				except Exception as x:
					print(x)
				finally:
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
