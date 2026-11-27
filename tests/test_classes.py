import json
from unittest.mock import Mock, patch

import pytest

from src.classes import (
    Aircraft,
    BaseAPI,
    BaseStorage,
    JSONStorage,
    NominatimAPI,
    OpenSkyAPI,
)


# Вспомогательная функция для создания тестового самолёта
def make_aircraft(
    icao24="ABC123",
    callsign="TEST123",
    origin_country="Finland",
    altitude=10000.0,
    velocity=250.0,
):
    return Aircraft(icao24, callsign, origin_country, altitude, velocity)


def test_base_api_is_abstract():
    with pytest.raises(TypeError):
        BaseAPI()


def test_base_api_make_request():
    api = NominatimAPI()
    expected_data = [{"name": "Finland"}]

    response = Mock()
    response.json.return_value = expected_data

    with patch("src.classes.requests.get", return_value=response) as mock_get:
        result = api._make_request("https://example.com", {"q": "Finland"})

    assert result == expected_data
    mock_get.assert_called_once_with(
        "https://example.com",
        params={"q": "Finland"},
        headers={"User-Agent": "FlyTracker/1.0 (suxarev.a86@gmail.com)"},
    )
    response.raise_for_status.assert_called_once()
    response.json.assert_called_once()


def test_base_api_request_error_propagates():
    api = NominatimAPI()
    response = Mock()
    response.raise_for_status.side_effect = Exception("HTTP error")

    with patch("src.classes.requests.get", return_value=response):
        with pytest.raises(Exception, match="HTTP error"):
            api._make_request("https://example.com", {})


def test_nominatim_get_data_returns_coordinates():
    api = NominatimAPI()
    api_response = [
        {
            "boundingbox": [
                "59.4541578",
                "70.0922930",
                "19.0832000",
                "31.5867071",
            ]
        }
    ]

    with patch.object(api, "_make_request", return_value=api_response):
        result = api.get_data(q="Finland")

    assert result == (
        59.4541578,
        70.0922930,
        19.0832000,
        31.5867071,
    )


def test_nominatim_get_data_raises_error_when_result_is_empty():
    api = NominatimAPI()

    with patch.object(api, "_make_request", return_value=[]):
        with pytest.raises(ValueError, match="No results found"):
            api.get_data(q="Unknown place")


def test_opensky_get_data_passes_coordinates_to_request():
    api = OpenSkyAPI()
    coordinates = (59.45, 70.09, 19.08, 31.58)
    expected_data = {"time": 123456, "states": []}

    with patch.object(
            api, "_make_request", return_value=expected_data) as mock_request:
        result = api.get_data(coordinates=coordinates)

    assert result == expected_data
    mock_request.assert_called_once_with(
        "https://opensky-network.org/api/states/all",
        {
            "lamin": 59.45,
            "lamax": 70.09,
            "lomin": 19.08,
            "lomax": 31.58,
        },
    )


def test_base_storage_is_abstract():
    with pytest.raises(TypeError):
        BaseStorage()


def test_aircraft_init():
    aircraft = make_aircraft()

    assert aircraft.icao24 == "ABC123"
    assert aircraft.callsign == "TEST123"
    assert aircraft.origin_country == "Finland"
    assert aircraft.altitude == 10000.0
    assert aircraft.velocity == 250.0


def test_aircraft_allows_none_callsign_altitude_and_velocity():
    aircraft = make_aircraft(
        callsign=None,
        altitude=None,
        velocity=None,
    )

    assert aircraft.callsign is None
    assert aircraft.altitude is None
    assert aircraft.velocity is None


@pytest.mark.parametrize("icao24", [123456, None, True])
def test_aircraft_icao24_rejects_non_string(icao24):
    with pytest.raises(TypeError):
        make_aircraft(icao24=icao24)


@pytest.mark.parametrize(
    "icao24",
    ["ABC12", "ABC1234", "GHIJKL", "", "ABC 12"],
)
def test_aircraft_icao24_rejects_invalid_format(icao24):
    with pytest.raises(ValueError):
        make_aircraft(icao24=icao24)


@pytest.mark.parametrize("icao24", ["ABC123", "abcdef", "a1B2c3"])
def test_aircraft_icao24_accepts_six_hex_characters(icao24):
    aircraft = make_aircraft(icao24=icao24)

    assert aircraft.icao24 == icao24


@pytest.mark.parametrize("callsign", [123, True, []])
def test_aircraft_callsign_rejects_non_string(callsign):
    with pytest.raises(TypeError):
        make_aircraft(callsign=callsign)


@pytest.mark.parametrize("callsign", ["", "   ", "\t\n"])
def test_aircraft_callsign_rejects_empty_string(callsign):
    with pytest.raises(ValueError):
        make_aircraft(callsign=callsign)


