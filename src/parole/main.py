import argparse
import bisect
import random
import re
from array import array

import lrclib
import monitor
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


async def get_metadata():
    provider = monitor.get_provider()
    await provider.init()
    metadata = await provider.get_metadata()
    if metadata.artist == None and metadata.title == None and metadata.album == None:
        run = False
    else:
        run = True
    return [run, metadata.artist, metadata.title, metadata.album]


async def get_position():
    provider = monitor.get_provider()
    await provider.init()
    position = await provider.get_position()
    return position


async def check_if_new_song():
    global trackid, active, current_lyrics, current_timestamps, current_infos
    trackid = None if not isinstance(trackid, str) else trackid
    metadata = await get_metadata()
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
                    seconds = (
                        int(match.group(1)) * 60
                        + int(match.group(2))
                        + int(match.group(3) or 0) / 100
                    )
                    current_timestamps.append(seconds)

                    # Check if the lyric is not empty and then append it
                    lyric = TIMESTAMP_REGEX.sub("", i).strip()
                    if not lyric:
                        lyric = random.choice(["♫", "♪"])

                    current_lyrics.append(lyric)
            except AttributeError, TypeError:
                current_lyrics = None

            active = True
            current_infos = [metadata[1], metadata[2]]

        else:
            current_timestamps = None
            current_infos = None
            trackid = None
            current_lyrics = None
            active = False


async def get_current_lyrics(show_infos: bool, line_count: int):
    if active:
        if current_lyrics == None:
            return ["Can't find lyrics for this song"]
        pos = float(await get_position())

        index = bisect.bisect_right(current_timestamps, pos) - 1

        prev_lines = []
        for offset in range(line_count, 0, -1):
            target_idx = index - offset
            prev_lines.append(
                current_lyrics[target_idx]
                if 0 <= target_idx < len(current_lyrics)
                else ""
            )

        curr_line = (
            current_lyrics[index]
            if 0 <= index < len(current_lyrics)
            else (f"{current_infos[0]} - {current_infos[1]}" if show_infos else "")
        )

        next_lines = []
        for offset in range(1, line_count + 1):
            target_idx = index + offset
            next_lines.append(
                current_lyrics[target_idx]
                if 0 <= target_idx < len(current_lyrics)
                else ""
            )

        return [prev_lines, curr_line, next_lines]
    else:
        return ["No song is playing"]


async def get_thing_to_display(show_infos: bool, lines_count: int):
    await check_if_new_song()
    return await get_current_lyrics(show_infos, lines_count)


class ParoleApp(App):
    CSS_PATH = "textual.tcss"

    def __init__(self, delay_ms: float, show_infos: bool, ansi: bool, line_count: int):
        super().__init__()
        self.delay_seconds = delay_ms / 1000.0
        self.show_infos = show_infos
        self.ansi_color = ansi
        self.line_count = line_count

    def compose(self) -> ComposeResult:
        if self.line_count > 0:
            for i in range(self.line_count):
                yield Label(
                    " ", id=f"before-label-{i}", classes="secundary-label before-label"
                )
        yield Label("Loading...", id="main-label")
        if self.line_count > 0:
            for i in range(self.line_count):
                yield Label(
                    " ", id=f"after-label-{i}", classes="secundary-label after-label"
                )

    def on_mount(self) -> ComposeResult:
        self.set_interval(self.delay_seconds, self.update_label)

    async def update_label(self) -> None:
        main_label = self.query_one("#main-label", Label)
        before_labels = self.query(".before-label")
        after_labels = self.query(".after-label")

        lyrics = await get_thing_to_display(self.show_infos, self.line_count)
        try:
            before_lines, current_line, after_lines = lyrics
        except ValueError:
            current_line = lyrics[0]
            before_lines = []
            after_lines = []

        main_label.update(current_line)

        for label, text in zip(before_labels, before_lines):
            label.display = True
            label.update(text)

        for label, text in zip(after_labels, after_lines):
            label.display = True
            label.update(text)

        if len(before_lines) == 0:
            for label in before_labels:
                label.display = False

        if len(after_lines) == 0:
            for label in after_labels:
                label.display = False


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
    parser.add_argument(
        "--line-count",
        dest="line_count",
        default=1,
        type=int,
        help="Number of lyrics shown before and after the current one",
    )

    args = parser.parse_args()
    app = ParoleApp(
        delay_ms=args.delay,
        show_infos=args.show_infos,
        ansi=args.ansi,
        line_count=args.line_count,
    )
    app.run()
