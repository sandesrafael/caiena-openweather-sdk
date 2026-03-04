from datetime import date, datetime

import requests

from .config import BASE_URL, CURRENT_ENDPOINT, FORECAST_ENDPOINT, GEO_BASE_URL, LANG, UNITS
from .exceptions import APIError, CityNotFoundError, InvalidAPIKeyError, RateLimitError
from .models import CurrentWeather, DailyForecast


class OpenWeatherSDK:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def _make_request(self, base_url: str, endpoint: str, params: dict) -> dict:
        url = f"{base_url}{endpoint}"
        request_params = dict(params)
        request_params["appid"] = self.api_key

        response = self.session.get(url, params=request_params, timeout=10)

        if response.status_code == 404:
            raise CityNotFoundError("Cidade nao encontrada")
        if response.status_code == 401:
            raise InvalidAPIKeyError("Chave de API invalida")
        if response.status_code == 429:
            raise RateLimitError("Limite de requisicoes excedido")
        if response.status_code != 200:
            raise APIError(f"Erro {response.status_code}: {response.text}")

        return response.json()

    def _get_location(
        self,
        city: str,
        country: str = "BR",
        state: str | None = None,
    ) -> dict:
        query_parts = [city]
        if state:
            query_parts.append(state)
        query_parts.append(country)

        params = {"q": ",".join(query_parts), "limit": 1}
        data = self._make_request(GEO_BASE_URL, "/geo/1.0/direct", params)

        if not data:
            raise CityNotFoundError(f"Cidade nao encontrada: {city}")

        location = data[0]
        return {
            "lat": location["lat"],
            "lon": location["lon"],
            "name": location.get("name", city),
            "state": location.get("state"),
        }

    def get_current(
        self,
        city: str,
        country: str = "BR",
        state: str | None = None,
    ) -> CurrentWeather:
        location = self._get_location(city, country, state)

        params = {
            "lat": location["lat"],
            "lon": location["lon"],
            "units": UNITS,
            "lang": LANG,
        }
        data = self._make_request(BASE_URL, CURRENT_ENDPOINT, params)
        dt = datetime.fromtimestamp(data["dt"])

        return CurrentWeather(
            city=location["name"],
            state=location["state"],
            temp=round(data["main"]["temp"], 1),
            description=data["weather"][0]["description"],
            date=dt.strftime("%d/%m"),
        )

    def get_five_day_daily_forecast(
        self,
        city: str,
        country: str = "BR",
        state: str | None = None,
    ) -> list[DailyForecast]:
        location = self._get_location(city, country, state)
        params = {
            "lat": location["lat"],
            "lon": location["lon"],
            "units": UNITS,
            "lang": LANG,
        }
        data = self._make_request(BASE_URL, FORECAST_ENDPOINT, params)

        daily_temps: dict[date, list[float]] = {}
        today = datetime.now().date()

        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.date()

            if date_key <= today or (date_key - today).days > 5:
                continue

            if date_key not in daily_temps:
                daily_temps[date_key] = []
            daily_temps[date_key].append(item["main"]["temp"])

        result = []
        for date_key in sorted(daily_temps.keys()):
            avg = round(sum(daily_temps[date_key]) / len(daily_temps[date_key]), 1)
            result.append(DailyForecast(date=date_key.strftime("%d/%m"), avg_temp=avg))

        return result[:5]
