import asyncio
import re

import httpx

lrclred_endpoint = "https://lrc.red/"
musicbrainz_endpoint = "https://musicbrainz.org/ws/2/"


async def get(url: str, params: httpx.ParamsType = None) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url,
            params=params,
            headers={"User-Agent": "Parole/1.1.0 (skueee@outlook.com)"},
        )

    return r


async def get_isrc(artist: str, title: str, album: str | None = None):
    if album != None:
        query = f'recording:"{title}" AND artist:"{artist}" AND release:"{album}f"'
    else:
        query = f'recording:"{title}" AND artist:"{artist}"'

    params = {"query": query, "fmt": "json"}

    response = await get(f"{musicbrainz_endpoint}recording/", params)

    data = response.json()

    recordings = data.get("recordings", [])
    if not recordings:
        return None

    results = []
    for i in recordings:
        j = i.get("isrcs")
        if j is not None:
            results.extend(j)

    return results


def clean_lrc(input: str):
    cleaned_content = input

    word_sync_pattern = re.compile(r"<\d{2}[:\.]\d{2}[:\.]?\d*?>")
    matches = word_sync_pattern.findall(input)

    if len(matches) > 0:
        cleaned_content = word_sync_pattern.sub("", input)
        cleaned_content = re.sub(r"[ \t]+", " ", cleaned_content)

    metadata_pattern = re.compile(r"^\[([a-zA-Z]+):.*\]$")
    lines = cleaned_content.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if metadata_pattern.match(stripped):
            continue
        cleaned_lines.append(line)

    cleaned_content = "\n".join(cleaned_lines).lstrip("\n")

    return cleaned_content


async def get_lyrics(artist: str, title: str, album: str | None = None):
    isrcs = await get_isrc(artist, title, album)

    if isrcs == None:
        return None

    lyrics_url: str
    for i in isrcs:
        response = await get(f"{lrclred_endpoint}s/{i}.json")
        song_infos: dict = response.json()
        if "files" in song_infos and "lrc" in song_infos["files"]:
            lyrics_url = song_infos["files"]["lrc"]
            break
    if lyrics_url == "":
        return None

    response = await get(lyrics_url)
    lrc = response.text

    result = clean_lrc(lrc)

    return {"syncedLyrics": result}


if __name__ == "__main__":
    print(asyncio.run(get_lyrics("System Of A Down", "Sugar")))
