import re
import flask
import logging
from flask import jsonify
from flask_cors import CORS
from database.database import Database
from utils.analysis import get_kdtree_shortie
from utils.georeferencer import Georeferencer
from argument_parser import parse_args

app = flask.Flask(__name__)
cors = CORS(app)
args = parse_args()
database = Database(args.db_ini)
kd_tree, shortie = get_kdtree_shortie(database, args.crs)
georeferencer = Georeferencer(args.crs)

app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/analiziraj", methods=["POST"])
def analyse():
    json_body = flask.request.json
    closest_results = kd_tree.query(json_body["nodes"])
    shortest_results = shortie.astar_search(
        [closest_entry["connector_gid"] for closest_entry in closest_results]
    )
    for i in range(len(shortest_results)):
        (
            closest_results[i]["shortest_path"],
            closest_results[i]["cost"],
        ) = shortest_results[i]

    database.write_to_db(
        query=f"INSERT INTO public.povijest_upita(tocka_upita,najblizi_izvod,udaljenost,najkraca_putanja,cijena) VALUES %s",
        data=[
            [
                flask.request.json["nodes"][i][0],
                flask.request.json["nodes"][i][1],
                closest_results[i]["connector_gid"],
                closest_results[i]["distance"],
                closest_results[i]["shortest_path"],
                closest_results[i]["cost"],
            ]
            for i in range(len(shortest_results))
        ],
        template="ST_Transform(ST_GeomFromText('POINT(%s %s)'), {args.crs}), 3765), %s, %s, %s, %s",
    )
    return jsonify(closest_results)


@app.route("/georeferenciraj", methods=["POST"])
def georeference():
    json_body = flask.request.json
    return georeferencer.georeference(json_body["addresses"])


@app.route("/povijest", methods=["GET"])
def history():
    fields = [
        "id",
        "vrijeme_upisa",
        f"ST_AsText(ST_Transform(tocka_upita, {args.crs}))",
        "najblizi_izvod",
        "udaljenost",
        "najkraca_putanja",
        "cijena",
    ]
    result = database.query(f"SELECT {', '.join(fields)} FROM public.povijest_upita")
    return jsonify(
        [
            fields,
            *result,
        ]
    )


@app.route("/izvod", methods=["GET"])
def izvod():
    fields = [
        "gid",
        "brparica",
        "parice",
        "pkizvod",
        "smjestaj",
        f"ST_AsText(ST_Transform(geom, {args.crs}))",
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
        "ukuparica",
        f"ST_AsText(ST_Transform(geom, {args.crs}))",
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
        f"ST_AsText(ST_Transform(geom, {args.crs}))",
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
        f"ST_AsText(ST_Transform(geom, {args.crs}))",
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
        f"ST_AsText(ST_Transform(geom, {args.crs}))",
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
    logging.info("Selected CRS: EPSG:%s", args.crs)
    app.run(host=args.host, port=args.port)
