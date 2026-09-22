import asyncio
import subprocess
from array import array

import lrclib
import bisect
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Label

current_lyrics: array[str] | None
current_timestamps: array[float] | None
trackid: str | None = None
active: bool


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
        return [run, None, None, None]


async def check_if_new_song():
    global trackid, active, current_lyrics, current_timestamps
    trackid = None if not isinstance(trackid, str) else trackid
    metadata = get_metadata()
    if trackid == None or trackid != f"{metadata[1]}__{metadata[2]}":
        if metadata[0] == True:
            trackid = f"{metadata[1]}__{metadata[2]}"
            lyrics = await get_lyrics(metadata[2], metadata[1])
            current_lyrics = []
            current_timestamps = []
            try:
                for i in lyrics["lyrics"].splitlines():
                    # Transform the timestamp into a position in seconds (because playerctl only outputs the position in seconds)
                    seconds = int(i[1:3]) * 60 + int(i[4:6]) + int(i[7:9]) / 100

                    current_timestamps.append(seconds)

                    current_lyrics.append(i[11:])
            except TypeError:
                current_lyrics = None
            current_position = 0
            active = True

        else:
            current_timestamps = None
            trackid = None
            current_lyrics = None
            current_position = 0
            active = False


def get_current_lyrics():
    if active:
        if current_lyrics == None:
            return "Can't find lyrics for this song"
        pos = float(
            subprocess.run(
                ["playerctl", "position"],
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
        )

        index = bisect.bisect_right(current_timestamps, pos) - 1

        return current_lyrics[index]
    else:
        return "No song is playing"


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
