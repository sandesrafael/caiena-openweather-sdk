import responses
from openweather_sdk import OpenWeatherSDK, CityNotFoundError

@responses.activate
def test_get_current_success(sdk):
    responses.add(
        responses.GET,
        "https://api.openweathermap.org/data/2.5/weather",
        json={
            "main": {"temp": 28.5},
            "weather": [{"description": "nublado"}],
            "dt": 1735689600
        },
        status=200
    )
    result = sdk.get_current("Rio de Janeiro")
    assert result.temp == 28.5
    assert result.description == "nublado"

@responses.activate
def test_city_not_found(sdk):
    responses.add(responses.GET, "https://api.openweathermap.org/data/2.5/weather", status=404)
    with pytest.raises(CityNotFoundError):
        sdk.get_current("CidadeInexistente")