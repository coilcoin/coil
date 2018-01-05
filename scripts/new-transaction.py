import requests

r = requests.post("http://localhost:1337/transaction/new",
	'wallet': '12389324',
	'inputs': [],
	'outputs': {
		'address': '1234345',
		'amount': 120
	}
)

print(r.text)