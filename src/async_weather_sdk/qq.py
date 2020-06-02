import re
import logging
from typing import Optional

import aiohttp

from .base import BaseClient

WEATHER_ENDPOINT = "https://wis.qq.com"
MAP_ENDPOINT = "https://apis.map.qq.com"

qq_logger = logging.getLogger(__name__)


class QQWeather(BaseClient):
    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Implement QQ Weather client that performs QQ weather API requests.

        :param session: Optionally specify the aiohttp session
        :param logger: An optional logger
        """
        super().__init__(
            endpoint=WEATHER_ENDPOINT, session=session, logger=logger
        )

    async def fetch_weather(self, province: str, city: str, weather_type: str):
        """
        Fetch weather data from Tencent (QQ) Weather API.

        :param province: Province Name in Chinese, for example: 北京市
        :param city: City Name in Chinese, for example: 北京市
        :param weather_type: Available types:
            observe|forecast_1h|forecast_24h|index|alarm|limit|tips|rise|air

            observe - Return real-time weather.
            forecast_1h - Return weather forecast data split hourly
                          in next 24 hours.
            forecast_24h - Return weather forecast data split daily
                           in next 7 days.
            index - Return today's index data of living.
            alarm - Return real-time weather alarm data.
            limit - Return today's car limit data.
            tips - Return today's weather tips data.
            rise - Return sunrise and sunset data.
            air - Return real-time air quality data.
        :return: Weather API response data.
        """
        params = dict(
            source="pc",
            weather_type=weather_type or "",
            province=province or "",
            city=city or "",
        )
        res = await self.request("/weather/common", params=params)
        if res.get("status") == 200 and res.get("message") == "OK":
            return res["data"]
        return {}

    async def fetch_current_weather(self, province: str, city: str) -> dict:
        """
        Return current weather data.

        :param province: Province Name in Chinese, for example: 北京市
        :param city: City Name in Chinese, for example: 北京市
        :return: real-time weather data.
        """
        res = await self.fetch_weather(
            province, city, "observe|index|alarm|limit|tips|rise|air"
        )
        res.update(rise=res.get("rise", {}).get("0", {}),)
        return res

    async def fetch_weather_forecast(
        self, province: str, city: str, forecast_days: int = 7
    ) -> dict:
        """
        Return weather forecast data for up to 7 days into the future.

        :param province: Province Name in Chinese, for example: 北京市
        :param city: City Name in Chinese, for example: 北京市
        :param forecast_days: The number of days for which the API returns
                              forecast data (Default: 7 days).
                              If pass forecast_days is 1, it will return
                              weather data split hourly.
        :return: forecast weather data.
        """
        forecast_days = min((max(1, forecast_days), 7))
        weather_type = "forecast_24h|rise"
        if forecast_days == 1:
            weather_type = "forecast_1h|rise"
        res = await self.fetch_weather(province, city, weather_type)
        if forecast_days == 1:
            weather_data = sorted(
                res.get("forecast_1h", {}).values(),
                key=lambda item: item["update_time"],
            )
        else:
            weather_data = sorted(
                res.get("forecast_24h", {}).values(),
                key=lambda item: item["time"],
            )
        if forecast_days > 1:
            weather_data = weather_data[: forecast_days + 1]
        else:
            weather_data = weather_data[:25]

        rise_data = sorted(
            res.get("rise", {}).values(), key=lambda item: item["time"]
        )
        return dict(forecast=weather_data, rise=rise_data[:forecast_days],)


class QQMap(BaseClient):
    api_key = None

    def __init__(
        self,
        api_key: str,
        session: Optional[aiohttp.ClientSession] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Implement QQ Map client that performs QQ Map API requests.

        :param api_key: QQ Map WebService API key
        :param session: Optionally specify the aiohttp session
        :param logger: An optional logger
        """
        self.api_key = api_key
        super().__init__(endpoint=MAP_ENDPOINT, session=session, logger=logger)

    async def location_lookup_by_ip(self, ip: str):
        params = dict(ip=ip, key=self.api_key)
        res = await self.request("/ws/location/v1/ip", params=params)
        if res.get("status") != 0:
            self.logger.warning("Failed to query location by IP %r", res)
        result = res.get("result", {})
        return result.get("ad_info", {})

    async def location_lookup_by_coordinates(self, coordinates: str):
        params = dict(location=coordinates, key=self.api_key)
        res = await self.request("/ws/geocoder/v1", params=params)
        if res.get("status") != 0:
            self.logger.warning(
                "Failed to query location by coordinates %r", res
            )
        result = res.get("result", {})
        return result.get("ad_info", {})

    async def location_lookup_by_keyword(self, keyword: str):
        params = dict(keyword=keyword, key=self.api_key)
        res = await self.request("/ws/district/v1/search", params=params)
        if res.get("status") != 0:
            self.logger.warning("Failed to query location by keyword %r", res)
        results = res.get("result", [])
        if not results or not results[0]:
            return {}
        location = results[0][0]["location"]
        lat = location["lat"]
        lng = location["lng"]
        return await self.location_lookup_by_coordinates(f"{lat},{lng}")

    async def location_lookup(self, query: str):
        ad_info = None
        ip_candidates = re.findall(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", query
        )
        if ip_candidates:
            ad_info = await self.location_lookup_by_ip(ip_candidates[0])

        coordinates = re.findall(r"^(-?\d+\.\d+?),\s*(-?\d+\.\d+?)$", query)
        if coordinates:
            ad_info = await self.location_lookup_by_coordinates(
                ",".join(coordinates[0])
            )

        if not ad_info:
            ad_info = await self.location_lookup_by_keyword(query)

        return ad_info


