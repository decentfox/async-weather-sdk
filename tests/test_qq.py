import sys

import asyncio
import aiohttp
import pytest

from async_weather_sdk.qq import query_current_weather, query_weather_forecast
from async_weather_sdk.qq import QQMap, QQWeather

pytestmark = pytest.mark.asyncio


async def test_query_current_weather(aresponses, qq_forecast_resp):
    with pytest.raises(ValueError, match="Please provide tencent map api key"):
        await query_current_weather("", "北京")

    with pytest.raises(ValueError, match="Empty query"):
        await query_current_weather("API_KEY", "")

    aresponses.add(
        "apis.map.qq.com",
        "/ws/location/v1/ip",
        "GET",
        response={
            "status": 0,
            "message": "query ok",
            "result": {
                "ip": "61.135.17.68",
                "location": {"lat": 39.90469, "lng": 116.40717},
                "ad_info": {
                    "nation": "中国",
                    "province": "北京市",
                    "city": "北京市",
                    "district": "",
                    "adcode": 110000,
                },
            },
        },
    )
    aresponses.add(
        "wis.qq.com", "/weather/common", "GET", response=qq_forecast_resp,
    )

    res = await query_current_weather("API_KEY", "61.135.17.68")
    assert "observe" in res
    assert res["observe"] == {
        "degree": "29",
        "humidity": "30",
        "precipitation": "0.0",
        "pressure": "998",
        "update_time": "202006011323",
        "weather": "晴",
        "weather_code": "00",
        "weather_short": "晴",
        "wind_direction": "5",
        "wind_power": "2",
    }
    assert res["rise"] == {
        "sunrise": "04:47",
        "sunset": "19:36",
        "time": "20200601",
    }
    assert res["location"] == {
        "nation": "中国",
        "province": "北京市",
        "city": "北京市",
        "district": "",
        "adcode": 110000,
    }


async def test_query_weather_forecast(aresponses, qq_forecast_resp):
    with pytest.raises(ValueError, match="Please provide tencent map api key"):
        await query_weather_forecast("", "北京")

    with pytest.raises(ValueError, match="Empty query"):
        await query_weather_forecast("API_KEY", "")

    with pytest.raises(ValueError, match="Invalid forecast days"):
        await query_weather_forecast("API_KEY", "北京", 10)

    aresponses.add(
        "apis.map.qq.com",
        "/ws/location/v1/ip",
        "GET",
        response={
            "status": 0,
            "message": "query ok",
            "result": {
                "ip": "61.135.17.68",
                "location": {"lat": 39.90469, "lng": 116.40717},
                "ad_info": {
                    "nation": "中国",
                    "province": "北京市",
                    "city": "北京市",
                    "district": "",
                    "adcode": 110000,
                },
            },
        },
    )
    aresponses.add(
        "wis.qq.com", "/weather/common", "GET", response=qq_forecast_resp,
    )

    res = await query_weather_forecast("API_KEY", "61.135.17.68", 2)
    assert res == {
        "rise": [
            {"sunrise": "04:47", "sunset": "19:36", "time": "20200601"},
            {"sunrise": "04:47", "sunset": "19:37", "time": "20200602"},
        ],
        "forecast": [
            {
                "day_weather": "小雨",
                "day_weather_code": "07",
                "day_weather_short": "小雨",
                "day_wind_direction": "西北风",
                "day_wind_direction_code": "7",
                "day_wind_power": "4",
                "day_wind_power_code": "1",
                "max_degree": "26",
                "min_degree": "14",
                "night_weather": "晴",
                "night_weather_code": "00",
                "night_weather_short": "晴",
                "night_wind_direction": "西风",
                "night_wind_direction_code": "6",
                "night_wind_power": "3",
                "night_wind_power_code": "0",
                "time": "2020-05-31",
            },
            {
                "day_weather": "雷阵雨",
                "day_weather_code": "04",
                "day_weather_short": "雷阵雨",
                "day_wind_direction": "西南风",
                "day_wind_direction_code": "5",
                "day_wind_power": "5",
                "day_wind_power_code": "2",
                "max_degree": "30",
                "min_degree": "16",
                "night_weather": "多云",
                "night_weather_code": "01",
                "night_weather_short": "多云",
                "night_wind_direction": "西南风",
                "night_wind_direction_code": "5",
                "night_wind_power": "3",
                "night_wind_power_code": "0",
                "time": "2020-06-01",
            },
            {
                "day_weather": "晴",
                "day_weather_code": "00",
                "day_weather_short": "晴",
                "day_wind_direction": "南风",
                "day_wind_direction_code": "4",
                "day_wind_power": "5",
                "day_wind_power_code": "2",
                "max_degree": "33",
                "min_degree": "20",
                "night_weather": "晴",
                "night_weather_code": "00",
                "night_weather_short": "晴",
                "night_wind_direction": "西南风",
                "night_wind_direction_code": "5",
                "night_wind_power": "4",
                "night_wind_power_code": "1",
                "time": "2020-06-02",
            },
        ],
        "location": {
            "nation": "中国",
            "province": "北京市",
            "city": "北京市",
            "district": "",
            "adcode": 110000,
        },
    }


