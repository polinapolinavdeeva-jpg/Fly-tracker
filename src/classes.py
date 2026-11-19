from abc import ABC, abstractmethod
import requests

class BaseAPI(ABC):
    @abstractmethod
    def get_data(self, **kwargs):
        pass

    def _make_request(self, url, params):
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()


class NominatimAPI(BaseAPI):
    def get_data(self, **kwargs):
        pass

class OpenSkyAPI(BaseAPI):
    def get_data(self, **kwargs):
        pass

class Aircraft():
    def __init__(self, altitude):
        self.altitude = altitude

