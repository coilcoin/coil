# wallet.py

from flask import Flask, render_template, session
import config
import requests

app = Flask(__name__)
app.secret_key = "somethingrandom"

@app.route("/")
def index():
	if config.private_key == "":
		try:
			r = requests.get(config.node_address + "/wallet/new").json()
			session["private_key"] = r["privateKey"]
			session["address"] = r["address"]
		except:
			return "Node is not online."

	else:
		session["private_key"] = config.private_key
		session["address"] = config.wallet_address

	return render_template("wallet.html", address=session["address"], privateKey=session["private_key"])