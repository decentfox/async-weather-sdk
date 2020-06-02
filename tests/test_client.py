import aiohttp
import asyncio
import pytest
from aiohttp import web

from async_weather_sdk.base import BaseClient

pytestmark = pytest.mark.asyncio


async def test_client_instantiation():
    client = BaseClient("https://BASE_ENDPOINT/")

    assert client.session is None

    async with aiohttp.ClientSession() as session:
        client = BaseClient("https://BASE_ENDPOINT/", session=session)
        assert client.session is not None

        with pytest.raises(aiohttp.ClientConnectionError):
            await client.request("/API_ENDPOINT")

        assert not session.closed


def test_client_get_url():
    fake_client = BaseClient("https://BASE_ENDPOINT/")

    assert (
        fake_client._get_url("/API_ENDPOINT")
        == "https://BASE_ENDPOINT/API_ENDPOINT"
    )

    assert (
        fake_client._get_url("https://API_ENDPOINT") == "https://API_ENDPOINT"
    )


async def test_request_with_error_response(aresponses):
    aresponses.add(
        "BASE_ENDPOINT",
        "/v1",
        "GET",
        response=aresponses.Response(status=500, text="error"),
    )

    async with aiohttp.ClientSession() as session:
        client = BaseClient("https://BASE_ENDPOINT/", session=session)

        res = await client.request("/v1")
        assert res == "error"


async def test_request_with_success_response(aresponses):
    aresponses.add(
        "BASE_ENDPOINT",
        "/v1",
        "GET",
        response=aresponses.Response(
            status=200,
            text='{"status": 200}',
            headers={"CONTENT-TYPE": "application/json"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = BaseClient("https://BASE_ENDPOINT/", session=session)

        res = await client.request("/v1")
        assert res == {"status": 200}


async def test_request_with_timeout(aresponses):
    async def response_handler(request):
        await asyncio.sleep(1)
        return aresponses.Response(text="ok")

    aresponses.add("BASE_ENDPOINT", "/v1", "GET", response_handler)
    with pytest.raises(web.HTTPBadRequest, match="HTTP Request Timeout"):
        async with aiohttp.ClientSession() as session:
            client = BaseClient("https://BASE_ENDPOINT/", session=session)

            await client.request("/v1", timeout=0.05)


async def test_session_closed_after_request(aresponses):
    aresponses.add(
        "BASE_ENDPOINT",
        "/v1",
        "GET",
        response=aresponses.Response(
            status=200,
            text='{"status": 200}',
            headers={"CONTENT-TYPE": "application/json"},
        ),
    )

    client = BaseClient("https://BASE_ENDPOINT/")
    assert client.session is None
    await client.request("/v1")
