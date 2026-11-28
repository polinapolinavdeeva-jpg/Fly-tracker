from src.classes import Aircraft


def parse_aircraft_data(data):
    states = data["states"]
    if states is None or len(states) == 0:
        return []

    aircraft = []
    for state in states:
        callsign = state[1]

        if callsign is not None and not callsign.strip():
            callsign = None

        aircraft.append(
            Aircraft(state[0], callsign, state[2], state[7], state[9])
        )
    return aircraft


def get_top_aircraft(aircraft_list, n):
    if n <= 0:
        raise ValueError("n must be positive")
    top_aircraft = [
        aircraft for aircraft in aircraft_list if aircraft.altitude is not None
    ]
    return sorted(top_aircraft, key=lambda x: x.altitude, reverse=True)[:n]


def get_aircraft_by_country(aircraft_list, country):
    country = country.strip().lower()
    filtered_aircraft = [
        aircraft
        for aircraft in aircraft_list
        if aircraft.origin_country.lower() == country
    ]
    return filtered_aircraft


def display_aircraft(aircraft_list):
    for aircraft in aircraft_list:
        print(
            f"Уникальный идентификатор: {aircraft.icao24}\n"
            f"Позывной: {aircraft.callsign}\n"
            f"Страна регистрации: {aircraft.origin_country}\n"
            f"Данные о высоте: {aircraft.altitude}\n"
            f"Данные о скорости: {aircraft.velocity}\n\n"
        )
