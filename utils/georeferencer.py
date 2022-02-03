from geopy.geocoders import ArcGIS


class Georeferencer:
    def __init__(self):
        self.georeferencer = ArcGIS()

    def georeference(self, addresses):
        result = {}
        for address in addresses:
            location = self.georeferencer.geocode(address, out_sr=3765)
            result[address] = {"lat": location.latitude, "long": location.longitude}
        return result


if __name__ == "__main__":
    refer = Georeferencer()
    print(
        refer.georeference(
            [
                "1600 Amphitheatre Parkway, Mountain View, CA",
                "Ulica Matije GUpca 24, Bedekovčina",
            ]
        )
    )
