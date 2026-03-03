from datetime import date, datetime
import re
from typing import Dict, List, Tuple
import unicodedata

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

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""
        text = unicodedata.normalize("NFKD", value)
        text = "".join(char for char in text if not unicodedata.combining(char))
        text = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip().lower()
        return re.sub(r"\s+", " ", text)

    def _is_city_match(
        self,
        location: dict,
        city: str,
        country: str,
        state: str | None,
    ) -> bool:
        candidate_names = []

        if location.get("name"):
            candidate_names.append(location["name"])

        local_names = location.get("local_names")
        if isinstance(local_names, dict):
            candidate_names.extend(str(value) for value in local_names.values())

        normalized_city = self._normalize_text(city)
        normalized_candidates = {self._normalize_text(name) for name in candidate_names if name}
        if normalized_city not in normalized_candidates:
            return False

        if self._normalize_text(location.get("country")) != self._normalize_text(country):
            return False

        if state and self._normalize_text(location.get("state")) != self._normalize_text(state):
            return False

        return True

    def _get_coordinates(
        self,
        city: str,
        country: str = "BR",
        state: str | None = None,
    ) -> Tuple[float, float]:
        query_parts = [city]
        if state:
            query_parts.append(state)
        query_parts.append(country)

        params = {"q": ",".join(query_parts), "limit": 5}
        data = self._make_request(GEO_BASE_URL, "/geo/1.0/direct", params)

        if not data:
            raise CityNotFoundError(f"Coordenadas nao encontradas para {city}")

        for location in data:
            if self._is_city_match(location, city, country, state):
                return location["lat"], location["lon"]

        raise CityNotFoundError("Cidade nao encontrada para os parametros informados")

    def get_current(
        self,
        city: str,
        country: str = "BR",
        state: str | None = None,
    ) -> CurrentWeather:
        lat, lon = self._get_coordinates(city, country, state)

        params = {
            "lat": lat,
            "lon": lon,
            "units": UNITS,
            "lang": LANG,
        }
        data = self._make_request(BASE_URL, CURRENT_ENDPOINT, params)
        dt = datetime.fromtimestamp(data["dt"])

        return CurrentWeather(
            city=city,
            temp=round(data["main"]["temp"], 1),
            description=data["weather"][0]["description"],
            date=dt.strftime("%d/%m"),
        )

    def get_five_day_daily_forecast(
        self,
        city: str,
        country: str = "BR",
        state: str | None = None,
    ) -> List[DailyForecast]:
        lat, lon = self._get_coordinates(city, country, state)
        params = {
            "lat": lat,
            "lon": lon,
            "units": UNITS,
            "lang": LANG,
        }
        data = self._make_request(BASE_URL, FORECAST_ENDPOINT, params)

        daily_temps: Dict[date, List[float]] = {}
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
