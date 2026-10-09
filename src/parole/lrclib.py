import asyncio
import time

import httpx

rate_limit_timeout: int = 0
endpoint = "https://lrclib.net"


async def get(url: str, params: httpx.ParamsType = None) -> httpx.Response:
    global rate_limit_timeout

    if int(time.time()) < rate_limit_timeout:
        await asyncio.sleep(int(time.time()) - rate_limit_timeout)

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    # Handle rate limit
    if r.status_code == 429:
        rate_limit_timeout = int(time.time()) + int(r.headers["Retry-After"])
        r = await get(url, params)

    return r


async def get_lyrics(artist: str, title: str, album: str | None = None):
    if album != None:
        parameters = {"track_name": title, "artist_name": artist, "album_name": album}
    else:
        parameters = {"track_name": title, "artist_name": artist}

    response = await get(endpoint + "/api/get", params=parameters)
    return response.json()
