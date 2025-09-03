from email.utils import formatdate
from pathlib import Path

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True, parents=True)

def rfc2822(ts: int) -> str:
    return formatdate(ts, usegmt=True)

def make_title(text: str | None) -> str:
    if not text:
        return "Новый пост"
    return text.strip().split("\n")[0][:100]
