from scipy.spatial import KDTree
from geopy import distance


class KDTreeWrapper:
    def __init__(self, coordinates, ids):
        self.__tree = KDTree(coordinates)
        self.__ids = ids

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


def get_kdtree(database):

    result = database.query(
        "SELECT gid, ST_X(geom), ST_Y(geom) FROM public.izvod WHERE brparica > 0"
    )

    points = []
    ids = []
    for entry in result:
        points.append([entry[1], entry[2]])
        ids.append(entry[0])

    return KDTreeWrapper(points, ids)
