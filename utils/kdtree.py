from scipy.spatial import KDTree
from geopy import distance


class KDTreeWrapper:
    def __init__(self, coordinates, ids):
        self.__tree = KDTree(coordinates)
        self.__coordinates = coordinates
        self.__ids = ids

    def query(self, x, *args, **kwargs):
        results = []
        _, indices = self.__tree.query(x, *args, **kwargs)
        for i, x_ in enumerate(x):
            results.append(
                {
                    "distance": distance.geodesic(
                        tuple(x_),
                        tuple(self.__coordinates[int(indices[i])]),
                        ellipsoid="GRS-80",
                    ).meters,
                    "connector_gid": self.__ids[int(indices[i])],
                }
            )
        return results


def get_kdtree(database):

    result = database.query(
        "SELECT gid, lat, long FROM public.izvod WHERE brparica > 0"
    )

    points = []
    ids = []
    for entry in result:
        points.append([entry[1], entry[2]])
        ids.append(entry[0])

    return KDTreeWrapper(points, ids)
