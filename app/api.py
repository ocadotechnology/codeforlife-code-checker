from flask import Flask
from flask_cors import CORS

from codeforlife.service.api import handle_flask_request

import service


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["POST"])
def run():
    return handle_flask_request(service.run)


if __name__ == "__main__":
    app.run(
        host="localhost",
        port="8080",
        debug=True,
    )