async def test_qq_weather_sdk_fetch_weather(aresponses):
    aresponses.add(
        "wis.qq.com",
        "/weather/common",
        "GET",
        response={
            "message": "OK",
            "status": 200,
            "data": {
                "observe": {
                    "degree": "29",
                    "humidity": "30",
                    "precipitation": "0.0",
                    "pressure": "998",
                    "update_time": "202006011323",
                    "weather": "晴",
                    "weather_code": "00",
                    "weather_short": "晴",
                    "wind_direction": "5",
                    "wind_power": "2",
                },
            },
        },
    )

    async with aiohttp.ClientSession() as session:
        qq_weather = QQWeather(session=session)

        res = await qq_weather.fetch_weather("北京", "北京", "observe")
        assert "observe" in res

    aresponses.add(
        "wis.qq.com",
        "/weather/common",
        "GET",
        response={"status": 311, "message": "key格式错误"},
    )

    async with aiohttp.ClientSession() as session:
        qq_weather = QQWeather(session=session)

        res = await qq_weather.fetch_weather("北京", "北京", "observe")
        assert res == {}


async def test_qq_weather_sdk_fetch_current_weather(
    aresponses, qq_forecast_resp
):
    aresponses.add(
        "wis.qq.com", "/weather/common", "GET", response=qq_forecast_resp,
    )
    async with aiohttp.ClientSession() as session:
        qq_weather = QQWeather(session=session)
        res = await qq_weather.fetch_current_weather("北京", "北京")
        assert "observe" in res
        assert "sunrise" in res["rise"]


async def test_qq_weather_sdk_fetch_weather_forecast(
    aresponses, qq_forecast_resp
):
    aresponses.add(
        "wis.qq.com", "/weather/common", "GET", response=qq_forecast_resp,
    )

    async with aiohttp.ClientSession() as session:
        qq_weather = QQWeather(session=session)
        res = await qq_weather.fetch_weather_forecast("北京", "北京", 3)

        assert "forecast" in res
        assert len(res["forecast"]) == 4

        assert "rise" in res
        assert len(res["rise"]) == 3

    aresponses.add(
        "wis.qq.com", "/weather/common", "GET", response=qq_forecast_resp,
    )

    async with aiohttp.ClientSession() as session:
        qq_weather = QQWeather(session=session)
        res = await qq_weather.fetch_weather_forecast("北京", "北京", 1)

        assert "forecast" in res
        assert len(res["forecast"]) == 25

        assert "rise" in res
        assert len(res["rise"]) == 1


