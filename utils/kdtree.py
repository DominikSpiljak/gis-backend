from scipy.spatial import KDTree
from geopy import distance


class KDTreeWrapper:
    def __init__(self, points, cables):
        self.__tree = KDTree(
            [
                points[point]["position"]
                for point in points
                if any(
                    cables[cable] > 0
                    for cable in cables[points[point]["parent_cables"]]
                )
            ]
        )
        self.__ids = [
            point
            for point in points
            if any(
                cables[cable] > 0 for cable in cables[points[point]["parent_cables"]]
            )
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
        f"SELECT izvod.gid, kabel.gid, kabel.ukuparica FROM public.izvod AS izvod, public.kabel AS kabel WHERE ST_DWithin(izvod.geom, kabel.geom, 0.00001);"
    )

    cables = {}

    for entry in result:
        cables[int(entry[1])] = int(entry[2])
        points[int(entry[0])]["parent_cables"].append(int(entry[1]))

    for point in points:
        num_parica = points[point]["num_parica"]
        for cable in points[point]["parent_cables"]:
            if num_parica == 0:
                break
            elif num_parica > cables[cable]:
                num_parica -= cables[cable]
                cables[cable] = 0
            else:
                cables[cable] -= num_parica
                break

    return KDTreeWrapper(points, cables)
