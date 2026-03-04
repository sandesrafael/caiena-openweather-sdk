# caiena-openweather-sdk

SDK Python para consumo da API OpenWeatherMap:
- clima atual
- media diaria da previsao para os proximos 5 dias

## Pre-requisitos

1. `uv` instalado
2. Python 3.10+
3. Chave de API do OpenWeatherMap

## Setup inicial (local)

```bash
# 1. Criar ambiente virtual com uv
uv venv

# 2. Instalar SDK em modo editavel + dependencias de teste
uv pip install -e ".[test]"
```

## Configuracao da chave

Para teste local, coloque a chave em um arquivo `.env` na raiz do SDK:

```env
OPENWEATHER_API_KEY=sua_chave_aqui
```

## Como testar localmente com `example.py`

```bash
# Instalar dependencias do exemplo
uv pip install -e ".[example]"

# Rodar o exemplo
uv run --active python example.py
```

O exemplo executa:
- `get_current("Rio de Janeiro", "BR")`
- `get_five_day_daily_forecast("Rio de Janeiro", "BR")`

O script tenta carregar `OPENWEATHER_API_KEY` do `.env` automaticamente.

## Como rodar os testes

```bash
uv run --active pytest
```

Use `--active` para o `uv` reaproveitar o ambiente virtual ja ativo


## Modelos retornados

- `CurrentWeather(city, state, temp, description, date)`
- `DailyForecast(date, avg_temp)`

## Excecoes

- `CityNotFoundError`
- `InvalidAPIKeyError`
- `RateLimitError`
- `APIError`
