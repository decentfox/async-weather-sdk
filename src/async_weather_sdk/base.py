import logging
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import asyncio
from aiohttp import web


class BaseClient(object):
    endpoint = None

    def __init__(
        self,
        endpoint: str,
        session: Optional[aiohttp.ClientSession] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Implement client that performs weather API requests.

        :param endpoint: The base endpoint URL
        :param session: Optionally specify the aiohttp session
        :param logger: An optional logger
        """
        self.endpoint = endpoint or self.endpoint
        self.logger = logger or logging.getLogger(__name__)
        self.session = session

    def _get_url(self, url):
        if self.endpoint and not url.startswith(("http://", "https://")):
            return urljoin(self.endpoint, url)
        return url

    async def request(
        self, url: str, method: Optional[str] = "GET", **aio_kwargs
    ):
        self.logger.debug("Fetch data from %s, %s", url, aio_kwargs)
        req_url = self._get_url(url)
        session = self.session or aiohttp.ClientSession(raise_for_status=True)
        try:
            async with session.request(method, req_url, **aio_kwargs) as resp:
                if "json" in resp.headers.get("CONTENT-TYPE"):
                    res = await resp.json()
                else:
                    res = await resp.text()
                self.logger.debug("Data fetched %r", res)
                return res
        except asyncio.TimeoutError:
            raise web.HTTPBadRequest(reason="HTTP Request Timeout")
        except (
            aiohttp.ClientResponseError,
            aiohttp.ClientConnectionError,
        ) as e:
            self.logger.warning("Error when getting %s, %s", url, e)
            raise e
        finally:
            if not self.session and not session.closed:
                await session.close()
