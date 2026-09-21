import asyncio
import subprocess
from array import array

import lrclib
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Label

current_lyrics: array | None
current_position: int
trackid: str | None = None


async def get_lyrics(title, artist, album: str | None = None):
    lyrics = await lrclib.get_lyrics(title=title, artist=artist, album=album)
    if "syncedLyrics" in lyrics:
        return {"lyrics": lyrics["syncedLyrics"], "synced": True}
    elif "plainLyrics" in lyrics:
        return {"lyrics": lyrics["plainLyrics"], "synced": False}
    else:
        return None


def get_metadata():
    run = (
        subprocess.run(
            ["playerctl", "status"], capture_output=True, text=True, check=False
        ).returncode
        == 0
    )
    if run:
        artist = subprocess.run(
            ["playerctl", "metadata", "artist"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        title = subprocess.run(
            ["playerctl", "metadata", "title"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        album = subprocess.run(
            ["playerctl", "metadata", "album"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        return [run, artist, title, album]
    else:
        return [run]


async def get_next_lyrics():
    global trackid
    trackid = None if not isinstance(trackid, str) else trackid
    metadata = get_metadata()
    if trackid == None or trackid != f"{metadata[1]}__{metadata[2]}":
        if metadata[0] == True:
            trackid = f"{metadata[1]}__{metadata[2]}"
            lyrics = await get_lyrics(metadata[2], metadata[1])
            current_lyrics = []
            for i in lyrics["lyrics"].splitlines():
                current_lyrics.append({"timestamp": i[1:9], "lyric": i[11:]})
            current_position = 0
            print(current_lyrics)

        else:
            trackid = None
            refresh = 3
            current_lyrics = None
            current_position = 0
            return [None, refresh]


class MyApp(App):
    CSS_PATH = "textual.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Loading lyrics...", id="loading-label")

    def on_mount(self) -> ComposeResult:
        self.init_lyrics()

    @work(exclusive=True)
    async def init_lyrics(self):
        global trackid
        metadata = get_metadata
        if metadata[0] == True:
            trackid = f"{metadata[1]}__{metadata[2]}"
        else:
            trackid = None


if __name__ == "__main__":
    print(asyncio.run(get_next_lyrics()))
    app = MyApp()
    app.run()
