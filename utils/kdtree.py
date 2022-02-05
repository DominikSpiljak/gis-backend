from scipy.spatial import KDTree
from geopy import distance


class KDTreeWrapper:
    def __init__(self, points, cables):
        self.__tree = KDTree(
            [
                points[point]["position"]
                for point in points
                if cables[points[point]["parent_cable"]] > 0
            ]
        )
        self.__ids = [
            point for point in points if cables[points[point]["parent_cable"]] > 0
        ]

    def query(self, x, *args, **kwargs):
        results = []
        distances, indices = self.__tree.query(x, *args, **kwargs)
        for i in range(len(x)):
            results.append(
                {
                    "distance": float(distances[i]),
                    "connector_gid": self.__ids[int(indices[i])],
                }
            )
        return results


def get_kdtree(database, crs):

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
        }

    result = database.query(
        f"SELECT izvod.gid, kabel.gid, kabel.ukuparica FROM public.izvod AS izvod, public.kabel AS kabel WHERE ST_DWithin(izvod.geom, kabel.geom, 0.00001);"
    )

    cables = {}

    for entry in result:
        cables[int(entry[1])] = int(entry[2])
        points[int(entry[0])]["parent_cable"] = int(entry[1])

    for point in points:
        cables[points[point]["parent_cable"]] -= points[point]["num_parica"]

    return KDTreeWrapper(points, cables)
