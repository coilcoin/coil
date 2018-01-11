# wallet.py

from flask import Flask, render_template, session, request, redirect
import config
import requests
import json
import os
import time
import hashlib
import struct

from Crypto.PublicKey import RSA

def doubleHash(input):
    return hashlib.sha256(hashlib.sha256(input).digest()).hexdigest()

def doubleHashEncode(input):
    return doubleHash(input.encode("utf-8"))

def doubleHashEncodeJSON(input):
	return doubleHashEncode(str(input))

app = Flask(__name__)
app.secret_key = "somethingrandom"

WALLET_FOLDER = os.path.join(os.getcwd(), "wallet")

def loadHistory():
	"""
	Returns dict { "inputs": [], "outputs": [] }
	"""

	history = {
		"inputs": [],
		"outputs": []
	}

	# INPUTS: Example line
	# amount, from, time, previousBlockHash, blockIndex
	f = open(WALLET_FOLDER + "/history_inputs.csv", "r")
	lines = f.readlines()

	for line in lines:
		line = [l.strip() for l in line.split(",")]
		app.logger.info(line)

		history["inputs"].append({
			"amount": line[0],
			"from": line[1],
			"time": float(line[2]),
			"previousBlockHash": line[3],
			"blockIndex": line[4]
		})

	# OUTPUTS: Example line
	# amount, to, time
	f = open(WALLET_FOLDER + "/history_outputs.csv", "r")
	lines = f.readlines()

	for line in lines:
		app.logger.info(line)
		line = [ l.strip() for l in line.split(",") ]

		history["outputs"].append({
			"to": line[0],
			"amount": line[1],
			"time": float(line[2])
		})

	return history

def writeHistory():
	# Before writing history, check is the history
	# already on disk?
	history = loadHistory()

	if session["inputs"] != history["inputs"]:
		# INPUTS: Example line
		# amount, from, time, previousBlockHash, blockIndex
		f = open(WALLET_FOLDER + "/history_inputs.csv", "a")

		string = ""
		for i in session["inputs"]:
			string = ",".join(list([ str(ii) for ii in i.values()]))
			print(string)
			string += "\n"

		f.write(string)
		f.close()

	if session["outputs"] != history["outputs"]:
		# OUTPUTS: Example line
		# amount, to, time
		f = open(WALLET_FOLDER + "/history_outputs.csv", "a")
		
		string = ""
		for o in session["outputs"]:
			string = ",".join(list([ str(i) for i in o.values()]))
			string += "\n"

		f.write(string)
		f.close()

@app.route("/")
def index():
	# Write files if they don't exist
	# Initialize Wallet Space
	if not "inputs" in session:
		session["inputs"] = []

	if not "outputs" in session:
		session["outputs"] = []

	# Is wallet directory empty
	if os.listdir(WALLET_FOLDER) == []:
		try:
			# Request a new wallet
			r = requests.get(config.node_address + "/wallet").json()
			session["private_key"] = r["privateKey"]
			session["address"] = r["address"]

			# Generate public key
			pubkey = RSA.importKey(minerPubKey).publickey().exportKey()
			f = open(WALLET_FOLDER + "/pubkey", "wb")
			f.write(pubkey)
			f.close()

			# Export PEM file
			f = open(WALLET_FOLDER + "/wallet.pem", "w")
			f.write(session["private_key"])
			f.close()

			# Write address file
			f = open(WALLET_FOLDER + "/address", "w")
			f.write(session["address"])
			f.close()

			# Initialize History Files
			writeHistory()

		except:
			return "Node is not online."

	else:
		# If history is not present, write history
		if not "history_inputs.csv" in os.listdir(WALLET_FOLDER) \
			and not "history_outputs.csv" in os.listdir(WALLET_FOLDER):
			f = open(WALLET_FOLDER + "/history_inputs.csv", "w")
			f.write("")
			f.close()

			f = open(WALLET_FOLDER + "/history_outputs.csv", "w")
			f.write("")
			f.close()
		else:
			history = loadHistory()
			session["inputs"] = history["inputs"]
			session["outputs"] = history["outputs"]

		with open(WALLET_FOLDER + "/wallet.pem", "r") as f:
			session["private_key"] = f.read().strip()
			print(session["private_key"])

		with open(WALLET_FOLDER + "/address", "r") as f:
			session["address"] = f.read().strip()

		# Populate history
		chain = requests.get(config.node_address + "/chain").json()
		blockchain = chain["chain"]

		blockIndex = 0
		for block in blockchain:
			for tx in block["transactions"]:
				for o in tx["outputs"]:
					if tx["address"] == session["address"]:
						amount = o["amount"]
						fromAddress = tx["address"]
						time = block["timestamp"]
						blockHash = doubleHashEncodeJSON(block)

						session["inputs"].append({
							"amount": amount,
							"from": fromAddress,
							"time": time,
							"previousBlockHash": blockHash,
							"blockIndex": blockIndex
						})

			blockIndex += 1

		writeHistory()

	# Calculate balance
	r = requests.post(config.node_address + "/balance", data={'address': session["address"]}).json()
	session["balance"] = r["balance"]

	# Load history
	history = loadHistory()
	session["inputs"] = history["inputs"]
	session["outputs"] = history["outputs"]

	# Combine inputs and outputs
	history = []
	for i in session["inputs"]:
		history.append(i)

	for o in session["outputs"]:
		history.append(o)

	# sorted_history = sorted(history, key=lambda k: k['time'])

	return render_template("wallet.html", address=session["address"], balance=session["balance"], history=history)

@app.route("/send", methods=["POST", "GET"])
def send():
	if request.method == "POST":
		sender = session["private_key"]
		recipient = request.form.get("recipient")
		amount = request.form.get("amount")

		# Generate Output
		output = {
			"address": recipient,
			"amount": float(amount)
		}

		inputs = []

		# Recall Inputs
		for inp in session["inputs"]:
			i = {}
			i["previousBlockHash"] = inp["previousBlockHash"]
			i["index"] = inp["blockIndex"]
			inputs.append(i)

		payload = {
			'wallet': sender,
			'inputs': inputs,
			'outputs': [output]
		}

		# Send transaction request to node
		r = requests.post(config.node_address + "/transaction/new", json.dumps(payload), headers={"Content-Type": "application/json"}).json()

		# Transaction was successful
		success = "blockHash" in r 

		# If all is good, add transaction to history
		if success:
			session["outputs"].append({
				"to": recipient,
				"amount": float(amount),
				"time": time.time()
			})
			writeHistory()

		return render_template("sent.html", message=r["message"], success=success)

	else:
		return redirect("/")

@app.route("/transaction")
def transaction():
	return render_template("transaction.html")

@app.route("/flush")
def flush():
	session.clear()
	return "Cleared Session."

if __name__ == "__main__":
    app.run(debug=True)
