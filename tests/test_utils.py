import pytest

from src.classes import Aircraft
from src.utils import (
    display_aircraft,
    get_aircraft_by_country,
    get_top_aircraft,
    parse_aircraft_data,
)

# =========================
# Вспомогательная функция
# =========================


def make_aircraft(
    icao24="ABC123",
    callsign="TEST123",
    origin_country="Finland",
    altitude=10000.0,
    velocity=250.0,
):
    return Aircraft(icao24, callsign, origin_country, altitude, velocity)


# =========================
# parse_aircraft_data
# =========================


def test_parse_aircraft_data_returns_aircraft_objects():
    data = {
        "states": [
            [
                "abc123",  # 0: icao24
                "TEST123",  # 1: callsign
                "Finland",  # 2: origin_country
                None,
                None,
                25.0,
                60.0,
                10000.0,  # 7: altitude
                False,
                250.0,  # 9: velocity
            ]
        ]
    }

    result = parse_aircraft_data(data)

    assert len(result) == 1
    assert isinstance(result[0], Aircraft)
    assert result[0].icao24 == "abc123"
    assert result[0].callsign == "TEST123"
    assert result[0].origin_country == "Finland"
    assert result[0].altitude == 10000.0
    assert result[0].velocity == 250.0


def test_parse_aircraft_data_returns_empty_list_when_states_is_none():
    data = {"states": None}

    assert parse_aircraft_data(data) == []


def test_parse_aircraft_data_returns_empty_list_when_states_is_empty():
    data = {"states": []}

    assert parse_aircraft_data(data) == []


def test_parse_aircraft_data_handles_none_callsign():
    data = {
        "states": [
            ["abc123", None, "Finland", None, None, 25.0, 60.0, 10000.0, False, 250.0]
        ]
    }

    result = parse_aircraft_data(data)

    assert result[0].callsign is None


@pytest.mark.parametrize("callsign", ["", "   ", "\t\n"])
def test_parse_aircraft_data_converts_empty_callsign_to_none(callsign):
    data = {
        "states": [
            [
                "abc123",
                callsign,
                "Finland",
                None,
                None,
                25.0,
                60.0,
                10000.0,
                False,
                250.0,
            ]
        ]
    }

    result = parse_aircraft_data(data)

    assert result[0].callsign is None


def test_parse_aircraft_data_handles_missing_altitude_and_velocity():
    data = {
        "states": [
            ["abc123", "TEST123", "Finland", None, None, 25.0, 60.0, None, False, None]
        ]
    }

    result = parse_aircraft_data(data)

    assert result[0].altitude is None
    assert result[0].velocity is None


def test_parse_aircraft_data_handles_multiple_aircraft():
    data = {
        "states": [
            [
                "abc123",
                "TEST123",
                "Finland",
                None,
                None,
                25.0,
                60.0,
                10000.0,
                False,
                250.0,
            ],
            [
                "def456",
                "TEST456",
                "Germany",
                None,
                None,
                26.0,
                61.0,
                11000.0,
                False,
                260.0,
            ],
        ]
    }

    result = parse_aircraft_data(data)

    assert len(result) == 2
    assert result[0].icao24 == "abc123"
    assert result[1].icao24 == "def456"


def test_parse_aircraft_data_raises_error_for_invalid_icao24():
    data = {
        "states": [
            [
                "invalid",
                "TEST123",
                "Finland",
                None,
                None,
                25.0,
                60.0,
                10000.0,
                False,
                250.0,
            ]
        ]
    }

    with pytest.raises(ValueError):
        parse_aircraft_data(data)


def test_parse_aircraft_data_raises_error_when_states_key_is_missing():
    data = {}

    with pytest.raises(KeyError):
        parse_aircraft_data(data)


# =========================
# get_top_aircraft
# =========================


def test_get_top_aircraft_returns_sorted_list():
    aircraft_list = [
        make_aircraft(altitude=9000),
        make_aircraft(icao24="DEF456", altitude=12000),
        make_aircraft(icao24="789ABC", altitude=10000),
    ]

    result = get_top_aircraft(aircraft_list, 3)

    assert [aircraft.altitude for aircraft in result] == [
        12000,
        10000,
        9000,
    ]


