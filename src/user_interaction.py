from src.classes import NominatimAPI, OpenSkyAPI
from src.utils import (
    display_aircraft,
    get_aircraft_by_country,
    get_top_aircraft,
    parse_aircraft_data,
)


def interaction():
    while True:
        input_country = input("Введите название страны: \n")
        nominatim_api = NominatimAPI()
        try:
            coordinates = nominatim_api.get_data(q=input_country)
        except ValueError:
            print("Страна не найдена")
            continue

        open_sky_api = OpenSkyAPI()
        data = open_sky_api.get_data(coordinates=coordinates)
        aircraft_list = parse_aircraft_data(data)

        while True:
            action = input(
                "1 Показать топ N самолётов по высоте.\n"
                "2 Найти самолёты по стране регистрации.\n"
                "3 Сменить область поиска. \n"
                "4 Завершить программу.\n"
            )
            if action == "1":
                n = input("Введите количество самолетов:\n")
                try:
                    n = int(n)
                except ValueError:
                    print("Некорректное значение")
                    continue

                try:
                    result = get_top_aircraft(aircraft_list, n)
                except ValueError:
                    print("Некорректное значение")
                    continue

                if not result:
                    print("Самолёты с доступными данными о высоте не найдены")
                    continue

                display_aircraft(result)

            elif action == "2":
                name_country = input(
                    "Введите (латиницей) название страны регистрации судна:\n"
                )
                if not name_country.strip():
                    print("Название страны не может быть пустым")
                    continue

                result = get_aircraft_by_country(aircraft_list, name_country)

                if result:
                    display_aircraft(result)
                else:
                    print("Самолеты из указанной страны не найдены")

            elif action == "3":
                break

            elif action == "4":
                print("Завершение работы программы")
                return
            else:
                print("Некорректный ввод")
