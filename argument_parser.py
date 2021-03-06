from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("--host", help="Host address for api", default="0.0.0.0")
    parser.add_argument("--port", help="Port for api", default="4321")
    parser.add_argument(
        "--db-ini", help="Path to database .ini file", default="database.ini"
    )
    parser.add_argument("--crs", help="CRS used in the project", default="3857")

    return parser.parse_args()