async def query_current_weather(api_key: str, query: str):
    """
    To query the QQ (Tencent) Weather API for real-time weather data in a
    location of your choice.

    :param api_key: Tencent Map WebServiceAPI key.
    :param query: Pass a single location identifier to the API and
                  auto-detect the associated location. For Example:
        北京市 - Location Name
        110105 - adcode (行政区划代码)
        39.90469,116.40717 - Coordinates (Lat/Lon)
        61.135.17.68 - IP Address.
    :return: real-time weather data.
    """
    if not api_key:
        raise ValueError("Please provide tencent map api key")

    if not query:
        raise ValueError("Empty query")

    async with aiohttp.ClientSession() as session:
        qq_map = QQMap(api_key, session=session, logger=qq_logger)
        qq_weather = QQWeather(session=session, logger=qq_logger)
        ad_info = await qq_map.location_lookup(query)
        province, city = ad_info.get("province"), ad_info.get("city")

        res = await qq_weather.fetch_current_weather(province, city)
        res.update(location=ad_info)
        return res


async def query_weather_forecast(
    api_key: str, query: str, forecast_days: int = 7
):
    """
    The QQ (Tencent) Weather API is capable of returning weather forecast data
    for up to 7 days into the future.

    :param api_key: Tencent Map WebServiceAPI key.
    :param query: Pass a single location identifier to the API and
                  auto-detect the associated location. For Example:
        北京市 - Location Name
        110105 - adcode (行政区划代码)
        39.90469,116.40717 - Coordinates (Lat/Lon)
        61.135.17.68 - IP Address.
    :param forecast_days: The number of days for which the API returns forecast
                          data (Default: 7 days).
                          If pass forecast_days is 1, it will return weather
                          data split hourly.
    :return: forecast weather data.
    """
    if not api_key:
        raise ValueError("Please provide tencent map api key")

    if not query:
        raise ValueError("Empty query")

    if forecast_days > 7 or forecast_days < 0:
        raise ValueError("Invalid forecast days")

    async with aiohttp.ClientSession() as session:
        qq_map = QQMap(api_key, session=session, logger=qq_logger)
        qq_weather = QQWeather(session=session, logger=qq_logger)
        ad_info = await qq_map.location_lookup(query)
        province, city = ad_info.get("province"), ad_info.get("city")

        res = await qq_weather.fetch_weather_forecast(
            province, city, forecast_days
        )
        res.update(location=ad_info)
        return res