@pytest.mark.parametrize("country", [123, None, True, []])
def test_aircraft_origin_country_rejects_non_string(country):
    with pytest.raises(TypeError):
        make_aircraft(origin_country=country)


@pytest.mark.parametrize("country", ["", "   ", "\t\n"])
def test_aircraft_origin_country_rejects_empty_string(country):
    with pytest.raises(ValueError):
        make_aircraft(origin_country=country)


@pytest.mark.parametrize("altitude", ["1000", [], True])
def test_aircraft_altitude_rejects_invalid_type(altitude):
    with pytest.raises(TypeError):
        make_aircraft(altitude=altitude)


@pytest.mark.parametrize("altitude", [float("inf"), float("-inf"), float("nan")])
def test_aircraft_altitude_rejects_non_finite_value(altitude):
    with pytest.raises(ValueError):
        make_aircraft(altitude=altitude)


@pytest.mark.parametrize("altitude", [0, 1000, 1000.5, None])
def test_aircraft_altitude_accepts_valid_values(altitude):
    aircraft = make_aircraft(altitude=altitude)

    assert aircraft.altitude == altitude


@pytest.mark.parametrize("velocity", ["250", [], True])
def test_aircraft_velocity_rejects_invalid_type(velocity):
    with pytest.raises(TypeError):
        make_aircraft(velocity=velocity)


@pytest.mark.parametrize("velocity", [-1, -0.1])
def test_aircraft_velocity_rejects_negative_value(velocity):
    with pytest.raises(ValueError, match="cannot be negative"):
        make_aircraft(velocity=velocity)


@pytest.mark.parametrize("velocity", [float("inf"), float("-inf"), float("nan")])
def test_aircraft_velocity_rejects_non_finite_value(velocity):
    with pytest.raises(ValueError, match="must be finite"):
        make_aircraft(velocity=velocity)


@pytest.mark.parametrize("velocity", [0, 250, 250.5, None])
def test_aircraft_velocity_accepts_valid_values(velocity):
    aircraft = make_aircraft(velocity=velocity)

    assert aircraft.velocity == velocity


def test_aircraft_setters_validate_new_values():
    aircraft = make_aircraft()

    aircraft.altitude = 12000
    aircraft.velocity = 300
    aircraft.callsign = None

    assert aircraft.altitude == 12000
    assert aircraft.velocity == 300
    assert aircraft.callsign is None


def test_aircraft_setter_rejects_invalid_value():
    aircraft = make_aircraft()

    with pytest.raises(ValueError):
        aircraft.icao24 = "INVALID"


def test_compare_speed_returns_one_when_self_is_faster():
    aircraft_1 = make_aircraft(velocity=300)
    aircraft_2 = make_aircraft(icao24="DEF456", velocity=200)

    assert aircraft_1.compare_speed(aircraft_2) == 1


def test_compare_speed_returns_minus_one_when_self_is_slower():
    aircraft_1 = make_aircraft(velocity=200)
    aircraft_2 = make_aircraft(icao24="DEF456", velocity=300)

    assert aircraft_1.compare_speed(aircraft_2) == -1


def test_compare_speed_returns_zero_when_speeds_are_equal():
    aircraft_1 = make_aircraft(velocity=250)
    aircraft_2 = make_aircraft(icao24="DEF456", velocity=250)

    assert aircraft_1.compare_speed(aircraft_2) == 0


def test_compare_speed_rejects_non_aircraft():
    aircraft = make_aircraft()

    with pytest.raises(TypeError):
        aircraft.compare_speed("not an aircraft")


def test_compare_speed_rejects_missing_velocity():
    aircraft_1 = make_aircraft(velocity=None)
    aircraft_2 = make_aircraft(icao24="DEF456", velocity=200)

    with pytest.raises(ValueError, match="velocity data is missing"):
        aircraft_1.compare_speed(aircraft_2)


def test_compare_altitude_returns_one_when_self_is_higher():
    aircraft_1 = make_aircraft(altitude=12000)
    aircraft_2 = make_aircraft(icao24="DEF456", altitude=10000)

    assert aircraft_1.compare_altitude(aircraft_2) == 1


def test_compare_altitude_returns_minus_one_when_self_is_lower():
    aircraft_1 = make_aircraft(altitude=10000)
    aircraft_2 = make_aircraft(icao24="DEF456", altitude=12000)

    assert aircraft_1.compare_altitude(aircraft_2) == -1


def test_compare_altitude_returns_zero_when_altitudes_are_equal():
    aircraft_1 = make_aircraft(altitude=10000)
    aircraft_2 = make_aircraft(icao24="DEF456", altitude=10000)

    assert aircraft_1.compare_altitude(aircraft_2) == 0


def test_compare_altitude_rejects_non_aircraft():
    aircraft = make_aircraft()

    with pytest.raises(TypeError):
        aircraft.compare_altitude("not an aircraft")


