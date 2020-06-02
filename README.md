# Async Weather SDK
[![PyPI version](https://badge.fury.io/py/async-weather-sdk.svg)](https://badge.fury.io/py/async-weather-sdk)

Async weather API wrapper for fetching weather and forecast data

## Core Dependencies
  * **Asyncio:** a library to write concurrent code using the async/await syntax.
  * **Aiohttp:** an asynchronous HTTP Client/Server for asyncio and Python.

## Usage
### QQ Weather API SDK

 1. Get current weather/forecast data by province and city.

```python
from async_weather_sdk.qq import QQWeather

weather = QQWeather()

await weather.fetch_current_weather('北京市', '北京市')
await weather.fetch_weather_forecast('北京市', '北京市', 3)
```

 2. Query current weather/forecast data with tencent map api key.

```python
from async_weather_sdk.qq import query_current_weather, query_weather_forecast

await query_current_weather('API_KEY', '北京市')
await query_weather_forecast('API_KEY', '39.90469,116.40717')
```
