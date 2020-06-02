# Async Weather SDK

[![PyPI version](https://img.shields.io/pypi/v/async-weather-sdk?logo=python&logoColor=white)](https://badge.fury.io/py/async-weather-sdk)
[![GitHub Workflow Status for tests](https://img.shields.io/github/workflow/status/decentfox/async-weather-sdk/test?logo=github&logoColor=white)](https://github.com/decentfox/async-weather-sdk/actions?query=workflow%3Atest)
[![Codacy Badge](https://img.shields.io/codacy/coverage/f548667427c24fc394204b440166c26d?logo=Codacy)](https://www.codacy.com/gh/decentfox/async-weather-sdk?utm_source=github.com&utm_medium=referral&utm_content=decentfox/async-weather-sdk&utm_campaign=Badge_Coverage)

Async weather API wrapper for fetching weather and forecast data

## Core Dependencies

**Asyncio:** a library to write concurrent code using the async/await syntax.

**Aiohttp:** an asynchronous HTTP Client/Server for asyncio and Python.

## Install

```bash
pip install async-weather-sdk

OR

poetry add async-weather-sdk
```

## Usage

### QQ Weather API SDK

Get current weather/forecast data by province and city.

```python
from async_weather_sdk.qq import QQWeather

weather = QQWeather()

await weather.fetch_current_weather('北京市', '北京市')
await weather.fetch_weather_forecast('北京市', '北京市', 3)
```

Query current weather/forecast data with tencent map api key.

```python
from async_weather_sdk.qq import query_current_weather, query_weather_forecast

await query_current_weather('API_KEY', '北京市')
await query_weather_forecast('API_KEY', '39.90469,116.40717')
```
