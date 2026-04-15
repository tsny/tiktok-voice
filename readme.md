# TikTok Text-to-speech

Fork of [oscie57/tiktok-voice](https://github.com/oscie57/tiktok-voice).

## Setup

```
pip3 install -r requirements.txt
```

Set your TikTok session ID via environment variable or pass it with `-s`:
```
export TIKTOK_SESSION_ID=abc123def456abc123def456abc123de
```

## Usage

**From text:**
```
python3 main.py -v en_us_002 -t "Hello, world!" 
```

**From file:**
```
python3 main.py -v en_us_ghostface -f input.txt -n output.mp3
```

**Play instead of save:**
```
python3 main.py -v en_us_002 -t "Hello, world!" -p
```

## Notes

- Automatically tries multiple API endpoints and caches the working URL per session in `session-cache.json`
- Voice codes are listed in `constants.py`
- Session ID: [how to obtain](https://github.com/oscie57/tiktok-voice/wiki/Obtaining-SessionID)
