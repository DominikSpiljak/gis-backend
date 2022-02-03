import re
import flask
import logging
from flask import jsonify
from database.database import Database
from utils.kdtree import get_kdtree
from utils.georeferencer import Georeferencer
from argument_parser import parse_args

app = flask.Flask(__name__)
args = parse_args()
database = Database(args.db_ini)
kd_tree = get_kdtree(database)
georeferencer = Georeferencer()


@app.route("/closest-connector", methods=["POST"])
def closest():
    json_body = flask.request.json
    return jsonify(kd_tree.query(json_body["nodes"]))


@app.route("/georeference", methods=["POST"])
def georeference():
    json_body = flask.request.json
    return georeferencer.georeference(json_body["addresses"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host=args.host, port=args.port)
