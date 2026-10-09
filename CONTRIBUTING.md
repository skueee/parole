# Contributing
Thanks for taking interest in parole ! Here is a guide on how to contribute or just develop for yourself !

## Developing
**1. Download the repo**
```
git clone https://github.com/skueee/parole.git
```

**2. Dependencies**

Parole uses UV to manage the project.
Follow the [installation guide](https://docs.astral.sh/uv/getting-started/installation/) to install it.
Then sync dependencies with :
```
uv sync
```

**3. Running**

To run the app, execute :
```
uv run parole
```

**You're all set !**

## Common commands
> [!NOTE]
> Every command starting by "uv run uvs" can just be replaced by "uvs" in the venv
```
uv run uvs lint         # Lint : check for errors
uv run uvs fix          # Fix : automatically fix errors that are fixable
uv run uvs format       # Format : makes the code looks niiiice
uv run uvs deps_check   # Check if there is any problem with the dependencies
uv run parole           # Launch the app
```

## Project structure
```
src/parole/
      __init__.py    Init file
      lrclib.py      The module containing all the calls to LRCLib API
      monitor.py     The module containing all the definition for the providers (MPRIS and winsdk)
      parole.py      The main file, containing the TUI and the parsing logic
      textual.tcss   The style file
```

## Pull Requests

When doing a Pull Request, please make one pull request by feature, never add multiple features into one PR.

Please run lint and format before submitting your PR :
```
uv run uvs format        # Format
uv run uvs fix           # Lint with auto fix
uv run uvs lint          # Lint
uv run uvs deps_check    # Check issues with dependencies
```

# AI Usage

AI is authorized when used to do research, but not to write code directly.

You can try to understand a bug, research a way of doing something... using AI, but you must write yourself your implementation in the code.

Also, try to be the more transparent possible on what you're doing.

When writing an issue or a PR desription, never write it using AI, even to "improve" your English. You do not need perfect English, just undertandable one.

**Anything clearly AI made will be closed without further discussion.**