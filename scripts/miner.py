import requests
import hashlib
import datetime

def doubleHash(input):
    return hashlib.sha256(hashlib.sha256(input).digest()).hexdigest()

def doubleHashEncode(input):
    return doubleHash(input.encode("utf-8"))

def validProof(prevHash, nonce):
	result = doubleHashEncode(str(prevHash) + str(nonce))
	return result[:5] == "00000" and int(result, 16) % 5 == 0

started = datetime.datetime.now()
total = 0

print("welcome to hacky miner")
print("we be mining all t'day")
print("Ctrl-C to quit m'deer")

s = requests.Session()
url = "http://localhost:1337"

#address = s.get(url + "/wallet/new").json()["address"]
address = 'bb696bae2f05df403051306d26'
pubkey = b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCkQ5i+p35CjZeueJYG0lZ0VDY0\np8obVjsuSsczjyk38S+HWcmxn2nvPM4+Cq+4meQ+mMDTvMfboKEhrAoSKVkV1g0P\n3Rowmo9yw/bo3qthjLt+0qX3zNJXw3j67qMCfjcXMGPyXSEDMTAJjIQtgHYHxHtp\n11QpmcRde9lH7B6N/wIDAQAB\n-----END PUBLIC KEY-----'
last_hash = s.get(url + "/block/hash").json()["message"]

nonce = 0

try:
	while True:
		if validProof(last_hash, nonce):
			payload = {
				'minerAddress': address,
				'previousBlockHash': last_hash,
				'nonce': str(nonce),
				'transactionHashes': '',
				'minerPubKey': pubkey.decode("utf-8")
			}

			r = s.post(url + "/mine", payload)
			total += 1

			print("New block mined")
			elapsed = (datetime.datetime.now() - started).total_seconds()
			print("Time Elapsed: ", elapsed , "s")
			print("Average Speed:", (total / elapsed), " blocks per second")

			print("Node says:", r.text)
			print()

			last_hash = s.get(url + "/block/hash").json()["message"]

		nonce += 1


except KeyboardInterrupt:
	print()
