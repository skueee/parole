import argparse
import bisect
import random
import subprocess
from array import array
import re

import lrclib
from textual.app import App, ComposeResult
from textual.widgets import Label

current_lyrics: array[str] | None
current_timestamps: array[float] | None
current_infos: array | None
trackid: str | None = None
active: bool


async def get_lyrics(title, artist, album: str | None = None):
    lyrics = await lrclib.get_lyrics(title=title, artist=artist, album=album)
    if "syncedLyrics" in lyrics:
        return {"lyrics": lyrics["syncedLyrics"]}
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
    global trackid, active, current_lyrics, current_timestamps, current_infos
    trackid = None if not isinstance(trackid, str) else trackid
    metadata = get_metadata()
    if trackid == None or trackid != f"{metadata[1]}__{metadata[2]}":
        if metadata[0] == True:
            trackid = f"{metadata[1]}__{metadata[2]}"
            lyrics = await get_lyrics(metadata[2], metadata[1])
            current_lyrics = []
            current_timestamps = []

            TIMESTAMP_REGEX = re.compile(r"\[(\d{1,2}):(\d{2})(?:\.(\d{2,3}))?\]")
            try:
                for i in lyrics["lyrics"].splitlines():
                    match = TIMESTAMP_REGEX.search(i)

                    if not match:
                        current_lyrics = None
                        break

                    # Transform the timestamp into a position in seconds (because playerctl only outputs the position in seconds)
                    seconds = int(match.group(1)) * 60 + int(match.group(2)) + int(match.group(3) or 0) / 100
                    current_timestamps.append(seconds)

                    # Check if the lyric is not empty and then append it
                    lyric = TIMESTAMP_REGEX.sub("", i).strip()
                    if not lyric:
                        lyric = random.choice(["♫", "♪"])

                    current_lyrics.append(lyric)
            except (AttributeError, TypeError):
                current_lyrics = None

            active = True
            current_infos = [metadata[1], metadata[2]]

        else:
            current_timestamps = None
            current_infos = None
            trackid = None
            current_lyrics = None
            active = False


def get_current_lyrics(show_infos: bool):
    if active:
        if current_lyrics == None:
            return ["Can't find lyrics for this song"]
        pos = float(
            subprocess.run(
                ["playerctl", "position"],
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
        )

        index = bisect.bisect_right(current_timestamps, pos) - 1

        prev_line = current_lyrics[index - 1] if index > 0 else ""
        curr_line = (
            current_lyrics[index]
            if 0 <= index < len(current_lyrics)
            else (f"{current_infos[0]} - {current_infos[1]}" if show_infos else "")
        )
        next_line = current_lyrics[index + 1] if index + 1 < len(current_lyrics) else ""

        return [prev_line, curr_line, next_line]
    else:
        return ["No song is playing"]


async def get_thing_to_display(show_infos: bool):
    await check_if_new_song()
    return get_current_lyrics(show_infos)


class ParoleApp(App):
    CSS_PATH = "textual.tcss"

    def __init__(self, delay_ms: float, show_infos: bool, ansi: bool):
        super().__init__()
        self.delay_seconds = delay_ms / 1000.0
        self.show_infos = show_infos
        self.ansi_color = ansi

    def compose(self) -> ComposeResult:
        yield Label(" ", id="before-label")
        yield Label("Loading...", id="main-label")
        yield Label(" ", id="after-label")

    def on_mount(self) -> ComposeResult:
        self.set_interval(self.delay_seconds, self.update_label)

    async def update_label(self) -> None:
        main_label = self.query_one("#main-label", Label)
        before_label = self.query_one("#before-label", Label)
        after_label = self.query_one("#after-label", Label)

        lyrics = await get_thing_to_display(self.show_infos)

        if len(lyrics) == 1:
            main_label.update(lyrics[0])
            before_label.display = False
            after_label.display = False
        else:
            before_label.display = True
            after_label.display = True

            before_label.update(lyrics[0])
            main_label.update(lyrics[1])
            after_label.update(lyrics[2])


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
    parser.add_argument(
        "--no-song-infos",
        dest="show_infos",
        action="store_false",
        default=True,
        help="Don't show song infos at the start of the song",
    )
    parser.add_argument(
        "--no-ansi",
        dest="ansi",
        action="store_false",
        default=True,
        help="Don't use terminal colors",
    )

    args = parser.parse_args()
    app = ParoleApp(delay_ms=args.delay, show_infos=args.show_infos, ansi=args.ansi)
    app.run()
