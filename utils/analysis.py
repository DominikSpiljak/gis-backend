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
            "position": [float(entry[1]), float(entry[2])],
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
            cables[int(entry[1])]["neighbour_points"].append(int(entry[0]))
        else:
            cables[int(entry[1])] = {
                "capacity": int(entry[2]),
                "length": float(entry[3]),
                "neighbour_points": [int(entry[0])],
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
    offset = max(list(points)) + 1

    # Cabel relationships
    result = database.query(
        f"SELECT spojnica.gid, kabel.gid, ST_X(ST_Transform(spojnica.geom, {crs})), ST_Y(ST_Transform(spojnica.geom, {crs})), COALESCE(kabel.duz::float, ST_Length(kabel.geom)), ukuparica FROM public.spojnica AS spojnica, public.kabel AS kabel WHERE ST_Touches(ST_QuantizeCoordinates(spojnica.geom, 1), ST_QuantizeCoordinates(kabel.geom, 1));"
    )

    for entry in result:
        # Add cable to cables if doesnt exist and add neighbour points
        if int(entry[1]) in cables:
            cables[int(entry[1])]["neighbour_points"].append(int(entry[0]) + offset)
        else:
            cables[int(entry[1])] = {
                "capacity": int(entry[5]),
                "length": float(entry[4]),
                "neighbour_points": [int(entry[0]) + offset],
            }

        # Add connector to points if doesnt exist and add parent cable
        if int(entry[0]) + offset not in points:
            points[int(entry[0]) + offset] = {
                "position": [float(entry[2]), float(entry[3])],
                "parent_cables": [],
            }
        points[int(entry[0]) + offset]["parent_cables"].append(int(entry[1]))

    sp_points = {}
    for point in points:
        sp_points[point] = {
            "position": tuple(points[point]["position"]),
            "neighbours": [],
        }
        print(f"Currently adding point {point}")
        for cable in points[point]["parent_cables"]:
            if cables[cable]["capacity"] > 0:
                print(
                    f"Found cable with capacity > 0: {cable} and neighbour points {cables[cable]['neighbour_points']}"
                )
                for neigh_point in cables[cable]["neighbour_points"]:
                    if tuple(points[neigh_point]["position"]) != tuple(
                        points[point]["position"]
                    ):
                        print(f"Adding neighbour point {neigh_point}")
                        sp_points[point]["neighbours"].append(
                            {
                                "id": neigh_point,
                                "cost": cables[cable]["length"],
                                "cable": cable,
                            }
                        )
        print("Done with point, result: ")
        print(sp_points[point])
        print("================================")
        print()
        raise ValueError

    print("SP Points")
    print(sp_points)
    print(offset)
    return kdwrapper
