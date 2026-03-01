import pytest
import responses

@pytest.fixture
def sdk():
    return OpenWeatherSDK("test-key")