from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class CurrentWeather:
    city: str
    temp: float
    description: str
    date: str  # DD/MM

@dataclass(frozen=True)
class DailyForecast:
    date: str      # DD/MM
    avg_temp: float