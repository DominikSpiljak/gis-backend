import re
import flask
import logging
from flask import request
from utils.kdtree import get_kdtree
from argument_parser import parse_args

app = flask.Flask(__name__)
args = parse_args()
kd_tree = get_kdtree(args.db_ini)


@app.route("/closest-connector", methods=["GET"])
def closest():
    x = request.args.get("x")
    y = request.args.get("y")

    return kd_tree.query([x, y])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host=args.host, port=args.port)
