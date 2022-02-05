from geopy.geocoders import ArcGIS
import pyproj


class Georeferencer:
    def __init__(self, crs):
        self.georeferencer = ArcGIS()
        self.transformer = pyproj.Transformer.from_crs("EPSG:4326", f"EPSG:{crs}")

    def georeference(self, addresses):
        result = {}
        for address in addresses:
            location = self.georeferencer.geocode(address)
            x, y = self.transformer.transform(location.latitude, location.longitude)
            result[address] = {"x": x, "y": y}
        return result


if __name__ == "__main__":
    refer = Georeferencer()
    print(
        refer.georeference(
            [
                "Špičkovina",
                "Trg Josipa Jelačića",
            ]
        )
    )
