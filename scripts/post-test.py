from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		app.logger.info(request.json)
		return "got it"
	else:
		return "Post Tester 1.0"

app.run(port=8080, debug=True)