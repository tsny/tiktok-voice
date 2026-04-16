# TikTok Text-to-speech

Fork of [oscie57/tiktok-voice](https://github.com/oscie57/tiktok-voice).

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync
```

Copy `.envrc` values or export them manually:

```
export TIKTOK_SESSION_ID=abc123def456abc123def456abc123de
export TIKTOK_VOICE=en_us_002
export TIKTOK_BASE_URLS_FILE="$(pwd)/base-urls.txt"
```

Session ID: [how to obtain](https://github.com/oscie57/tiktok-voice/wiki/Obtaining-SessionID)

## Usage

**From text:**
```
uv run main.py -t "Hello, world!"
```

**From file:**
```
uv run main.py -f input.txt -n output.mp3
```

**Override voice or session inline:**
```
uv run main.py -v en_us_ghostface -t "Hello, world!" -s abc123...
```

**Play instead of save:**
```
uv run main.py -t "Hello, world!" -p
```

## Notes

- Voice defaults to `TIKTOK_VOICE` env var; override with `-v`. Codes listed in `tiktok_voice/constants.py`
- Tries all URLs in `base-urls.txt` on failure, caching the working one per session in `session-cache.json`
- Output is saved as a timestamped `.mp3` (e.g. `voice_0415_143022.mp3`) unless `-n` is specified
