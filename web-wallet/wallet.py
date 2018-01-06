# wallet.py

from flask import Flask, render_template, session, request, redirect
import config
import requests
import json
import os

import hashlib

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
	# INPUTS: Example line
	# amount, from, time, previousBlockHash, blockIndex
	f = open(WALLET_FOLDER + "/history_inputs.csv", "r")
	lines = f.readlines()

	for line in lines:
		line = [ l.strip() for l in line.split(",") ]
		session["inputs"].append({
			"amount": line[0],
			"from": line[1],
			"time": line[2],
			"previousBlockHash": line[3],
			"blockIndex": line[4]
		})

	# OUTPUTS: Example line
	# amount, to, time
	f = open(WALLET_FOLDER + "/history_outputs.csv", "r")
	lines = f.readlines()

	for line in lines:
		line = [ l.strip() for l in line.split(",") ]
		session["outputs"].append({
			"amount": line[0],
			"to": line[1],
			"time": line[2]
		})

def writeHistory():
	# INPUTS: Example line
	# amount, from, time, previousBlockHash, blockIndex
	f = open(WALLET_FOLDER + "/history_inputs.csv", "w")

	string = ""
	for i in session["inputs"]:
		for ii in i:
			string += str(i[ii]) + ","
		string += "\n"

	f.write(string)
	f.close()

	# OUTPUTS: Example line
	# amount, to, time
	f = open(WALLET_FOLDER + "/history_outputs.csv", "w")
	
	string = ""
	for output in session["outputs"]:
		for i in output:
			string += str(i[output]) + ","
		string += "\n"

	f.write(string)
	f.close()

@app.route("/")
def index():
	# Initialize Wallet Space
	if not "inputs" in session:
		session["inputs"] = []

	if not "outputs" in session:
		session["outputs"] = []

	# Is wallet directory empty
	if os.listdir(WALLET_FOLDER) == []:
		try:
			# Request a new wallet
			r = requests.get(config.node_address + "/wallet/new").json()
			session["private_key"] = r["privateKey"]
			session["address"] = r["address"]

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
		if not "history_inputs.csv" in os.listdir(WALLET_FOLDER):
			writeHistory()
		else:
			loadHistory()

		with open(WALLET_FOLDER + "/wallet.pem", "r") as f:
			session["private_key"] = f.read().strip()

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

	app.logger.info(session["inputs"])

	return render_template("wallet.html", address=session["address"], balance=session["balance"])

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

		# { wallet: "key", inputs: [  ], outputs: [ ] }

		return render_template("sent.html", message=r["message"], success=success)

		
	else:
		return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
