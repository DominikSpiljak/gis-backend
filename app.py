import re
import flask
import logging
from flask import request
from utils.kdtree import get_kdtree

app = flask.Flask(__name__)
kd_tree = get_kdtree()


@app.route("/closest-connector", methods=["GET"])
def closest():
    x = request.args.get("x")
    y = request.args.get("y")

    return kd_tree.query([x, y])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=8765)
