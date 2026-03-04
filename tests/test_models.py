from dataclasses import FrozenInstanceError

import pytest

from openweather_sdk.models import CurrentWeather, DailyForecast


def test_current_weather_model():
    model = CurrentWeather(
        city="Rio de Janeiro",
        state="Rio de Janeiro",
        temp=28.5,
        description="nublado",
        date="01/03",
    )
    assert model.city == "Rio de Janeiro"
    assert model.state == "Rio de Janeiro"
    assert model.temp == 28.5


def test_daily_forecast_model():
    model = DailyForecast(date="02/03", avg_temp=24.7)
    assert model.date == "02/03"
    assert model.avg_temp == 24.7


def test_models_are_immutable():
    model = CurrentWeather(
        city="Sao Paulo",
        state="São Paulo",
        temp=26.0,
        description="ceu limpo",
        date="01/03",
    )
    with pytest.raises(FrozenInstanceError):
        model.temp = 30.0
