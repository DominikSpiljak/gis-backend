from scipy.spatial import KDTree
from geopy import distance
import pyproj


class KDTreeWrapper:
    def __init__(self, points, cables, crs):
        self.__positions = [
            points[point]["position"]
            for point in points
            if any(
                cables[cable]["capacity"] > 0
                for cable in points[point]["parent_cables"]
            )
        ]
        self.__tree = KDTree(self.__positions)
        self.__ids = [
            point
            for point in points
            if any(
                cables[cable]["capacity"] > 0
                for cable in points[point]["parent_cables"]
            )
        ]
        self.transformer = pyproj.transformer.Transformer.from_proj(
            f"EPSG:{crs}", f"EPSG:4326"
        )

    def query(self, x, *args, **kwargs):
        results = []
        _, indices = self.__tree.query(x, *args, **kwargs)
        for i, x_ in enumerate(x):
            results.append(
                {
                    "distance": distance.geodesic(
                        self.transformer.transform(*x_),
                        self.transformer.transform(*self.__positions[int(indices[i])]),
                    ).meters,
                    "connector_gid": self.__ids[int(indices[i])],
                }
            )
        return results


class Shortie:
    pass


def get_kdtree_shortie(database, crs):

    # Points query
    result = database.query(
        f"SELECT gid, ST_X(ST_Transform(geom, {crs})), ST_Y(ST_Transform(geom, {crs})), brparica FROM public.izvod;"
    )

    points = {}
    for entry in result:
        points[int(entry[0])] = {
            "position": [entry[1], entry[2]],
            "num_parica": int(entry[3])
            if entry[3] != "null" and entry[3] is not None
            else 0,
            "parent_cables": [],
        }

    # Parent cable query
    result = database.query(
        f"SELECT izvod.gid, kabel.gid, kabel.ukuparica, COALESCE(kabel.duz::float, ST_Length(kabel.geom)) FROM public.izvod AS izvod, public.kabel AS kabel WHERE ST_Touches(ST_QuantizeCoordinates(izvod.geom, 1), ST_QuantizeCoordinates(kabel.geom, 1));"
    )

    cables = {}

    for entry in result:
        if int(entry[1]) in cables:
            cables[int(entry[1])]["neighbour_points"].append(entry[0])
        else:
            cables[int(entry[1])] = {
                "capacity": int(entry[2]),
                "length": entry[3],
                "neighbour_points": [entry[0]],
            }
        points[int(entry[0])]["parent_cables"].append(int(entry[1]))

    for point in points:
        num_parica = points[point]["num_parica"]
        for cable in sorted(
            points[point]["parent_cables"], key=lambda x: cables[x]["length"]
        ):
            if num_parica == 0:
                break
            elif num_parica > cables[cable]["capacity"]:
                num_parica -= cables[cable]["capacity"]
                cables[cable]["capacity"] = 0
            else:
                cables[cable]["capacity"] -= num_parica
                break

    kdwrapper = KDTreeWrapper(points, cables, crs)

    connectors = {}

    # Cabel relationships
    result = database.query(
        f"SELECT spojnica.gid, kabel.gid, ST_X(ST_Transform(spojnica.geom, {crs})), ST_Y(ST_Transform(spojnica.geom, {crs})), COALESCE(kabel.duz::float, ST_Length(kabel.geom)), ukuparica FROM public.spojnica AS spojnica, public.kabel AS kabel WHERE ST_Touches(ST_QuantizeCoordinates(spojnica.geom, 1), ST_QuantizeCoordinates(kabel.geom, 1));"
    )

    for entry in result:
        # Add cable to cables if doesnt exist and add neighbour points
        if int(entry[1]) in cables:
            cables[int(entry[1])]["neighbour_points"].append(entry[0])
        else:
            cables[int(entry[1])] = {
                "capacity": int(entry[5]),
                "length": entry[4],
                "neighbour_points": [entry[0]],
            }

        # Add connector to connectors if doesnt exist and add parent cable
        if int(entry[0]) not in connectors:
            connectors[int(entry[0])] = {
                "position": [entry[2], entry[3]],
                "parent_cables": [],
            }
        connectors[int(entry[0])]["parent_cables"].append(int(entry[1]))

    return kdwrapper
