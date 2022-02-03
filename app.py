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


@app.route("/najblizi-izvod", methods=["POST"])
def closest():
    json_body = flask.request.json
    return jsonify(kd_tree.query(json_body["nodes"]))


@app.route("/georeferenciraj", methods=["POST"])
def georeference():
    json_body = flask.request.json
    return georeferencer.georeference(json_body["addresses"])


@app.route("/izvod", methods=["GET"])
def izvod():
    fields = [
        "gid",
        "brparica",
        "parice",
        "pkizvod",
        "smjestaj",
        "ST_X(geom)",
        "ST_Y(geom)",
    ]
    result = database.query(f"SELECT {', '.join(fields)} FROM public.izvod")
    return jsonify(
        [
            fields,
            *result,
        ]
    )


@app.route("/kabel", methods=["GET"])
def kabel():
    fields = [
        "gid",
        "duz",
        "godina",
        "tipkab",
        "ST_AsText(geom)",
    ]
    result = database.query(f"SELECT {', '.join(fields)} FROM public.kabel")
    return jsonify(
        [
            fields,
            *result,
        ]
    )


@app.route("/spojnica", methods=["GET"])
def spojnica():
    fields = [
        "gid",
        "nasbr",
        "ST_X(geom)",
        "ST_Y(geom)",
    ]
    result = database.query(f"SELECT {', '.join(fields)} FROM public.spojnica")
    return jsonify(
        [
            fields,
            *result,
        ]
    )


@app.route("/trasa", methods=["GET"])
def trasa():
    fields = [
        "gid",
        "ST_AsText(geom)",
    ]
    result = database.query(f"SELECT {', '.join(fields)} FROM public.trasa")
    return jsonify(
        [
            fields,
            *result,
        ]
    )


@app.route("/zdenac", methods=["GET"])
def zdenac():
    fields = [
        "gid",
        "br_zdenca",
        "dim",
        "godina",
        "gr",
        "kbr",
        "poklopac",
        "smjestaj",
        "tip",
        "tkc",
        "zd",
        "ST_X(geom)",
        "ST_Y(geom)",
    ]
    result = database.query(f"SELECT {', '.join(fields)} FROM public.zdenac")
    return jsonify(
        [
            fields,
            *result,
        ]
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host=args.host, port=args.port)
