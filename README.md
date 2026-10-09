# parole
Parole is a TUI tool to display lyrics from the song you are currently playing !

![GitHub commit activity](https://img.shields.io/github/commit-activity/t/skueee/parole?label=total%20commits)
![GitHub Issues](https://img.shields.io/github/issues/skueee/parole)
![GitHub Repo stars](https://img.shields.io/github/stars/skueee/parole?style=flat&color=yellow)

> [!NOTE]
> While this tool is meant to be compatible with Windows, it could be more unstable due to less testing.

[![asciicast](https://asciinema.org/a/1267969.png)](https://asciinema.org/a/1267969)

#### [Download here !](https://pypi.org/project/parole-tui/)

## Quick start
**1. Dependencies**

You will need pipx or pip to run this program

**2. Download the program**
```
pipx install parole-tui
```
or if you don't have pipx
```
pip install parole-tui
```
**3. Launch the program**
```
parole
```

## Usage
Here is a list of the arguments that it can take :
```
-h, --help                Show the available arguments
--delay DELAY             Delay at which the program will update lyrics
--no-song-infos           Don't show song infos at the start of the song
--no-ansi                 Don't use terminal colors
--line-count LINE_COUNT   Number of lyrics shown before and after the current one
```

## Features
- Show lyrics in terminal
- Multiplatform - Uses MPRIS or winsdk depending on your OS
- Some customization options
- Sync lyrics with music

## Development
You can see infos on how to contribute and develop on the CONTRIBUTING.md file

## How does that works ?
The program takes the current song using two ways, depending on the OS. If it runs on Linux, it will create a LinuxMediaProvider which uses MPRIS (through dbus-next) to get infos, while on Windows it uses a WindowsMediaProvider that uses winsdk to get infos. If the song changed, it sends a request to LRCLib to get the lyrics and display them !

## Stardance
This tool was made for Stardance, a program ran by [Hack Club](https://hackclub.com/)

[My project page](https://stardance.hackclub.com/projects/63249) | [Hack Club](https://hackclub.com/) | [Stardance Program](https://stardance.hackclub.com/)

## AI Notice

AI was used to do research in this project, but the code was always rewritten and edited by an human. 

## Credit

### Libraries
- **dbus-next, to interact with MPRIS on Linux :** [pypi.org/project/dbus-next](https://pypi.org/project/dbus-next/)
- **Winsdk, to interact with Windows :** [pypi.org/project/winsdk](https://pypi.org/project/winsdk/)
- **Textual, to display the TUI :** [textual.textualize.io](https://textual.textualize.io/)

### API
- **LRCLib, to get the lyrics :** [lrclib.net](https://lrclib.net/)

### Project management
- **UV, to manage the project :** [docs.astral.sh/uv](https://docs.astral.sh/uv/)
- **uv-script, to create custom scripts (lint, format...) :** [pypi.org/project/uv-script](https://pypi.org/project/uv-script/)
- **Ruff, to lint and format :** [docs.astral.sh/ruff](https://docs.astral.sh/ruff/)
- **Deptry, to check dependencies problems :** [deptry.com](https://deptry.com/)
