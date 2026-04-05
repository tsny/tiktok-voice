# TikTok Text-to-speech

Fork of [oscie57/tiktok-voice](https://github.com/oscie57/tiktok-voice).

## Setup

```
pip3 install -r requirements.txt
```

Create a `.env` file with your TikTok session ID:
```
session_id=YOUR_SESSION_ID
```

## Usage

**From text:**
```
python3 main.py -v VOICE -t "your text" -s SESSION_ID
```

**From file:**
```
python3 main.py -v VOICE -f input.txt -s SESSION_ID -n output.mp3
```

**Play instead of save:**
```
python3 main.py -v VOICE -t "your text" -s SESSION_ID -p
```

## Notes

- Automatically tries multiple API endpoints and caches the working URL per session in `session-cache.json`
- Voice codes are listed in `constants.py`
- Session ID: [how to obtain](https://github.com/oscie57/tiktok-voice/wiki/Obtaining-SessionID)