def test_get_top_aircraft_returns_only_n_aircraft():
    aircraft_list = [
        make_aircraft(altitude=9000),
        make_aircraft(icao24="DEF456", altitude=12000),
        make_aircraft(icao24="789ABC", altitude=10000),
    ]

    result = get_top_aircraft(aircraft_list, 2)

    assert len(result) == 2
    assert [aircraft.altitude for aircraft in result] == [12000, 10000]


def test_get_top_aircraft_excludes_aircraft_without_altitude():
    aircraft_list = [
        make_aircraft(altitude=9000),
        make_aircraft(icao24="DEF456", altitude=None),
        make_aircraft(icao24="789ABC", altitude=10000),
    ]

    result = get_top_aircraft(aircraft_list, 3)

    assert len(result) == 2
    assert all(aircraft.altitude is not None for aircraft in result)


def test_get_top_aircraft_returns_empty_list_when_no_altitude():
    aircraft_list = [
        make_aircraft(altitude=None),
        make_aircraft(icao24="DEF456", altitude=None),
    ]

    assert get_top_aircraft(aircraft_list, 5) == []


def test_get_top_aircraft_returns_all_when_n_exceeds_list_length():
    aircraft_list = [
        make_aircraft(altitude=9000),
        make_aircraft(icao24="DEF456", altitude=12000),
    ]

    result = get_top_aircraft(aircraft_list, 10)

    assert len(result) == 2


def test_get_top_aircraft_raises_error_when_n_is_zero():
    with pytest.raises(ValueError, match="n must be positive"):
        get_top_aircraft([], 0)


def test_get_top_aircraft_raises_error_when_n_is_negative():
    with pytest.raises(ValueError, match="n must be positive"):
        get_top_aircraft([], -1)


def test_get_top_aircraft_returns_empty_list_for_empty_input():
    assert get_top_aircraft([], 5) == []


# =========================
# get_aircraft_by_country
# =========================


def test_get_aircraft_by_country_returns_matching_aircraft():
    aircraft_list = [
        make_aircraft(),
        make_aircraft(icao24="DEF456", origin_country="Germany"),
        make_aircraft(icao24="789ABC", origin_country="Finland"),
    ]

    result = get_aircraft_by_country(aircraft_list, "Finland")

    assert len(result) == 2
    assert all(aircraft.origin_country == "Finland" for aircraft in result)


def test_get_aircraft_by_country_ignores_case():
    aircraft_list = [
        make_aircraft(origin_country="Finland"),
        make_aircraft(icao24="DEF456", origin_country="Germany"),
    ]

    result = get_aircraft_by_country(aircraft_list, "fInLaNd")

    assert len(result) == 1
    assert result[0].origin_country == "Finland"


def test_get_aircraft_by_country_strips_whitespace():
    aircraft_list = [make_aircraft()]

    result = get_aircraft_by_country(aircraft_list, "  Finland  ")

    assert len(result) == 1


def test_get_aircraft_by_country_returns_empty_list_when_not_found():
    aircraft_list = [make_aircraft()]

    result = get_aircraft_by_country(aircraft_list, "France")

    assert result == []


def test_get_aircraft_by_country_returns_empty_list_for_empty_input():
    assert get_aircraft_by_country([], "Finland") == []


# =========================
# display_aircraft
# =========================


def test_display_aircraft_prints_aircraft_data(capsys):
    aircraft_list = [make_aircraft()]

    display_aircraft(aircraft_list)

    captured = capsys.readouterr()

    assert "ABC123" in captured.out
    assert "TEST123" in captured.out
    assert "Finland" in captured.out
    assert "10000.0" in captured.out
    assert "250.0" in captured.out


def test_display_aircraft_prints_none_values(capsys):
    aircraft_list = [make_aircraft(callsign=None, altitude=None, velocity=None)]

    display_aircraft(aircraft_list)

    captured = capsys.readouterr()

    assert "None" in captured.out


def test_display_aircraft_does_not_print_for_empty_list(capsys):
    display_aircraft([])

    captured = capsys.readouterr()

    assert captured.out == ""
