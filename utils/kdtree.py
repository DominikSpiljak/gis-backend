from scipy.spatial import KDTree
import numpy as np


class KDTreeWrapper:
    def __init__(self, coordinates, ids):
        self.__tree = KDTree(coordinates)
        self.__ids = ids

    def query(self, *args, **kwargs):
        distance, index = self.__tree.query(*args, **kwargs)
        return {"distance": float(distance), "id": int(self.__ids[index])}


def get_kdtree():
    # test behaviour
    # TODO: Load connectors from db, filter and load into wrapper
    npoints = 100000000
    points = np.random.rand(npoints, 2)
    ids = np.arange(npoints)
    return KDTreeWrapper(points, ids)
