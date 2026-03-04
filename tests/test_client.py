from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from openweather_sdk import CityNotFoundError


def _mock_response(status_code: int, payload, text: str = "") -> Mock:
    response = Mock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = payload
    return response


def test_get_current_success(sdk):
    geo_response = _mock_response(
        200,
        [{"name": "Rio de Janeiro", "country": "BR", "lat": -22.9068, "lon": -43.1729}],
    )
    current_response = _mock_response(
        200,
        {
            "main": {"temp": 28.5},
            "weather": [{"description": "nublado"}],
            "dt": 1735689600,
        },
    )

    with patch.object(sdk.session, "get", side_effect=[geo_response, current_response]) as get_mock:
        result = sdk.get_current("Rio de Janeiro")

    assert result.city == "Rio de Janeiro"
    assert result.state is None
    assert result.temp == 28.5
    assert result.description == "nublado"
    assert get_mock.call_count == 2


def test_get_current_uses_state_in_geocoding_query(sdk):
    geo_response = _mock_response(
        200,
        [{"name": "Springfield", "state": "Illinois", "country": "US", "lat": 39.8, "lon": -89.64}],
    )
    current_response = _mock_response(
        200,
        {
            "main": {"temp": 14.0},
            "weather": [{"description": "clear sky"}],
            "dt": 1735689600,
        },
    )

    with patch.object(sdk.session, "get", side_effect=[geo_response, current_response]) as get_mock:
        result = sdk.get_current("Springfield", "US", "Illinois")

    first_call_params = get_mock.call_args_list[0].kwargs["params"]
    assert first_call_params["q"] == "Springfield,Illinois,US"
    assert result.state == "Illinois"


def test_city_not_found_includes_city_and_country_in_message(sdk):
    geo_response = _mock_response(200, [])

    with patch.object(sdk.session, "get", return_value=geo_response):
        with pytest.raises(CityNotFoundError, match="Rio de Janeiro.*US"):
            sdk.get_current("Rio de Janeiro", "US")


def test_city_not_found_includes_state_in_message(sdk):
    geo_response = _mock_response(200, [])

    with patch.object(sdk.session, "get", return_value=geo_response):
        with pytest.raises(CityNotFoundError, match="Osasco.*JP.*Tokyo"):
            sdk.get_current("Osasco", "JP", "Tokyo")


def test_city_not_found_when_geocoding_returns_mismatched_name(sdk):
    geo_response = _mock_response(
        200,
        [{"name": "City of Syracuse", "state": "New York", "country": "US", "lat": 43.0, "lon": -76.1}],
    )

    with patch.object(sdk.session, "get", return_value=geo_response):
        with pytest.raises(CityNotFoundError, match="us.*US"):
            sdk.get_current("us", "US", "US")


def test_get_five_day_daily_forecast_averages_by_day(sdk):
    now = datetime.now()
    day_one = now + timedelta(days=1)
    day_two = now + timedelta(days=2)

    geo_response = _mock_response(
        200,
        [{"name": "Rio de Janeiro", "country": "BR", "lat": -22.9068, "lon": -43.1729}],
    )
    forecast_response = _mock_response(
        200,
        {
            "list": [
                {"dt": int((day_one.replace(hour=9, minute=0, second=0, microsecond=0)).timestamp()), "main": {"temp": 20.0}},
                {"dt": int((day_one.replace(hour=15, minute=0, second=0, microsecond=0)).timestamp()), "main": {"temp": 24.0}},
                {"dt": int((day_two.replace(hour=9, minute=0, second=0, microsecond=0)).timestamp()), "main": {"temp": 18.0}},
                {"dt": int((day_two.replace(hour=15, minute=0, second=0, microsecond=0)).timestamp()), "main": {"temp": 22.0}},
            ]
        },
    )

    with patch.object(sdk.session, "get", side_effect=[geo_response, forecast_response]):
        result = sdk.get_five_day_daily_forecast("Rio de Janeiro")

    expected = {
        day_one.strftime("%d/%m"): 22.0,
        day_two.strftime("%d/%m"): 20.0,
    }
    assert len(result) == 2
    assert {item.date: item.avg_temp for item in result} == expected
