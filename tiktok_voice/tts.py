import requests, base64, random, argparse, os, playsound, time, re, textwrap, json
from datetime import datetime
from .constants import voices

_BASE_URLS_FILE = os.environ.get(
    'TIKTOK_BASE_URLS_FILE',
    os.path.join(os.path.dirname(__file__), '..', 'base-urls.txt')
)
_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "tiktok-voice")
os.makedirs(_CONFIG_DIR, exist_ok=True)
_SESSION_CACHE_FILE = os.environ.get(
    "TIKTOK_SESSION_CACHE_FILE",
    os.path.join(_CONFIG_DIR, "session-cache.json")
)

def _load_base_urls():
    try:
        with open(_BASE_URLS_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(urls)} base URL(s) from {os.path.abspath(_BASE_URLS_FILE)}")
        return urls
    except FileNotFoundError:
        print(f"Base URLs file not found ({_BASE_URLS_FILE}), using built-in fallback URL")
        return ["https://api16-normal-v6.tiktokv.com/media/api/text/speech/invoke/"]

def _load_session_cache():
    try:
        with open(_SESSION_CACHE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_session_cache(cache):
    with open(_SESSION_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

BASE_URLS = _load_base_urls()
USER_AGENT = "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)"


def tts(session_id: str, text_speaker: str = "en_us_002", req_text: str = "TikTok Text To Speech",
        filename: str = 'voice.mp3', play: bool = False):
    req_text = req_text.replace("+", "plus")
    req_text = req_text.replace(" ", "+")
    req_text = req_text.replace("&", "and")
    req_text = req_text.replace("ä", "ae")
    req_text = req_text.replace("ö", "oe")
    req_text = req_text.replace("ü", "ue")
    req_text = req_text.replace("ß", "ss")

    cache = _load_session_cache()
    cached_url = cache.get(session_id)
    urls_to_try = ([cached_url] + [u for u in BASE_URLS if u != cached_url]) if cached_url else BASE_URLS

    if text_speaker not in voices:
        print(f"\033[33m\nWARN:  '{text_speaker}' is not a known voice ID\n\033[0m")

    preview = req_text[:60].replace("+", " ") + ("..." if len(req_text) > 60 else "")
    print(f"Session:  {session_id}")
    print(f"Voice:    {text_speaker}")
    print(f"Text:     {preview}")
    print(f"Output:   {filename}")
    if cached_url:
        print(f"Cache:    {cached_url}")
    else:
        print(f"Cache:    none found for this session ({_SESSION_CACHE_FILE})")
    print(f"URLs:     {len(urls_to_try)} endpoint(s) to try")
    print("")
    last_error = None
    for base_url in urls_to_try:
        print(f"Trying {base_url}")
        try:
            r = requests.post(
                f"{base_url}?text_speaker={text_speaker}&req_text={req_text}&speaker_map_type=0&aid=1233",
                headers={
                    'User-Agent': USER_AGENT,
                    'Cookie': f'sessionid={session_id}'
                }
            )
            data = r.json()
        except Exception as e:
            print(f"Request error for {base_url}: {e}")
            last_error = e
            if base_url == cached_url:
                cache.pop(session_id, None)
                _save_session_cache(cache)
                print(f"Cleared stale cached URL: {base_url}")
            continue

        msg = data.get("message", "")
        if isinstance(msg, str) and any(k in msg.lower() for k in ("session", "invalid", "unauthorized", "login")):
            print(f"[{r.status_code}] Session/auth error from {base_url}: {msg}")
            last_error = data
            if base_url == cached_url:
                cache.pop(session_id, None)
                _save_session_cache(cache)
                print(f"Cleared stale cached URL: {base_url}")
            continue

        if data.get("message") == "Couldn't load speech. Try again.":
            print(f"[{r.status_code}] Failed with {base_url}: {data.get('message') or json.dumps(data, indent=2)}")
            last_error = data
            if base_url == cached_url:
                cache.pop(session_id, None)
                _save_session_cache(cache)
                print(f"Cleared stale cached URL: {base_url}")
            continue

        if not data.get("data") or not data["data"].get("v_str"):
            print(f"[{r.status_code}] No audio data from {base_url}: {data.get('message') or json.dumps(data, indent=2)}")
            last_error = data
            if base_url == cached_url:
                cache.pop(session_id, None)
                _save_session_cache(cache)
                print(f"Cleared stale cached URL: {base_url}")
            continue

        if cache.get(session_id) != base_url:
            cache[session_id] = base_url
            _save_session_cache(cache)
            print(f"Cached working URL for session: {base_url}")

        vstr = data["data"]["v_str"]
        msg = data["message"]
        scode = data["status_code"]
        log = data["extra"]["log_id"]
        dur = data["data"]["duration"]
        spkr = data["data"]["speaker"]

        b64d = base64.b64decode(vstr)

        with open(filename, "wb") as out:
            out.write(b64d)

        print(f"Saved to: {filename}")

        output_data = {
            "status": msg.capitalize(),
            "status_code": scode,
            "duration": dur,
            "speaker": spkr,
            "log": log
        }

        print(json.dumps(output_data, indent=2))

        if play is True:
            playsound.playsound(filename)
            os.remove(filename)

        return output_data

    output_data = {"status": "Session ID is invalid", "status_code": 5, "last_error": str(last_error)}
    print(output_data)
    return output_data


def batch_create(filename: str = 'voice.mp3'):
    out = open(filename, 'wb')

    def sorted_alphanumeric(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(data, key=alphanum_key)

    for item in sorted_alphanumeric(os.listdir('./batch/')):
        filestuff = open('./batch/' + item, 'rb').read()
        out.write(filestuff)

    out.close()


def main():
    parser = argparse.ArgumentParser(description="Simple Python script to interact with the TikTok TTS API")
    parser.add_argument("-v", "--voice", help="the code of the desired voice")
    parser.add_argument("-t", "--text", help="the text to be read")
    parser.add_argument("-s", "--session", help="account session id")
    parser.add_argument("-f", "--file", help="use this if you wanna use 'text.txt'")
    parser.add_argument("-n", "--name", help="The name for the output file (.mp3)")
    parser.add_argument("-p", "--play", action='store_true', help="use this if you want to play your output")
    args = parser.parse_args()

    text_speaker = args.voice

    if args.file is not None:
        req_text = open(args.file, 'r', errors='ignore', encoding='utf-8').read()
    elif args.text is not None:
        req_text = args.text
    else:
        print('FATAL: You must provide text via -t/--text or a file via -f/--file.')
        exit(1)

    if args.play is not None:
        play = args.play

    if text_speaker is None:
        text_speaker = os.environ.get('TIKTOK_VOICE')
    if text_speaker is None:
        print('FATAL: You must provide a voice via -v/--voice or set TIKTOK_VOICE. (See README.md)')
        exit(1)

    if text_speaker == "random":
        text_speaker = randomvoice()

    if args.name is not None:
        filename = args.name
    else:
        filename = f"voice_{datetime.now().strftime('%m%d_%H%M%S')}.mp3"

    session_id = args.session or os.environ.get('TIKTOK_SESSION_ID')
    if not session_id:
        print('FATAL: You need to have a TikTok session ID! Use -s or set TIKTOK_SESSION_ID.')
        exit(1)
    if args.file is not None:
        chunk_size = 200
        textlist = textwrap.wrap(req_text, width=chunk_size, break_long_words=True, break_on_hyphens=False)

        batch_dir = './batch/'

        if not os.path.exists(batch_dir):
            os.makedirs(batch_dir)

        for i, item in enumerate(textlist):
            tts(session_id, text_speaker, item, f'{batch_dir}{i}.mp3', False)

        batch_create(filename)

        for item in os.listdir(batch_dir):
            os.remove(batch_dir + item)

        if os.path.exists:
            os.removedirs(batch_dir)

        return

    tts(session_id, text_speaker, req_text, filename, play)


def randomvoice():
    count = random.randint(0, len(voices))
    text_speaker = voices[count]

    return text_speaker


def sampler():
    for item in voices:
        text_speaker = item
        filename = item
        print(item)
        req_text = 'TikTok Text To Speech Sample'
        tts(text_speaker, req_text, filename)


if __name__ == "__main__":
    main()
