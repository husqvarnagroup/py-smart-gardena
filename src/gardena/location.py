import json
from gardena.base_gardena_class import BaseGardenaClass
from gardena.gateway import Gateway
from gardena.mower import Mower


class Location(BaseGardenaClass):
    """Keep informations about gardena locations (gardens, ..) and devices"""

    latitude = None
    longitude = None
    address = None
    city = None
    sunrise = None
    sunset = None
    time_zone = None
    time_zone_offset = None
    gateways = {}
    mowers = {}
    categories_data = {
        "gateway": {"class": Gateway, "map": gateways},
        "mower": {"class": Mower, "map": mowers},
    }

    def update_information(self, information):
        super(Location, self).update_information(information)
        if "geo_position" in information:
            self.set_field_if_exists(
                information["geo_position"], "latitude", "latitude"
            )
            self.set_field_if_exists(
                information["geo_position"], "longitude", "longitude"
            )
            self.set_field_if_exists(information["geo_position"], "address", "address")
            self.set_field_if_exists(information["geo_position"], "city", "city")
            self.set_field_if_exists(information["geo_position"], "sunrise", "sunrise")
            self.set_field_if_exists(information["geo_position"], "sunset", "sunset")
            self.set_field_if_exists(
                information["geo_position"], "time_zone", "time_zone"
            )
            self.set_field_if_exists(
                information["geo_position"], "time_zone_offset", "time_zone_offset"
            )

    def add_or_update_device(self, device=None):
        if device is None:
            return
        if device["category"] not in self.categories_data:
            return

        device_class = self.categories_data[device["category"]]["class"]
        device_map = self.categories_data[device["category"]]["map"]
        if device["id"] not in device_map:
            device_map[device["id"]] = device_class(smart_system=self.smart_system)
        device_map[device["id"]].update_information(device)

    def update_devices(self):
        url = "https://smart.gardena.com/sg-1/devices/"
        params = (("locationId", self.id),)
        response = self.smart_system.request_session.get(
            url, headers=self.smart_system.create_header(), params=params
        )
        response.raise_for_status()
        response_data = json.loads(response.content.decode("utf-8"))
        for device in response_data["devices"]:
            self.add_or_update_device(device)
