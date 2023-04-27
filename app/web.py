from flask import Flask, request, Response
from flask_cors import CORS
from pydantic import ValidationError

import service


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["POST"])
def run():
    try:
        data = service.Data(**request.json)
    except ValidationError as error:
        return Response(error.json(), status=400, content_type="application/json")

    try:
        response = service.run(data)
    except service.Error as error:
        return Response(str(error), status=500, content_type="text/plain")
    except Exception:
        return Response(status=500)

    return Response(response, status=200, content_type="application/json")


if __name__ == "__main__":
    app.run(
        host="localhost",
        port="8080",
        debug=True,
    )
