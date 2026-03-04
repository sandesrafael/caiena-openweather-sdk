from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentWeather:
    city: str
    state: str | None
    temp: float
    description: str
    date: str  # DD/MM

@dataclass(frozen=True)
class DailyForecast:
    date: str      # DD/MM
    avg_temp: float