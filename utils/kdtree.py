from scipy.spatial import KDTree
from database.db_connect import connect


class KDTreeWrapper:
    def __init__(self, coordinates, ids):
        self.__tree = KDTree(coordinates)
        self.__ids = ids

    def query(self, *args, **kwargs):
        distance, index = self.__tree.query(*args, **kwargs)
        return {"distance": float(distance), "id": int(self.__ids[index])}


def get_kdtree(config_file):
    conn = connect(config_file)

    cur = conn.cursor()
    cur.execute("SELECT gid, lat, long FROM public.izvod WHERE brparica > 0")
    result = cur.fetchall()
    cur.close()

    points = []
    ids = []
    for entry in result:
        points.append([entry[1], entry[2]])
        ids.append(entry[0])

    return KDTreeWrapper(points, ids)