async def test_qq_map_wrong_api_key(aresponses):
    aresponses.add(
        "apis.map.qq.com",
        "/ws/location/v1/ip",
        "GET",
        response={"status": 311, "message": "key格式错误"},
    )

    async with aiohttp.ClientSession() as session:
        qq_map = QQMap("API_KEY", session=session)
        res = await qq_map.location_lookup_by_ip("61.135.17.68")
        assert res == {}


async def test_qq_map_location_lookup_by_ip(aresponses):
    aresponses.add(
        "apis.map.qq.com",
        "/ws/location/v1/ip",
        "GET",
        response={
            "status": 0,
            "message": "query ok",
            "result": {
                "ip": "61.135.17.68",
                "location": {"lat": 39.90469, "lng": 116.40717},
                "ad_info": {
                    "nation": "中国",
                    "province": "北京市",
                    "city": "北京市",
                    "district": "",
                    "adcode": 110000,
                },
            },
        },
    )
    async with aiohttp.ClientSession() as session:
        qq_map = QQMap("API_KEY", session=session)

        res = await qq_map.location_lookup_by_ip("61.135.17.68")
        assert res == {
            "nation": "中国",
            "province": "北京市",
            "city": "北京市",
            "district": "",
            "adcode": 110000,
        }


async def test_qq_map_location_lookup_by_coordinates(aresponses):
    aresponses.add(
        "apis.map.qq.com",
        "/ws/geocoder/v1",
        "GET",
        response={
            "status": 0,
            "message": "query ok",
            "result": {
                "location": {"lat": 39.90469, "lng": 116.40717},
                "address": "北京市东城区正义路2号",
                "ad_info": {
                    "nation_code": "156",
                    "adcode": "110101",
                    "city_code": "156110000",
                    "name": "中国,北京市,北京市,东城区",
                    "location": {"lat": 39.916668, "lng": 116.434578},
                    "nation": "中国",
                    "province": "北京市",
                    "city": "北京市",
                    "district": "东城区",
                },
            },
        },
    )
    async with aiohttp.ClientSession() as session:
        qq_map = QQMap("API_KEY", session=session)

        res = await qq_map.location_lookup_by_coordinates("39.90469,116.40717")
        assert res == {
            "nation_code": "156",
            "adcode": "110101",
            "city_code": "156110000",
            "name": "中国,北京市,北京市,东城区",
            "location": {"lat": 39.916668, "lng": 116.434578},
            "nation": "中国",
            "province": "北京市",
            "city": "北京市",
            "district": "东城区",
        }

    aresponses.add(
        "apis.map.qq.com",
        "/ws/geocoder/v1",
        "GET",
        response={"status": 400, "message": "query failed",},
    )
    async with aiohttp.ClientSession() as session:
        qq_map = QQMap("API_KEY", session=session)

        res = await qq_map.location_lookup_by_coordinates("39.90469,116.40717")
        assert res == {}


