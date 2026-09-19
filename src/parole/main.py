import subprocess

from textual.app import App, ComposeResult
from textual.widgets import Label


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


class MyApp(App):
    CSS_PATH = "textual.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Lorem Ipsum")


if __name__ == "__main__":
    app = MyApp()
    app.run()
