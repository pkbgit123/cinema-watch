"""Alert via ntfy when a Light House Cinema film page gains booking links."""
import json, os, re, sys, urllib.request
from pathlib import Path

URL = "https://www.lighthousecinema.co.nz/schedule/film/tenzing"
FILM_TITLE = "Tenzing"  # sanity check: page really loaded, not a Cloudflare challenge
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")  # repo secret
STATE = Path(__file__).with_name("seen.json")

BOOK_RE = re.compile(r'href="(/schedule/film/Film/book/(\d+))"')


def booking_ids(html):
    return {m[1] for m in BOOK_RE.findall(html)}


def notify(msg):
    urllib.request.urlopen(urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode(),
        headers={"Title": "Bookings open!", "Priority": "urgent", "Click": URL, "Tags": "film"}), timeout=20)


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (personal booking watcher)"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    if FILM_TITLE not in html:
        sys.exit("Unexpected page content (blocked or page changed) - not treating as 'no bookings'")
    seen = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    new = booking_ids(html) - seen
    if new:
        notify(f"{len(new)} new session(s) bookable for {FILM_TITLE}. Tap to book.")
        STATE.write_text(json.dumps(sorted(seen | new)))
    print(f"{len(new)} new booking link(s)")


if __name__ == "__main__":
    main()