def test_compare_altitude_rejects_missing_altitude():
    aircraft_1 = make_aircraft(altitude=None)
    aircraft_2 = make_aircraft(icao24="DEF456", altitude=10000)

    with pytest.raises(ValueError, match="altitude data is missing"):
        aircraft_1.compare_altitude(aircraft_2)


def test_json_storage_read_returns_empty_list_when_file_does_not_exist(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")

    assert storage._read_data() == []


def test_json_storage_read_returns_empty_list_when_file_is_empty(tmp_path):
    file_path = tmp_path / "aircraft.json"
    file_path.write_text("", encoding="utf-8")
    storage = JSONStorage(file_path)

    assert storage._read_data() == []


def test_json_storage_read_returns_data(tmp_path):
    file_path = tmp_path / "aircraft.json"
    expected_data = [{"icao24": "ABC123", "origin_country": "Finland"}]
    file_path.write_text(
        json.dumps(expected_data),
        encoding="utf-8",
    )
    storage = JSONStorage(file_path)

    assert storage._read_data() == expected_data


def test_json_storage_read_rejects_non_dictionary_items(tmp_path):
    file_path = tmp_path / "aircraft.json"
    file_path.write_text(json.dumps(["not a dictionary"]), encoding="utf-8")
    storage = JSONStorage(file_path)

    with pytest.raises(TypeError, match="All items must be dictionaries"):
        storage._read_data()


def test_json_storage_read_rejects_non_list_data(tmp_path):
    file_path = tmp_path / "aircraft.json"
    file_path.write_text(json.dumps({"icao24": "ABC123"}), encoding="utf-8")
    storage = JSONStorage(file_path)

    with pytest.raises(TypeError):
        storage._read_data()


def test_json_storage_write_data(tmp_path):
    file_path = tmp_path / "aircraft.json"
    storage = JSONStorage(file_path)
    data = [{"icao24": "ABC123", "origin_country": "Finland"}]

    storage._write_data(data)

    with open(file_path, encoding="utf-8") as file:
        result = json.load(file)

    assert result == data


def test_json_storage_add_aircraft(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")
    aircraft = make_aircraft()

    storage.add_aircraft(aircraft)

    result = storage._read_data()

    assert result == [
        {
            "icao24": "ABC123",
            "callsign": "TEST123",
            "origin_country": "Finland",
            "altitude": 10000.0,
            "velocity": 250.0,
        }
    ]


def test_json_storage_add_multiple_aircraft(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")
    aircraft_1 = make_aircraft()
    aircraft_2 = make_aircraft(
        icao24="DEF456",
        callsign="TEST456",
        origin_country="Germany",
    )

    storage.add_aircraft(aircraft_1)
    storage.add_aircraft(aircraft_2)

    result = storage._read_data()

    assert len(result) == 2
    assert result[0]["icao24"] == "ABC123"
    assert result[1]["icao24"] == "DEF456"


def test_json_storage_get_aircraft_by_icao24(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")
    storage.add_aircraft(make_aircraft())
    storage.add_aircraft(make_aircraft(icao24="DEF456"))

    result = storage.get_aircraft(icao24="ABC123")

    assert len(result) == 1
    assert result[0]["icao24"] == "ABC123"


def test_json_storage_get_aircraft_by_multiple_criteria(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")
    storage.add_aircraft(make_aircraft())
    storage.add_aircraft(
        make_aircraft(
            icao24="DEF456",
            origin_country="Germany",
        )
    )

    result = storage.get_aircraft(
        origin_country="Finland",
        callsign="TEST123",
    )

    assert len(result) == 1
    assert result[0]["icao24"] == "ABC123"


def test_json_storage_get_aircraft_returns_empty_list_when_not_found(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")
    storage.add_aircraft(make_aircraft())

    result = storage.get_aircraft(icao24="FFFFFF")

    assert result == []


def test_json_storage_get_aircraft_requires_criteria(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")

    with pytest.raises(ValueError, match="At least one search criterion"):
        storage.get_aircraft()


def test_json_storage_get_aircraft_rejects_unknown_criteria(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")

    with pytest.raises(ValueError, match="Invalid search criterion"):
        storage.get_aircraft(unknown_field="value")


def test_json_storage_delete_aircraft(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")
    storage.add_aircraft(make_aircraft())
    storage.add_aircraft(make_aircraft(icao24="DEF456"))

    storage.delete_aircraft("ABC123")

    result = storage._read_data()

    assert len(result) == 1
    assert result[0]["icao24"] == "DEF456"


def test_json_storage_delete_aircraft_raises_error_when_not_found(tmp_path):
    storage = JSONStorage(tmp_path / "aircraft.json")
    storage.add_aircraft(make_aircraft())

    with pytest.raises(ValueError, match="Aircraft not found"):
        storage.delete_aircraft("FFFFFF")
