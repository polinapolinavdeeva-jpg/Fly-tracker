from unittest.mock import patch

from src.user_interaction import interaction


@patch("src.user_interaction.NominatimAPI")
def test_country_not_found(mock_nominatim, capsys):
    mock_nominatim.return_value.get_data.side_effect = [
        ValueError,
        (60.0, 70.0, 20.0, 30.0),
    ]

    with patch("builtins.input", side_effect=["Unknown", "Finland", "4"]):
        with patch("src.user_interaction.OpenSkyAPI") as mock_opensky:
            mock_opensky.return_value.get_data.return_value = {"states": []}
            interaction()

    assert "Страна не найдена" in capsys.readouterr().out
    assert mock_nominatim.return_value.get_data.call_count == 2


@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_exit_program(mock_nominatim, mock_opensky, capsys):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}

    with patch("builtins.input", side_effect=["Finland", "4"]):
        interaction()

    assert "Завершение работы программы" in capsys.readouterr().out


@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_change_search_area(mock_nominatim, mock_opensky):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}

    with patch("builtins.input", side_effect=["Finland", "3", "Germany", "4"]):
        interaction()

    assert mock_nominatim.return_value.get_data.call_count == 2
    assert mock_opensky.return_value.get_data.call_count == 2


@patch("src.user_interaction.display_aircraft")
@patch("src.user_interaction.get_top_aircraft")
@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_show_top_aircraft(mock_nominatim, mock_opensky, mock_get_top, mock_display):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}
    mock_get_top.return_value = ["aircraft1", "aircraft2"]

    with patch("builtins.input", side_effect=["Finland", "1", "2", "4"]):
        interaction()

    mock_get_top.assert_called_once_with([], 2)
    mock_display.assert_called_once_with(["aircraft1", "aircraft2"])


@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_invalid_number_of_aircraft(mock_nominatim, mock_opensky, capsys):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}

    with patch("builtins.input", side_effect=["Finland", "1", "abc", "4"]):
        interaction()

    assert "Некорректное значение" in capsys.readouterr().out


@patch("src.user_interaction.get_top_aircraft")
@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_top_aircraft_value_error(mock_nominatim, mock_opensky, mock_get_top, capsys):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}
    mock_get_top.side_effect = ValueError

    with patch("builtins.input", side_effect=["Finland", "1", "0", "4"]):
        interaction()

    assert "Некорректное значение" in capsys.readouterr().out


@patch("src.user_interaction.get_top_aircraft")
@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_top_aircraft_not_found(mock_nominatim, mock_opensky, mock_get_top, capsys):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}
    mock_get_top.return_value = []

    with patch("builtins.input", side_effect=["Finland", "1", "5", "4"]):
        interaction()

    assert (
        "Самолёты с доступными данными о высоте не найдены" in capsys.readouterr().out
    )


@patch("src.user_interaction.display_aircraft")
@patch("src.user_interaction.get_aircraft_by_country")
@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_find_aircraft_by_country(
    mock_nominatim, mock_opensky, mock_get_by_country, mock_display
):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}
    mock_get_by_country.return_value = ["aircraft1"]

    with patch("builtins.input", side_effect=["Finland", "2", "Germany", "4"]):
        interaction()

    mock_get_by_country.assert_called_once_with([], "Germany")
    mock_display.assert_called_once_with(["aircraft1"])


@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_empty_country_name(mock_nominatim, mock_opensky, capsys):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}

    with patch("builtins.input", side_effect=["Finland", "2", "   ", "4"]):
        interaction()

    assert "Название страны не может быть пустым" in capsys.readouterr().out


@patch("src.user_interaction.get_aircraft_by_country")
@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_aircraft_by_country_not_found(
    mock_nominatim, mock_opensky, mock_get_by_country, capsys
):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}
    mock_get_by_country.return_value = []

    with patch("builtins.input", side_effect=["Finland", "2", "Germany", "4"]):
        interaction()

    assert "Самолеты из указанной страны не найдены" in capsys.readouterr().out


@patch("src.user_interaction.get_aircraft_by_country")
@patch("src.user_interaction.OpenSkyAPI")
@patch("src.user_interaction.NominatimAPI")
def test_invalid_menu_action(mock_nominatim, mock_opensky, mock_get_by_country, capsys):
    mock_nominatim.return_value.get_data.return_value = (60.0, 70.0, 20.0, 30.0)
    mock_opensky.return_value.get_data.return_value = {"states": []}

    with patch("builtins.input", side_effect=["Finland", "5", "4"]):
        interaction()

    assert "Некорректный ввод" in capsys.readouterr().out
