class OpenWeatherSDKError(Exception):
    """Exceção base do SDK."""

class CityNotFoundError(OpenWeatherSDKError):
    """Cidade não encontrada."""

class InvalidAPIKeyError(OpenWeatherSDKError):
    """Chave de API inválida ou expirada."""

class RateLimitError(OpenWeatherSDKError):
    """Limite de requisições excedido."""

class APIError(OpenWeatherSDKError):
    """Erro genérico da API."""