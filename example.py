from dotenv import load_dotenv
import os
from openweather_sdk import OpenWeatherSDK, CityNotFoundError

# Carrega as variáveis do .env
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    print("❌ Coloque sua chave no arquivo .env antes de rodar!")
    exit(1)

sdk = OpenWeatherSDK(api_key=API_KEY)

try:
    print("🌡️  Buscando dados...")
    
    current = sdk.get_current("Rio de Janeiro,BR")
    forecast = sdk.get_five_day_daily_forecast("Rio de Janeiro,BR")
    
    print(f"\n✅ Temperatura atual em {current.city}:")
    print(f"   {current.temp}°C - {current.description} ({current.date})")
    
    print("\n📅 Previsão média dos próximos 5 dias:")
    for day in forecast:
        print(f"   {day.date}: {day.avg_temp}°C")

except CityNotFoundError:
    print("❌ Cidade não encontrada")
except Exception as e:
    print(f"❌ Erro: {e}")