import pytest
from openweather_sdk import OpenWeatherSDK

@pytest.fixture
def sdk():
    return OpenWeatherSDK("test-key")
