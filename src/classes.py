import json
import math
import os
import re
from abc import ABC, abstractmethod

import requests


class BaseAPI(ABC):
    @abstractmethod
    def get_data(self, **kwargs):
        pass

    def _make_request(self, url, params):
        headers = {"User-Agent": "FlyTracker/1.0 (suxarev.a86@gmail.com)"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data


class NominatimAPI(BaseAPI):
    def get_data(self, **kwargs):
        q = kwargs.get("q")
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": q,
            "format": "json",
        }
        result = self._make_request(url, params)
        if not result:
            raise ValueError("No results found")
        coordinates = tuple((float(x) for x in result[0]["boundingbox"]))
        return coordinates


class OpenSkyAPI(BaseAPI):
    def get_data(self, **kwargs):
        coordinates = kwargs.get("coordinates")
        url = "https://opensky-network.org/api/states/all"
        params = {
            "lamin": coordinates[0],
            "lamax": coordinates[1],
            "lomin": coordinates[2],
            "lomax": coordinates[3],
        }
        result = self._make_request(url, params)
        return result


class Aircraft:

    def __init__(
        self,
        icao24: str,
        callsign: str | None,
        origin_country: str,
        altitude: float | None,
        velocity: float | None,
    ):
        self.icao24 = icao24
        self.callsign = callsign
        self.origin_country = origin_country
        self.altitude = altitude
        self.velocity = velocity

    @property
    def icao24(self):
        return self.__icao24

    @icao24.setter
    def icao24(self, value):
        self.validate_icao24(value)
        self.__icao24 = value

    @property
    def callsign(self):
        return self.__callsign

    @callsign.setter
    def callsign(self, value):
        self.validate_callsign(value)
        self.__callsign = value

    @property
    def origin_country(self):
        return self.__origin_country

    @origin_country.setter
    def origin_country(self, value):
        self.validate_origin_country(value)
        self.__origin_country = value

    @property
    def altitude(self):
        return self.__altitude

    @altitude.setter
    def altitude(self, value):
        self.validate_altitude(value)
        self.__altitude = value

    @property
    def velocity(self):
        return self.__velocity

    @velocity.setter
    def velocity(self, value):
        self.validate_velocity(value)
        self.__velocity = value

    def validate_icao24(self, icao24):
        pattern = r"[0-9a-fA-F]{6}"

        if not isinstance(icao24, str):
            raise TypeError("icao24 must be a string")

        if re.fullmatch(pattern, icao24) is None:
            raise ValueError("Invalid icao24")

    def validate_callsign(self, callsign):
        if callsign is None:
            return

        if not isinstance(callsign, str):
            raise TypeError("callsign must be string")

        if not callsign.strip():
            raise ValueError("callsing must be filled")

    def validate_origin_country(self, origin_country):
        if not isinstance(origin_country, str):
            raise TypeError("origin_country must be a string")

        if not origin_country.strip():
            raise ValueError("origin_country must be filled")

    def validate_altitude(self, altitude):
        if altitude is None:
            return

        if isinstance(altitude, bool):
            raise TypeError("altitude can`t be a boolean")

        if not isinstance(altitude, (float, int)):
            raise TypeError("altitude must be a float or int else")

        if not math.isfinite(altitude):
            raise ValueError("altitude must be finite")

    def validate_velocity(self, velocity):
        if velocity is None:
            return

        if isinstance(velocity, bool):
            raise TypeError("velocity can`t be a boolean")

        if not isinstance(velocity, (float, int)):
            raise TypeError("velocity must be a float or int else")

        if not math.isfinite(velocity):
            raise ValueError("velocity must be finite")

        if velocity < 0:
            raise ValueError("velocity cannot be negative")

    def compare_speed(self, other):
        if not isinstance(other, Aircraft):
            raise TypeError("other must be an Aircraft")

        if other.velocity is None or self.velocity is None:
            raise ValueError(
                "Cannot compare aircraft: velocity data is missing"
            )

        if other.velocity > self.velocity:
            return -1

        elif other.velocity < self.velocity:
            return 1

        else:
            return 0

    def compare_altitude(self, other):
        if not isinstance(other, Aircraft):
            raise TypeError("other must be an Aircraft")

        if other.altitude is None or self.altitude is None:
            raise ValueError("Cannot compare aircraft: altitude data is missing")

        if other.altitude > self.altitude:
            return -1

        elif other.altitude < self.altitude:
            return 1

        else:
            return 0


class BaseStorage(ABC):
    def connect(self):
        pass

    def disconnect(self):
        pass

    @abstractmethod
    def add_aircraft(self, aircraft: Aircraft):
        pass

    @abstractmethod
    def get_aircraft(self, **kwargs):
        pass

    @abstractmethod
    def delete_aircraft(self, icao24: str):
        pass


class JSONStorage(BaseStorage):
    ALLOWED_FIELDS = {"icao24", "callsign", "origin_country", "altitude", "velocity"}

    def __init__(self, path: str):
        self.__path = path

    def _read_data(self) -> list[dict]:
        if not os.path.isfile(self.__path):
            return []

        try:
            with open(self.__path, "r", encoding="utf-8") as f:
                result = json.load(f)
        except json.JSONDecodeError:
            return []

        if not all(isinstance(item, dict) for item in result):
            raise TypeError("All items must be dictionaries")

        if isinstance(result, list):
            return result
        else:
            raise TypeError("result must be a list")

    def _write_data(self, data: list[dict]):
        with open(self.__path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_aircraft(self, aircraft: Aircraft):
        result = self._read_data()
        aircraft_data = {
            "icao24": aircraft.icao24,
            "callsign": aircraft.callsign,
            "origin_country": aircraft.origin_country,
            "altitude": aircraft.altitude,
            "velocity": aircraft.velocity,
        }
        result.append(aircraft_data)
        self._write_data(result)

    def get_aircraft(self, **kwargs):

        if not kwargs:
            raise ValueError("At least one search criterion is required")

        if not all(key in self.ALLOWED_FIELDS for key in kwargs):
            raise ValueError("Invalid search criterion")

        result = self._read_data()
        ordered_data = []
        for aircraft in result:
            if all(aircraft[key] == value for key, value in kwargs.items()):
                ordered_data.append(aircraft)
        return ordered_data

    def delete_aircraft(self, icao24: str):
        result = self._read_data()
        new_result = [aircraft for aircraft in result if aircraft["icao24"] != icao24]

        if len(result) == len(new_result):
            raise ValueError("Aircraft not found")
        self._write_data(new_result)