async def test_qq_map_location_lookup_by_keyword(aresponses):
    aresponses.add(
        "apis.map.qq.com",
        "/ws/district/v1/search",
        "GET",
        response={
            "status": 0,
            "message": "query ok",
            "result": [
                [
                    {
                        "id": "110000",
                        "name": "北京",
                        "fullname": "北京市",
                        "pinyin": ["bei", "jing"],
                        "level": 1,
                        "location": {"lat": 39.90469, "lng": 116.40717},
                        "address": "北京",
                    },
                    {
                        "id": "230225580",
                        "fullname": "北京市双河农场",
                        "level": 4,
                        "location": {"lat": 47.866631, "lng": 123.753351},
                        "address": "黑龙江,齐齐哈尔,甘南县,北京市双河农场",
                    },
                ]
            ],
        },
    )
    aresponses.add(
        "apis.map.qq.com",
        "/ws/geocoder/v1",
        "GET",
        response={
            "status": 0,
            "message": "query ok",
            "result": {
                "location": {"lat": 39.90469, "lng": 116.40717},
                "address": "北京市东城区正义路2号",
                "ad_info": {
                    "nation_code": "156",
                    "adcode": "110101",
                    "city_code": "156110000",
                    "name": "中国,北京市,北京市,东城区",
                    "location": {"lat": 39.916668, "lng": 116.434578},
                    "nation": "中国",
                    "province": "北京市",
                    "city": "北京市",
                    "district": "东城区",
                },
            },
        },
    )
    async with aiohttp.ClientSession() as session:
        qq_map = QQMap("API_KEY", session=session)

        res = await qq_map.location_lookup_by_keyword("北京市")
        assert res == {
            "nation_code": "156",
            "adcode": "110101",
            "city_code": "156110000",
            "name": "中国,北京市,北京市,东城区",
            "location": {"lat": 39.916668, "lng": 116.434578},
            "nation": "中国",
            "province": "北京市",
            "city": "北京市",
            "district": "东城区",
        }

    aresponses.add(
        "apis.map.qq.com",
        "/ws/district/v1/search",
        "GET",
        response={"status": 0, "message": "query ok", "result": [],},
    )
    async with aiohttp.ClientSession() as session:
        qq_map = QQMap("API_KEY", session=session)

        res = await qq_map.location_lookup_by_keyword("北京市")
        assert res == {}

    aresponses.add(
        "apis.map.qq.com",
        "/ws/district/v1/search",
        "GET",
        response={"status": 400, "message": "query failed",},
    )
    async with aiohttp.ClientSession() as session:
        qq_map = QQMap("API_KEY", session=session)

        res = await qq_map.location_lookup_by_keyword("北京市")
        assert res == {}


@pytest.fixture()
def mock_location_lookup_by_ip(mocker):
    future = asyncio.Future()
    mocker.patch(
        "async_weather_sdk.qq.QQMap.location_lookup_by_ip", return_value=future
    )
    future.set_result("mock_location_lookup_by_ip")
    return future


@pytest.fixture()
def mock_location_lookup_by_coordinates(mocker):
    future = asyncio.Future()
    mocker.patch(
        "async_weather_sdk.qq.QQMap.location_lookup_by_coordinates",
        return_value=future,
    )
    future.set_result("location_lookup_by_coordinates")
    return future


@pytest.fixture()
def mock_location_lookup_by_keyword(mocker):
    future = asyncio.Future()
    mocker.patch(
        "async_weather_sdk.qq.QQMap.location_lookup_by_keyword",
        return_value=future,
    )
    future.set_result("location_lookup_by_keyword")
    return future


async def test_qq_map_location_lookup(
    mock_location_lookup_by_ip,
    mock_location_lookup_by_coordinates,
    mock_location_lookup_by_keyword,
):
    if sys.version_info >= (3, 8):
        return

    qq_map = QQMap("API_KEY")
    res = await qq_map.location_lookup("61.135.17.68")
    assert res == "mock_location_lookup_by_ip"

    res = await qq_map.location_lookup("39.90469,116.40717")
    assert res == "location_lookup_by_coordinates"

    res = await qq_map.location_lookup("北京市")
    assert res == "location_lookup_by_keyword"


async def test_qq_map_location_lookup_p38(mocker):
    if sys.version_info < (3, 8):
        return

    mocker.patch("async_weather_sdk.qq.QQMap.location_lookup_by_ip")
    mocker.patch("async_weather_sdk.qq.QQMap.location_lookup_by_coordinates")
    mocker.patch("async_weather_sdk.qq.QQMap.location_lookup_by_keyword")

    qq_map = QQMap("API_KEY")
    await qq_map.location_lookup("61.135.17.68")
    QQMap.location_lookup_by_ip.assert_called_once()

    await qq_map.location_lookup("39.90469,116.40717")
    QQMap.location_lookup_by_coordinates.assert_called_once()

    await qq_map.location_lookup("北京市")
    QQMap.location_lookup_by_keyword.assert_called_once()
