import requests
from datetime import datetime
from typing import List, Dict, Tuple

from .config import *
from .exceptions import *
from .models import *


class OpenWeatherSDK:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def _make_request(self, base_url: str, endpoint: str, params: dict) -> dict:
        url = f"{base_url}{endpoint}"

        # Sempre adiciona API key
        params["appid"] = self.api_key

        response = self.session.get(url, params=params, timeout=10)

        if response.status_code == 404:
            raise CityNotFoundError("Cidade não encontrada")
        if response.status_code == 401:
            raise InvalidAPIKeyError("Chave de API inválida")
        if response.status_code == 429:
            raise RateLimitError("Limite de requisições excedido")
        if response.status_code != 200:
            raise APIError(f"Erro {response.status_code}: {response.text}")

        return response.json()

    def _get_coordinates(self, city: str, country: str = "BR") -> Tuple[float, float]:
        """Geocoding API oficial"""
        params = {"q": f"{city},{country}", "limit": 1}

        # 🔴 Geocoding usa base diferente
        data = self._make_request(GEO_BASE_URL, "/geo/1.0/direct", params)

        if not data:
            raise CityNotFoundError(f"Coordenadas não encontradas para {city}")

        return data[0]["lat"], data[0]["lon"]

    def get_current(self, city: str, country: str = "BR") -> CurrentWeather:
        lat, lon = self._get_coordinates(city, country)

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
            date=dt.strftime("%d/%m")
        )

    def get_five_day_daily_forecast(self, city: str, country: str = "BR") -> List[DailyForecast]:
        lat, lon = self._get_coordinates(city, country)

        params = {
            "lat": lat,
            "lon": lon,
            "units": UNITS,
            "lang": LANG,
        }

        data = self._make_request(BASE_URL, FORECAST_ENDPOINT, params)

        daily_temps: Dict[str, List[float]] = {}
        today = datetime.now().date()

        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.date()

            # Apenas próximos 5 dias (exclui hoje)
            if date_key <= today or (date_key - today).days > 5:
                continue

            date_str = dt.strftime("%d/%m")

            if date_str not in daily_temps:
                daily_temps[date_str] = []

            daily_temps[date_str].append(item["main"]["temp"])

        result = []
        for date_str in sorted(daily_temps.keys()):
            avg = round(sum(daily_temps[date_str]) / len(daily_temps[date_str]), 1)
            result.append(DailyForecast(date=date_str, avg_temp=avg))

        return result[:5]