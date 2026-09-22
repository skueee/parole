import argparse
import bisect
import subprocess
from array import array

import lrclib
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
            active = True

        else:
            current_timestamps = None
            trackid = None
            current_lyrics = None
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


async def get_thing_to_display():
    await check_if_new_song()
    return get_current_lyrics()


class ParoleApp(App):
    CSS_PATH = "textual.tcss"

    def __init__(self, delay_ms: float):
        super().__init__()
        self.delay_seconds = delay_ms / 1000.0

    def compose(self) -> ComposeResult:
        yield Label("Loading...", id="main-label")

    def on_mount(self) -> ComposeResult:
        self.set_interval(self.delay_seconds, self.update_label)

    async def update_label(self) -> None:
        label = self.query_one("#main-label", Label)
        label.update(await get_thing_to_display())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parole is a TUI tool to display lyrics from the song you are currently playing"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=100,
        help="Delay at which the program will update lyrics",
    )

    args = parser.parse_args()
    app = ParoleApp(delay_ms=args.delay)
    app.run()
